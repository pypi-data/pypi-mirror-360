import os
from typing import Dict, List

from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.azure.azure_client import AzureBlobClient
from tenyks_sdk.file_providers.azure.azure_url_parser import AzureBlobUrlParser
from tenyks_sdk.file_providers.azure.data_classes import AzureLocation
from tenyks_sdk.file_providers.directory_provider import DirectoryProvider


class AzureDirectoryProvider(DirectoryProvider):

    def __init__(self, location: Dict) -> None:
        self.location: AzureLocation = AzureLocation.from_dict(location)
        self.client = AzureBlobClient(self.location.credentials)
        self.azure_blob_location = AzureBlobUrlParser(self.location.azure_uri).parse()

    def list_files(self, file_extensions: list = None) -> List[str]:
        file_paths_only = self.client.list_files(
            self.azure_blob_location.container, self.azure_blob_location.blob
        )

        relative_paths_only = [
            file_path.replace(self.azure_blob_location.blob, "")
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
        relative_filepath = filename.lstrip("/")
        full_path = os.path.join(self.azure_blob_location.blob, relative_filepath)
        stream = self.client.get_blob_stream(
            self.azure_blob_location.container, full_path
        )
        file = FileStorage(stream=stream, filename=filename)
        return file

    def save_file(self, file_storage: FileStorage) -> dict:
        file_storage.stream.seek(0)
        self.client.save_file(
            self.azure_blob_location.container,
            os.path.join(self.azure_blob_location.blob, file_storage.filename),
            file_storage.stream,
        )

        file_metadata_location: AzureLocation = AzureLocation.from_dict(
            self.location.to_dict()
        )

        file_metadata_location.azure_uri = os.path.join(
            file_metadata_location.azure_uri, file_storage.filename
        )

        return file_metadata_location.to_dict()

    def get_size(self) -> int:
        total_size = 0
        blob_list = self.client.list_blobs(
            self.azure_blob_location.container, self.azure_blob_location.blob
        )

        for blob in blob_list:
            total_size += blob.size

        return total_size
