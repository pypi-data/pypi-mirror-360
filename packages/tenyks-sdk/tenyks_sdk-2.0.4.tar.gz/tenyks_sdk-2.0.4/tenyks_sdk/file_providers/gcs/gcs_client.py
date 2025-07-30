from datetime import timedelta
from io import BytesIO
from typing import List

from google.api_core import retry
from google.api_core.page_iterator import HTTPIterator
from google.cloud.storage import Blob, Client

retry_wrapper = retry.Retry(predicate=retry.if_transient_error)


class GCSClient:
    def __init__(self, client: Client) -> None:
        self.client = client

    @retry_wrapper
    def generate_url(
        self, bucket: str, bucket_internal_path: str, expiration_seconds: int
    ) -> str:
        blob = self.get_blob(bucket, bucket_internal_path)
        generated_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration_seconds),
            method="GET",
        )

        return generated_url

    def get_blob(self, bucket: str, bucket_internal_path: str) -> Blob:
        blob = self.client.bucket(bucket).get_blob(bucket_internal_path)
        return blob

    def list_blobs(self, bucket: str, prefix: str) -> HTTPIterator:
        blobs = self.client.list_blobs(bucket_or_name=bucket, prefix=prefix)
        return blobs

    def list_files(self, bucket: str, prefix: str) -> List[str]:
        blobs = self.list_blobs(bucket=bucket, prefix=prefix)
        file_paths_only = [blob.name for blob in blobs if not blob.name.endswith("/")]

        return file_paths_only

    def does_file_exist(self, bucket: str, bucket_internal_path: str) -> bool:
        matching_result = self.get_blob(bucket, bucket_internal_path)
        if matching_result is None:
            return False
        exists = matching_result.exists()

        return exists

    @retry_wrapper
    def save_file(self, bucket: str, bucket_internal_path: str, file: BytesIO):
        new_blob = self.client.bucket(bucket).blob(bucket_internal_path)
        new_blob.upload_from_file(file)

    @retry_wrapper
    def delete_file(self, bucket: str, bucket_internal_path: str):
        blob_to_delete = self.client.bucket(bucket).blob(bucket_internal_path)
        blob_to_delete.delete()

    @retry_wrapper
    def delete_by_prefix(self, bucket: str, prefix: str):
        blobs = self.client.list_blobs(bucket_or_name=bucket, prefix=prefix)
        for blob in blobs:
            blob.delete()
