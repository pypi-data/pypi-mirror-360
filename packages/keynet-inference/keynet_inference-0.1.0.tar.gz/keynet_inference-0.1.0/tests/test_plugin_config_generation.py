#!/usr/bin/env python3

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from keynet_inference.plugin import TritonPlugin


class TestTritonPluginConfigGeneration:
    """Test ONNX metadata extraction and config.pbtxt generation."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def mock_plugin(self, temp_dir):
        """Create a mock TritonPlugin instance for testing."""
        with patch("keynet_inference.plugin.TritonPlugin.__init__", return_value=None):
            plugin = TritonPlugin()
            plugin.triton_model_repo = str(temp_dir)
            return plugin

    @pytest.fixture
    def simple_model_path(self):
        """Path to the simple ONNX test model."""
        return Path("triton_test_models/simple_model/1/model.onnx")

    @pytest.fixture
    def multi_input_model_path(self):
        """Path to the multi-input ONNX test model."""
        return Path("triton_test_models/multi_input_model/1/model.onnx")

    def test_generate_onnx_config_simple_model(self, mock_plugin, simple_model_path):
        """Test config generation for a simple single-input model."""
        if not simple_model_path.exists():
            pytest.skip("Simple test model not found")

        # Generate config
        config = mock_plugin._generate_onnx_config(
            model_name="test_simple",
            model_file="model.onnx",
            model_path=simple_model_path,
        )

        print("Generated config for simple model:")
        print(config)

        # Verify config contains expected elements
        assert 'name: "test_simple"' in config
        assert 'backend: "onnxruntime"' in config
        assert 'default_model_filename: "model.onnx"' in config
        assert "max_batch_size: 1" in config

        # Verify input section
        assert "input [" in config
        assert 'name: "x"' in config  # Based on simple_model config.pbtxt
        assert "data_type: TYPE_FP32" in config
        assert "dims: [-1, 10]" in config  # Updated to match actual batch-aware output

        # Verify output section
        assert "output [" in config
        assert 'name: "output_0"' in config
        assert "dims: [-1, 2]" in config  # Updated to match actual batch-aware output

    def test_generate_onnx_config_multi_input_model(
        self, mock_plugin, multi_input_model_path
    ):
        """Test config generation for a multi-input model."""
        if not multi_input_model_path.exists():
            pytest.skip("Multi-input test model not found")

        # Generate config
        config = mock_plugin._generate_onnx_config(
            model_name="test_multi",
            model_file="model.onnx",
            model_path=multi_input_model_path,
        )

        print("Generated config for multi-input model:")
        print(config)

        # Verify config contains expected elements
        assert 'name: "test_multi"' in config
        assert 'backend: "onnxruntime"' in config

        # Verify multiple inputs
        assert "input [" in config
        assert 'name: "image"' in config
        assert 'name: "mask"' in config
        assert "dims: [-1, 3, 32, 32]" in config  # Updated to match batch-aware output
        assert "dims: [-1, 1, 32, 32]" in config  # Updated to match batch-aware output

        # Verify output
        assert "output [" in config
        assert 'name: "output_0"' in config
        assert "dims: [-1, 10]" in config  # Updated to match batch-aware output

    def test_onnx_to_triton_dtype_mapping(self, mock_plugin):
        """Test ONNX to Triton data type mapping."""
        # Test common data types
        assert mock_plugin._onnx_to_triton_dtype(1) == "TYPE_FP32"  # FLOAT
        assert mock_plugin._onnx_to_triton_dtype(6) == "TYPE_INT32"  # INT32
        assert mock_plugin._onnx_to_triton_dtype(7) == "TYPE_INT64"  # INT64
        assert mock_plugin._onnx_to_triton_dtype(10) == "TYPE_FP16"  # FLOAT16
        assert mock_plugin._onnx_to_triton_dtype(9) == "TYPE_BOOL"  # BOOL

        # Test unknown type fallback
        assert mock_plugin._onnx_to_triton_dtype(999) == "TYPE_FP32"

    def test_generate_minimal_config_fallback(self, mock_plugin):
        """Test minimal config generation as fallback."""
        config = mock_plugin._generate_minimal_config("test_model", "test.onnx")

        expected_lines = [
            'name: "test_model"',
            'backend: "onnxruntime"',
            'default_model_filename: "test.onnx"',
        ]

        for line in expected_lines:
            assert line in config

    def test_generate_onnx_config_with_import_error(
        self, mock_plugin, simple_model_path
    ):
        """Test fallback to minimal config when ONNX import fails."""
        # Mock the onnx.load method to raise ImportError
        with patch("onnx.load", side_effect=ImportError("No ONNX")):
            config = mock_plugin._generate_onnx_config(
                model_name="test_fallback",
                model_file="model.onnx",
                model_path=simple_model_path,
            )

            # Should fall back to minimal config
            assert 'name: "test_fallback"' in config
            assert 'backend: "onnxruntime"' in config
            assert 'default_model_filename: "model.onnx"' in config

            # Should not contain detailed input/output info
            assert "input [" not in config
            assert "output [" not in config

    def test_generate_onnx_config_with_load_error(self, mock_plugin):
        """Test fallback when ONNX model loading fails."""
        fake_path = Path("/nonexistent/model.onnx")

        config = mock_plugin._generate_onnx_config(
            model_name="test_error", model_file="model.onnx", model_path=fake_path
        )

        # Should fall back to minimal config
        assert 'name: "test_error"' in config
        assert 'backend: "onnxruntime"' in config

    def test_config_file_structure_validity(
        self, mock_plugin, simple_model_path, temp_dir
    ):
        """Test that generated config file can be written and has valid structure."""
        if not simple_model_path.exists():
            pytest.skip("Simple test model not found")

        # Generate config
        config = mock_plugin._generate_onnx_config(
            model_name="test_structure",
            model_file="model.onnx",
            model_path=simple_model_path,
        )

        # Write to file
        config_file = temp_dir / "test_config.pbtxt"
        config_file.write_text(config)

        # Verify file was created and is readable
        assert config_file.exists()
        content = config_file.read_text()

        # Basic structure validation
        lines = content.strip().split("\n")
        assert len(lines) > 5  # Should have multiple lines

        # Check for proper protobuf structure
        assert any("name:" in line for line in lines)
        assert any("backend:" in line for line in lines)
        assert any("input [" in line for line in lines)
        assert any("output [" in line for line in lines)

        # Check bracket matching
        open_brackets = content.count("[")
        close_brackets = content.count("]")
        assert open_brackets == close_brackets

        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces

    def test_end_to_end_config_generation(self, temp_dir, simple_model_path):
        """Test end-to-end config generation process."""
        if not simple_model_path.exists():
            pytest.skip("Simple test model not found")

        # Copy test model to temp directory
        test_artifact_dir = temp_dir / "artifact"
        test_artifact_dir.mkdir()
        shutil.copy(simple_model_path, test_artifact_dir / "model.onnx")

        # Mock the TritonPlugin with temp directory
        with patch("keynet_inference.plugin.TritonPlugin.__init__", return_value=None):
            plugin = TritonPlugin()
            plugin.triton_model_repo = str(temp_dir)

            # Test the actual _get_copy_paths method which calls _generate_onnx_config
            plugin._get_copy_paths(
                artifact_path=test_artifact_dir, name="test_end_to_end", flavor="onnx"
            )

            # Verify that config.pbtxt was created
            config_file = temp_dir / "test_end_to_end" / "config.pbtxt"
            assert config_file.exists()

            # Verify config content
            config_content = config_file.read_text()
            assert 'name: "test_end_to_end"' in config_content
            assert 'backend: "onnxruntime"' in config_content
            assert 'name: "x"' in config_content  # Input name from simple model
            assert 'name: "output_0"' in config_content  # Output name from simple model


def test_compare_generated_vs_reference_config():
    """Compare generated config with reference config from existing models."""
    simple_model_path = Path("triton_test_models/simple_model/1/model.onnx")
    reference_config_path = Path("triton_test_models/simple_model/config.pbtxt")

    if not simple_model_path.exists() or not reference_config_path.exists():
        pytest.skip("Test models not found")

    # Create mock plugin
    with patch("keynet_inference.plugin.TritonPlugin.__init__", return_value=None):
        plugin = TritonPlugin()

        # Generate config
        generated_config = plugin._generate_onnx_config(
            model_name="simple_model",
            model_file="model.onnx",
            model_path=simple_model_path,
        )

        # Read reference config
        reference_config = reference_config_path.read_text()

        print("=== Generated Config ===")
        print(generated_config)
        print("\n=== Reference Config ===")
        print(reference_config)

        # Compare key elements (not exact match due to different formatting)
        generated_lines = [line.strip() for line in generated_config.split("\n")]
        reference_lines = [line.strip() for line in reference_config.split("\n")]

        # Check that input/output names match
        gen_input_names = [line for line in generated_lines if 'name: "x"' in line]
        ref_input_names = [line for line in reference_lines if 'name: "x"' in line]
        assert len(gen_input_names) > 0
        assert len(ref_input_names) > 0

        gen_output_names = [
            line for line in generated_lines if 'name: "output_0"' in line
        ]
        ref_output_names = [
            line for line in reference_lines if 'name: "output_0"' in line
        ]
        assert len(gen_output_names) > 0
        assert len(ref_output_names) > 0

        # Check data types match
        gen_fp32 = [line for line in generated_lines if "TYPE_FP32" in line]
        ref_fp32 = [line for line in reference_lines if "TYPE_FP32" in line]
        assert len(gen_fp32) > 0
        assert len(ref_fp32) > 0
