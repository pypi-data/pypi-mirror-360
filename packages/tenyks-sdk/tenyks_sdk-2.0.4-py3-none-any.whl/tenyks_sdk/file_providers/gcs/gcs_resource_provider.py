import os
from io import BytesIO
from typing import List

from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.file_resource_provider import FileResourceProvider
from tenyks_sdk.file_providers.gcs.gcs_client import GCSClient
from tenyks_sdk.file_providers.gcs.gcs_url_parser import GCSUrl
from tenyks_sdk.file_providers.config import GCS_SIGNED_URL_EXPIRATION_SECONDS


class GCSResourceProvider(FileResourceProvider):
    def __init__(
        self,
        gcs_url: GCSUrl,
        gcs_client: GCSClient,
    ) -> None:
        self.client: GCSClient = gcs_client
        self.gcs_location: GCSUrl = gcs_url
        self.signed_url_expiration_seconds = GCS_SIGNED_URL_EXPIRATION_SECONDS

    def get_file(self, relative_path: str) -> FileStorage:
        file_path = os.path.join(self.gcs_location.path, relative_path)
        blob = self.client.get_blob(self.gcs_location.bucket, file_path)
        blob_bytes = BytesIO(blob.download_as_bytes())
        file = FileStorage(blob_bytes, filename=os.path.basename(relative_path))
        return file

    def save_file(self, file_storage: FileStorage, relative_path: str) -> None:
        file_storage.stream.seek(0)
        file_path = os.path.join(self.gcs_location.path, relative_path)
        self.client.save_file(self.gcs_location.bucket, file_path, file_storage)

    def list_files_relative_paths(self, relative_path: str = "") -> List[str]:
        directory_path = os.path.join(self.gcs_location.path, relative_path)
        file_paths_only = self.client.list_files(
            self.gcs_location.bucket, directory_path
        )

        relative_paths_only = [
            file_path.replace(self.gcs_location.path, "")
            for file_path in file_paths_only
        ]

        return relative_paths_only

    def get_url(self, relative_path: str = "") -> str:
        path_in_bucket = os.path.join(self.gcs_location.path, relative_path)

        url = self.client.generate_url(
            self.gcs_location.bucket, path_in_bucket, self.signed_url_expiration_seconds
        )

        return url
