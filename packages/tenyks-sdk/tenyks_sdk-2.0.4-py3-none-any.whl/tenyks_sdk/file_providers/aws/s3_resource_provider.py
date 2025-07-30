import os
from typing import List

from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.aws.s3_client import S3Client
from tenyks_sdk.file_providers.aws.s3_url_parser import S3Url
from tenyks_sdk.file_providers.config import S3_PRESIGNED_URL_EXPIRATION
from tenyks_sdk.file_providers.file_resource_provider import FileResourceProvider


class S3ResourceProvider(FileResourceProvider):
    def __init__(self, s3_url: str, s3_client: S3Client) -> None:
        self.s3_client: S3Client = s3_client
        self.s3_url: S3Url = s3_url
        self.s3_presigned_url_expiration = S3_PRESIGNED_URL_EXPIRATION

    def get_file(self, relative_path: str) -> FileStorage:
        path_in_bucket = os.path.join(self.s3_url.path, relative_path)
        file_object = self.s3_client.get_object(self.s3_url.bucket, path_in_bucket)

        file_stream = file_object["Body"]
        file_storage = FileStorage(
            file_stream, filename=os.path.basename(relative_path)
        )

        return file_storage

    def save_file(self, file_storage: FileStorage, relative_path: str) -> None:
        file_storage.stream.seek(0)

        path_in_bucket = os.path.join(self.s3_url.path, relative_path)

        self.s3_client.upload_fileobj(
            file_storage.stream, self.s3_url.bucket, path_in_bucket
        )

    def list_files_relative_paths(self, relative_path: str = "") -> List[str]:
        path_in_bucket = os.path.join(self.s3_url.path, relative_path)
        content = self.s3_client.list_objects_v2(self.s3_url.bucket, path_in_bucket)
        filenames = [
            item["Key"].replace(os.path.join(self.s3_url.path), "") for item in content
        ]

        return filenames

    def get_url(self, relative_path: str = "") -> str:
        path_in_bucket = os.path.join(self.s3_url.path, relative_path)
        url = self.s3_client.generate_presigned_url(
            self.s3_url.bucket,
            path_in_bucket,
            self.s3_presigned_url_expiration,
        )

        return url
