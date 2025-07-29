#!/usr/bin/env python3

# Copyright 2021-2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import ast
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

import numpy as np
import tritonclient.grpc as tritongrpcclient
from mlflow.deployments import BaseDeploymentClient
from mlflow.exceptions import MlflowException
from mlflow.models import Model
from mlflow.tracking.artifact_utils import _download_artifact_from_uri
from tritonclient.utils import InferenceServerException, np_to_triton_dtype

from .config import Config, check_env
from .model_config import InputOutput, ModelConfig

logger = logging.getLogger(__name__)

_MLFLOW_META_FILENAME = "mlflow-meta.json"


class TritonPlugin(BaseDeploymentClient):
    def __init__(self, uri: Optional[str] = None):
        """Initialize the deployment plugin, sets the triton model repo."""
        check_env()
        super(TritonPlugin, self).__init__(target_uri=uri)
        self.server_config = Config()
        triton_url, self.triton_model_repo = self._get_triton_server_config()
        # need to add other flavors
        self.supported_flavors = ["triton", "onnx"]

        if triton_url.startswith("http://"):
            triton_url = triton_url[len("http://") :]
            ssl = False
        elif triton_url.startswith("https://"):
            triton_url = triton_url[len("https://") :]
            ssl = True
        else:
            raise ValueError(
                f"Triton URL must start with http:// or https://. Got: {triton_url}"
            )
        print(f"Triton URL: {triton_url}, ssl: {ssl}")

        try:
            self.triton_client = tritongrpcclient.InferenceServerClient(
                url=triton_url,
                ssl=ssl,
                # verbose=True,
                # concurrency=5,        # in http
                # network_timeout=90,   # in http
            )
        except Exception as e:
            (f"Failed to connect to Triton server at {triton_url}. Error: {e}")

    def get_config(self, model_name):
        model_data = self.triton_client.get_model_metadata(
            model_name=model_name, as_json=True
        )
        return ModelConfig(
            name=model_data["name"],
            versions=model_data["versions"],
            platform=model_data["platform"],
            ready=self.triton_client.is_model_ready(model_name=model_name),
            inputs=[InputOutput(**inp) for inp in model_data["inputs"]],
            outputs=[InputOutput(**out) for out in model_data["outputs"]],
        )

    def init(self, name, model_uri, flavor="onnx", config=None):
        self._validate_flavor(flavor)

        # Verify model does not already exist in Triton
        if self._model_exists(name):
            raise Exception(
                f"Unable to create deployment for name {name} because it already exists."
            )

        # Get the path of the artifact
        path = Path(_download_artifact_from_uri(model_uri))

        print("Copy files to Triton repo...")
        self._copy_files_to_triton_repo(path, name, flavor)

        print("Generate mlflow meta file...")
        self._generate_mlflow_meta_file(name, flavor, model_uri)

        return name, flavor

    def create_deployment(self, name, model_uri, flavor="onnx", config=None):
        """
        Deploy the model at the model_uri to the Triton model repo.

        Associated config.pbtxt and *labels* files will be deployed.

        :param name: Name of the of the model
        :param model_uri: Model uri in format model:/<model-name>/<version-or-stage>
        :param flavor: Flavor of the deployed model
        :param config: Configuration parameters

        :return: Model flavor and name
        """
        self._validate_flavor(flavor)

        # Verify model does not already exist in Triton
        if self._model_exists(name):
            raise Exception(
                f"Unable to create deployment for name {name} because it already exists."
            )

        # Get the path of the artifact
        path = Path(_download_artifact_from_uri(model_uri))

        print("Copy files to Triton repo...")
        self._copy_files_to_triton_repo(path, name, flavor)

        print("Generate mlflow meta file...")
        self._generate_mlflow_meta_file(name, flavor, model_uri)

        try:
            print("Start load model to Triton...")
            self.triton_client.load_model(model_name=name)
            print("Model loaded to Triton")
        except InferenceServerException as ex:
            (str(ex))

        return name, flavor

    def delete_deployment(self, name):
        """
        Delete the deployed model in Triton with the provided model name.

        :param name: Name of the of the model with version number. For ex: "densenet_onnx/2"

        :return: None
        """
        # Verify model is already deployed to Triton
        if not self._model_exists(name):
            raise Exception(
                f"Unable to delete deployment for name {name} because it does not exist."
            )

        try:
            self.triton_client.unload_model(name)
        except InferenceServerException as ex:
            (str(ex))

        self._delete_deployment_files(name)

        return None

    def update_deployment(self, name, model_uri=None, flavor=None, config=None):
        """
        Update the model deployment in triton with the provided name.

        :param name: Name and version number of the model, <model_name>/<version>.
        :param model_uri: Model uri models:/model_name/version
        :param flavor: The flavor of the model
        :param config: Configuration parameters

        :return: Returns the flavor of the model
        """
        # TODO: Update this function with a warning. If config and label files associated with this
        # updated model are different than the ones already deployed to triton, issue a warning to the user.
        self._validate_flavor(flavor)

        # Verify model is already deployed to Triton
        if not self._model_exists(name):
            raise Exception(
                f"Unable to update deployment for name {name} because it does not exist."
            )

        self.get_deployment(name)

        # Get the path of the artifact
        path = Path(_download_artifact_from_uri(model_uri))

        self._copy_files_to_triton_repo(path, name, flavor)

        self._generate_mlflow_meta_file(name, flavor, model_uri)

        try:
            self.triton_client.load_model(name)
        except InferenceServerException as ex:
            (str(ex))

        return {"flavor": flavor}

    def list_deployments(self):
        """
        List models deployed to Triton.

        :return: None
        """
        resp = self.triton_client.get_model_repository_index(as_json=True)
        actives = []

        if not resp:
            return []

        for d in resp["models"]:
            if "state" in d and d["state"] == "READY":
                mlflow_meta_path = (
                    Path(self.triton_model_repo) / d["name"] / _MLFLOW_META_FILENAME
                )
                if "s3" in self.server_config:
                    meta_dict = ast.literal_eval(
                        self.server_config["s3"]
                        .get_object(
                            Bucket=self.server_config["s3_bucket"],
                            Key=str(
                                Path(self.server_config["s3_prefix"])
                                / d["name"]
                                / _MLFLOW_META_FILENAME
                            ),
                        )["Body"]
                        .read()
                        .decode("utf-8")
                    )
                elif mlflow_meta_path.is_file():
                    meta_dict = self._get_mlflow_meta_dict(d["name"])
                else:
                    continue

                d["triton_model_path"] = meta_dict["triton_model_path"]
                d["mlflow_model_uri"] = meta_dict["mlflow_model_uri"]
                d["flavor"] = meta_dict["flavor"]
                actives.append(d)

        return actives

    def get_deployment(self, name):
        r"""
        Get deployment from Triton.

        :param name: Name of the model. \n
                     Ex: "mini_bert_onnx" - gets the details of active version of this model \n

        :return: output - Returns a dict with model info
        """
        deployments = self.list_deployments()
        for d in deployments:
            if d["name"] == name:
                return d
        raise ValueError(f"Unable to get deployment with name {name}")

    def load(self, model_name: str):
        try:
            print(f"Start load {model_name} model to Triton...")
            self.triton_client.load_model(model_name=model_name)
            print(f"Model {model_name} loaded to Triton")
        except InferenceServerException as ex:
            print(f"Failed to load model {model_name}")
            raise MlflowException(str(ex))

    def unload(self, model_name: str):
        try:
            print(f"Start unload {model_name} model from Triton...")
            self.triton_client.unload_model(model_name=model_name)
            print(f"Model {model_name} unloaded from Triton")
        except InferenceServerException as ex:
            print(f"Failed to unload model {model_name}")
            raise MlflowException(str(ex))

    def predict(self, model_name: str, df):  # type: ignore[override]
        single_input_np = None
        if isinstance(df, np.ndarray):
            single_input_np = df

        inputs = []
        if single_input_np is not None:
            raise MlflowException("Unnamed input is not currently supported")
        else:
            for key, val in df.items():
                inputs.append(
                    tritongrpcclient.InferInput(
                        key, val.shape, np_to_triton_dtype(val.dtype)
                    )
                )
                inputs[-1].set_data_from_numpy(val)

        try:
            resp = self.triton_client.infer(model_name=model_name, inputs=inputs)
            outputs = resp.get_response(as_json=True)["outputs"]
            res = {}
            for output in outputs:
                res[output["name"]] = resp.as_numpy(output["name"])
            return res
        except InferenceServerException as ex:
            raise MlflowException(str(ex))

    def _get_triton_server_config(self):
        triton_url = self.server_config["triton_url"]
        logger.info(f"Triton url = {triton_url}")

        triton_model_repo = self.server_config["triton_model_repo"]
        logger.info(f"Triton model repo = {triton_model_repo}")

        return triton_url, triton_model_repo

    def _generate_mlflow_meta_file(self, name, flavor, model_uri):
        triton_deployment_dir = Path(self.triton_model_repo) / name
        meta_dict = {
            "name": name,
            "triton_model_path": str(triton_deployment_dir),
            "mlflow_model_uri": model_uri,
            "flavor": flavor,
        }

        if "s3" in self.server_config:
            self.server_config["s3"].put_object(
                Body=json.dumps(meta_dict, indent=4).encode("utf-8"),
                Bucket=self.server_config["s3_bucket"],
                Key=str(
                    Path(self.server_config["s3_prefix"]) / name / _MLFLOW_META_FILENAME
                ),
            )
        else:
            with (triton_deployment_dir / _MLFLOW_META_FILENAME).open("w") as outfile:
                json.dump(meta_dict, outfile, indent=4)

        print("Saved", _MLFLOW_META_FILENAME, "to", triton_deployment_dir)

    def _get_mlflow_meta_dict(self, name):
        mlflow_meta_path = Path(self.triton_model_repo) / name / _MLFLOW_META_FILENAME

        if "s3" in self.server_config:
            mlflow_meta_dict = ast.literal_eval(
                self.server_config["s3"]
                .get_object(
                    Bucket=self.server_config["s3_bucket"],
                    Key=str(
                        Path(self.server_config["s3_prefix"])
                        / name
                        / _MLFLOW_META_FILENAME
                    ),
                )["Body"]
                .read()
                .decode("utf-8")
            )
        else:
            with mlflow_meta_path.open() as metafile:
                mlflow_meta_dict = json.load(metafile)

        return mlflow_meta_dict

    def _get_copy_paths(
        self, artifact_path: Path, name: str, flavor: str
    ) -> dict[str, dict[str, str]]:
        copy_paths: dict[str, dict[str, str]] = {}
        copy_paths["model_path"] = {}
        triton_deployment_dir = Path(self.triton_model_repo) / name
        if flavor == "triton":
            # When flavor is 'triton', the model is assumed to be preconfigured
            # with proper model versions and version strategy, which may differ from
            # the versioning in MLFlow
            for file in artifact_path.iterdir():
                if file.is_dir():
                    copy_paths["model_path"]["from"] = str(file)
                    break
            copy_paths["model_path"]["to"] = str(triton_deployment_dir)
        elif flavor == "onnx":
            # Look for model file via MLModel metadata or iterating dir
            model_file = None
            config_file = None
            for file in artifact_path.iterdir():
                if file.name == "MLmodel":
                    mlmodel = Model.load(file)
                    onnx_meta_data = mlmodel.flavors.get("onnx", None)
                    if onnx_meta_data is not None:
                        model_file = onnx_meta_data.get("data", None)
                elif file.name == "config.pbtxt":
                    config_file = file.name
                    copy_paths["config_path"] = {}
                elif file.suffix == ".txt" and file.stem != "requirements":
                    copy_paths[file.stem] = {
                        "from": str(file),
                        "to": str(triton_deployment_dir),
                    }
            if model_file is None:
                for file in artifact_path.iterdir():
                    if file.suffix == ".onnx":
                        model_file = file.name
                        break
            # copy_paths["model_path"]["from"] = str(artifact_path / model_file)
            # copy_paths["model_path"]["to"] = str(triton_deployment_dir / "1")

            if config_file is not None:
                copy_paths["config_path"]["from"] = str(artifact_path / config_file)
                copy_paths["config_path"]["to"] = str(triton_deployment_dir)
            else:
                # Generate a more complete config file with ONNX metadata
                config = self._generate_onnx_config(
                    model_name=name,
                    model_file=model_file,
                    model_path=artifact_path / model_file,
                )

                # Create a temporary config.pbtxt file in the artifact directory
                temp_config_path = artifact_path / "config.pbtxt"
                with temp_config_path.open("w") as cfile:
                    cfile.write(config)

                # Add the generated config to copy_paths so it gets uploaded to S3/copied locally
                copy_paths["config_path"] = {
                    "from": str(temp_config_path),
                    "to": str(triton_deployment_dir),
                }
        return copy_paths

    def _walk(self, path):
        """
        Walk a path like os.walk() if path is dir, return file in the expected format otherwise.

        :param path: dir or file path
        :return: root, dirs, files
        """
        path_obj = Path(path)
        if path_obj.is_file():
            return [(str(path_obj.parent), [], [path_obj.name])]
        elif path_obj.is_dir():
            return list(os.walk(path))
        else:
            raise Exception(f"path: {path} is not a valid path to a file or dir.")

    def _copy_files_to_triton_repo(self, artifact_path, name, flavor):
        copy_paths = self._get_copy_paths(artifact_path, name, flavor)
        print(copy_paths)
        for key in copy_paths:
            if "s3" in self.server_config:
                # copy model dir to s3 recursively
                for root, dirs, files in self._walk(copy_paths[key]["from"]):
                    for filename in files:
                        local_path = str(Path(root) / filename)

                        if flavor == "onnx":
                            s3_path = str(
                                Path(self.server_config["s3_prefix"])
                                / Path(copy_paths[key]["to"]).relative_to(
                                    self.server_config["triton_model_repo"]
                                )
                                / filename
                            )

                        elif flavor == "triton":
                            rel_path = Path(local_path).relative_to(
                                copy_paths[key]["from"]
                            )
                            s3_path = str(
                                Path(self.server_config["s3_prefix"]) / name / rel_path
                            )

                        self.server_config["s3"].upload_file(
                            local_path,
                            self.server_config["s3_bucket"],
                            # "model.onnx",
                            s3_path,
                        )
            else:
                from_path = Path(copy_paths[key]["from"])
                to_path = Path(copy_paths[key]["to"])
                if from_path.is_dir():
                    if to_path.is_dir():
                        shutil.rmtree(to_path)
                    shutil.copytree(from_path, to_path)
                else:
                    if not to_path.is_dir():
                        to_path.mkdir(parents=True, exist_ok=True)
                    shutil.copy(from_path, to_path)

        if "s3" not in self.server_config:
            triton_deployment_dir = Path(self.triton_model_repo) / name
            version_folder = triton_deployment_dir / "1"
            version_folder.mkdir(parents=True, exist_ok=True)

        return copy_paths

    def _delete_mlflow_meta(self, filepath):
        if "s3" in self.server_config:
            self.server_config["s3"].delete_object(
                Bucket=self.server_config["s3_bucket"],
                Key=filepath,
            )
        elif Path(filepath).is_file():
            Path(filepath).unlink()

    def _delete_deployment_files(self, name):
        triton_deployment_dir = Path(self.triton_model_repo) / name

        if "s3" in self.server_config:
            objs = self.server_config["s3"].list_objects(
                Bucket=self.server_config["s3_bucket"],
                Prefix=str(Path(self.server_config["s3_prefix"]) / name),
            )

            for key in objs["Contents"]:
                key = key["Key"]
                try:
                    self.server_config["s3"].delete_object(
                        Bucket=self.server_config["s3_bucket"],
                        Key=key,
                    )
                except Exception as e:
                    raise Exception(f"Could not delete {key}: {e}")

        else:
            # Check if the deployment directory exists
            if not triton_deployment_dir.is_dir():
                raise Exception(
                    f"A deployment does not exist for this model in directory "
                    f"{triton_deployment_dir} for model name {name}"
                )

            model_files = list(triton_deployment_dir.glob("model*"))
            for file in model_files:
                print(f"Model directory found: {file}")
                file.unlink()
                print(f"Model directory removed: {file}")

    def _validate_config_args(self, config):
        if not config["version"]:
            raise Exception("Please provide the version as a config argument")
        if not config["version"].isdigit():
            raise ValueError(
                f"Please make sure version is a number. version = {config['version']}"
            )

    def _validate_flavor(self, flavor):
        if flavor not in self.supported_flavors:
            raise Exception(f"{flavor} model flavor not supported by Triton")

    def _model_exists(self, name):
        deploys = self.list_deployments()
        exists = False
        for d in deploys:
            if d["name"] == name:
                exists = True
        return exists

    def _generate_onnx_config(self, model_name, model_file, model_path):
        """Generate a more complete config.pbtxt with ONNX model metadata."""
        try:
            import onnx

            # Load ONNX model to extract metadata
            model = onnx.load(str(model_path))

            # Extract input information
            inputs = []
            for input_tensor in model.graph.input:
                # Skip if it's an initializer (weight)
                if input_tensor.name not in [
                    init.name for init in model.graph.initializer
                ]:
                    tensor_type = input_tensor.type.tensor_type
                    elem_type = tensor_type.elem_type

                    # Convert ONNX data type to Triton data type
                    data_type = self._onnx_to_triton_dtype(elem_type)

                    # Extract dimensions
                    dims = []
                    for dim in tensor_type.shape.dim:
                        if dim.dim_value:
                            dims.append(dim.dim_value)
                        else:
                            dims.append(-1)  # Dynamic dimension

                    inputs.append(
                        {
                            "name": input_tensor.name,
                            "data_type": data_type,
                            "dims": dims,
                        }
                    )

            # Extract output information
            outputs = []
            for output_tensor in model.graph.output:
                tensor_type = output_tensor.type.tensor_type
                elem_type = tensor_type.elem_type

                # Convert ONNX data type to Triton data type
                data_type = self._onnx_to_triton_dtype(elem_type)

                # Extract dimensions
                dims = []
                for dim in tensor_type.shape.dim:
                    if dim.dim_value:
                        dims.append(dim.dim_value)
                    else:
                        dims.append(-1)  # Dynamic dimension

                outputs.append(
                    {"name": output_tensor.name, "data_type": data_type, "dims": dims}
                )

            # Generate config content
            config_lines = [
                f'name: "{model_name}"',
                'backend: "onnxruntime"',
                f'default_model_filename: "{model_file}"',
                "max_batch_size: 1",
                "",
            ]

            # Add inputs
            if inputs:
                config_lines.append("input [")
                for inp in inputs:
                    config_lines.append("  {")
                    config_lines.append(f'    name: "{inp["name"]}"')
                    config_lines.append(f'    data_type: {inp["data_type"]}')
                    config_lines.append(f'    dims: {inp["dims"]}')
                    config_lines.append("  }")
                config_lines.append("]")
                config_lines.append("")

            # Add outputs
            if outputs:
                config_lines.append("output [")
                for out in outputs:
                    config_lines.append("  {")
                    config_lines.append(f'    name: "{out["name"]}"')
                    config_lines.append(f'    data_type: {out["data_type"]}')
                    config_lines.append(f'    dims: {out["dims"]}')
                    config_lines.append("  }")
                config_lines.append("]")

            return "\n".join(config_lines)

        except ImportError:
            logger.warning("ONNX package not available, generating minimal config")
            return self._generate_minimal_config(model_name, model_file)
        except Exception as e:
            logger.warning(
                f"Failed to extract ONNX metadata: {e}, generating minimal config"
            )
            return self._generate_minimal_config(model_name, model_file)

    def _onnx_to_triton_dtype(self, onnx_dtype):
        """Convert ONNX data type to Triton data type."""
        dtype_map = {
            1: "TYPE_FP32",  # FLOAT
            2: "TYPE_UINT8",  # UINT8
            3: "TYPE_INT8",  # INT8
            4: "TYPE_UINT16",  # UINT16
            5: "TYPE_INT16",  # INT16
            6: "TYPE_INT32",  # INT32
            7: "TYPE_INT64",  # INT64
            8: "TYPE_STRING",  # STRING
            9: "TYPE_BOOL",  # BOOL
            10: "TYPE_FP16",  # FLOAT16
            11: "TYPE_FP64",  # DOUBLE
            12: "TYPE_UINT32",  # UINT32
            13: "TYPE_UINT64",  # UINT64
        }
        return dtype_map.get(onnx_dtype, "TYPE_FP32")

    def _generate_minimal_config(self, model_name, model_file):
        """Generate minimal config when ONNX metadata extraction fails."""
        return f"""name: "{model_name}"
backend: "onnxruntime"
default_model_filename: "{model_file}"
"""
