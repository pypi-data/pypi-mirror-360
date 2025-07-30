import os
from typing import List

from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.azure.azure_client import AzureBlobClient
from tenyks_sdk.file_providers.azure.azure_url_parser import AzureBlobUrl
from tenyks_sdk.file_providers.file_resource_provider import FileResourceProvider
from tenyks_sdk.file_providers.config import AZURE_SIGNED_URL_EXPIRATION_SECONDS


class AzureResourceProvider(FileResourceProvider):
    def __init__(
        self, azure_blob_url: AzureBlobUrl, azure_blob_client: AzureBlobClient
    ) -> None:
        self.azure_blob_client: AzureBlobClient = azure_blob_client
        self.azure_blob_url = azure_blob_url
        self.signed_url_expiration_seconds = AZURE_SIGNED_URL_EXPIRATION_SECONDS

    def get_file(self, relative_path: str) -> FileStorage:
        path_in_container = self.__get_full_path(relative_path)
        stream = self.azure_blob_client.get_blob_stream(
            self.azure_blob_url.container, path_in_container
        )

        file_storage = FileStorage(stream, filename=os.path.basename(relative_path))
        return file_storage

    def save_file(self, file_storage: FileStorage, relative_path: str) -> None:
        file_storage.stream.seek(0)

        path_in_container = self.__get_full_path(relative_path)
        self.azure_blob_client.save_file(
            self.azure_blob_url.container, path_in_container, file_storage.stream
        )

    def list_files_relative_paths(self, relative_path: str = "") -> List[str]:
        path_in_container = self.__get_full_path(relative_path)
        all_files = self.azure_blob_client.list_files(
            self.azure_blob_url.container, path_in_container
        )

        relative_paths = [
            os.path.relpath(path, self.azure_blob_url.blob) for path in all_files
        ]
        return relative_paths

    def get_url(self, relative_path: str = "") -> str:
        path_in_container = self.__get_full_path(relative_path)
        url = self.azure_blob_client.generate_url(
            self.azure_blob_url.container,
            path_in_container,
            self.signed_url_expiration_seconds,
        )

        return url

    def __get_full_path(self, relative_path: str) -> str:
        relative_path = relative_path.lstrip("/")
        return os.path.join(self.azure_blob_url.blob, relative_path)
