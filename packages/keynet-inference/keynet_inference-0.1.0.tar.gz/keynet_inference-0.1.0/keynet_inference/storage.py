import datetime
import os
from io import BytesIO
from typing import Optional, Union
from uuid import uuid4

import requests

from .config import check_env


class Storage:
    def __init__(self):
        check_env()
        try:
            import boto3

            self.client = boto3.client(
                "s3",
                endpoint_url=os.environ.get("MLFLOW_S3_ENDPOINT_URL"),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            )
        except ImportError:
            raise ImportError(
                "boto3 is required for S3 storage. Install it with: pip install boto3"
            )
        self.public_bucket = os.environ.get("AWS_BUCKET_NAME")

    def presign(self, key, ttl=6000) -> str:
        """
        Pre-signed URL을 생성합니다.

        Args:
            key (str): pre-signed URL을 생성할 객체의 키.
            ttl (int, optional): pre-signed URL의 TTL. Defaults to 600.

        Returns:
            str: pre-signed URL.

        """
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.public_bucket, "Key": key},
            ExpiresIn=ttl,
        )

    def get(self, url: str, save_path: Optional[str] = None) -> Union[None, BytesIO]:
        """
        Pre-signed URL을 사용하여 이미지를 다운로드합니다.

        Args:
            url (str): 다운로드할 이미지의 pre-signed URL.
            save_path (str, optional): 이미지를 저장할 로컬 경로. 지정하지 않으면 버퍼를 반환합니다.

        Returns:
            BytesIO: save_path가 제공되지 않은 경우 이미지 데이터가 담긴 버퍼를 반환합니다. 그렇지 않으면 None을 반환합니다.

        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            if save_path:
                from pathlib import Path

                with Path(save_path).open("wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return None
            else:
                buffer = BytesIO()
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        buffer.write(chunk)
                buffer.seek(0)
                return buffer

        except requests.exceptions.RequestException as e:
            print(f"다운로드 실패: {e}")
            raise e

    def put(self, buffer, content_type: str = "image/png") -> str:
        """
        이미지를 업로드하고 pre-signed URL을 반환합니다.

        Args:
            buffer (BytesIO): 업로드할 이미지 데이터.
            content_type (str, optional): 업로드할 이미지의 MIME 타입. Defaults to "image/png".

        Returns:
            str: 업로드된 이미지의 pre-signed URL.

        """
        unique_key = datetime.datetime.now().strftime("%Y%m%d") + "/" + str(uuid4())
        try:
            self.client.put_object(
                Bucket=self.public_bucket,
                Key=unique_key,
                Body=buffer,
                ContentType=content_type,
            )
        except Exception as e:
            print(f"업로드 실패: {e}")
            raise e
        return self.presign(unique_key)
