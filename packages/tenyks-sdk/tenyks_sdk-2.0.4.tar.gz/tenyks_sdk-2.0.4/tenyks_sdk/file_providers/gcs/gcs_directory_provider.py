import os
from io import BytesIO
from typing import Dict, List

from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.directory_provider import DirectoryProvider
from tenyks_sdk.file_providers.gcs.data_classes import GCSLocation
from tenyks_sdk.file_providers.gcs.gcs_client_factory import GCSClientFactory
from tenyks_sdk.file_providers.gcs.gcs_url_parser import GCSUrlParser


class GcsDirectoryProvider(DirectoryProvider):

    def __init__(self, location: Dict) -> None:
        self.metadata_location: GCSLocation = GCSLocation.from_dict(location)
        self.client = GCSClientFactory.create_client(self.metadata_location.credentials)
        self.gcs_location = GCSUrlParser.parse_gcs_url(self.metadata_location.gcs_uri)

    def list_files(self, file_extensions: list = None) -> List[str]:
        file_paths_only = self.client.list_files(
            self.gcs_location.bucket, self.gcs_location.path
        )

        relative_paths_only = [
            file_path.replace(self.gcs_location.path, "")
            for file_path in file_paths_only
        ]

        if file_extensions is not None:
            clean_file_extensions = [
                (f".{ext}" if not ext.startswith(".") else ext).lower()
                for ext in file_extensions
            ]
            relative_paths_only = list(
                filter(
                    lambda filename: (
                        os.path.splitext(filename)[1].lower() in clean_file_extensions
                    ),
                    relative_paths_only,
                )
            )

        return relative_paths_only

    def get_file(self, filename: str) -> FileStorage:
        filepath = os.path.join(self.gcs_location.path, filename)
        blob = self.client.get_blob(self.gcs_location.bucket, filepath)
        blob_bytes = BytesIO(blob.download_as_bytes())
        file = FileStorage(blob_bytes, filename=filename)

        return file

    def save_file(self, file_storage: FileStorage) -> dict:
        # not touching user data
        pass

    def get_size(self) -> int:
        total_size = 0
        blob_list = self.client.list_blobs(
            self.gcs_location.bucket, self.gcs_location.path
        )

        for blob in blob_list:
            total_size += blob.size

        return total_size
