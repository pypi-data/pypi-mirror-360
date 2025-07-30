from io import BytesIO
from typing import Any, Dict, List, Optional

from botocore.client import BaseClient


class S3Client:
    def __init__(self, boto3_s3_client: BaseClient) -> None:
        self.boto3_s3_client = boto3_s3_client

    def list_objects_v2(self, s3_bucket: str, prefix: str) -> list:
        paginator = self.boto3_s3_client.get_paginator("list_objects_v2")

        pages = paginator.paginate(Bucket=s3_bucket, Prefix=prefix)

        result = []

        for page in pages:
            result.extend(page.get("Contents", []))

        return result

    def get_object(self, s3_bucket: str, s3_key: str) -> object:
        return self.boto3_s3_client.get_object(Bucket=s3_bucket, Key=s3_key)

    def head_object(self, s3_bucket: str, s3_key: str) -> object:
        return self.boto3_s3_client.head_object(Bucket=s3_bucket, Key=s3_key)

    def generate_presigned_url(
        self,
        s3_bucket: str,
        s3_key: str,
        expires_in: int,
    ):
        return self.boto3_s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": s3_bucket,
                "Key": s3_key,
            },
            ExpiresIn=expires_in,
        )

    def generate_presigned_post(
        self,
        s3_bucket: str,
        s3_key: str,
        expires_in: int,
        conditions: Optional[list] = [],
    ):
        return self.boto3_s3_client.generate_presigned_post(
            Bucket=s3_bucket, Key=s3_key, Conditions=conditions, ExpiresIn=expires_in
        )

    def upload_fileobj(
        self,
        file_stream: BytesIO,
        s3_bucket: str,
        s3_key: str,
    ):
        return self.boto3_s3_client.upload_fileobj(
            file_stream,
            Bucket=s3_bucket,
            Key=s3_key,
        )

    def delete_objects(self, s3_bucket: str, objects_to_delete: List[Dict[str, Any]]):
        objects_to_delete_chunks = self.__chunk_array(objects_to_delete, 1000)

        for objects_to_delete_chunk in objects_to_delete_chunks:
            self.boto3_s3_client.delete_objects(
                Bucket=s3_bucket, Delete={"Objects": objects_to_delete_chunk}
            )

    def __chunk_array(self, arr, chunk_size):
        return [arr[i : i + chunk_size] for i in range(0, len(arr), chunk_size)]
