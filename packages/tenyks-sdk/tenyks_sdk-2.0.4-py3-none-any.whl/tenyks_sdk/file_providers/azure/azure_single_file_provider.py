import os
from typing import IO, Dict, Optional

from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.azure.azure_client import AzureBlobClient
from tenyks_sdk.file_providers.azure.azure_url_parser import AzureBlobUrlParser
from tenyks_sdk.file_providers.azure.data_classes import AzureLocation
from tenyks_sdk.file_providers.config import AZURE_SIGNED_URL_EXPIRATION_SECONDS
from tenyks_sdk.file_providers.single_file_provider import SingleFileProvider


class AzureSingleFileProvider(SingleFileProvider):
    def __init__(
        self,
        metadata_location: dict,
        signed_url_expiration_seconds: int = AZURE_SIGNED_URL_EXPIRATION_SECONDS,
    ) -> None:
        self.metadata_location: AzureLocation = AzureLocation.from_dict(
            metadata_location
        )
        self.client = AzureBlobClient(self.metadata_location.credentials)
        self.signed_url_expiration_seconds = signed_url_expiration_seconds
        self.azure_location = AzureBlobUrlParser(
            self.metadata_location.azure_uri
        ).parse()

    def get_file(self) -> FileStorage:
        stream = self.client.get_blob_stream(
            self.azure_location.container, self.azure_location.blob
        )
        file = FileStorage(stream, filename=os.path.basename(self.azure_location.blob))
        return file

    def save_file(self, file_storage: FileStorage) -> Dict[str, object]:
        file_storage.stream.seek(0)
        self.client.save_file(
            self.azure_location.container,
            os.path.join(self.azure_location.blob, file_storage.filename),
            file_storage.stream,
        )

        file_metadata_location: AzureLocation = AzureLocation.from_dict(
            self.metadata_location.to_dict()
        )

        file_metadata_location.azure_uri = os.path.join(
            file_metadata_location.azure_uri, file_storage.filename
        )

        return file_metadata_location.to_dict()

    def save_content(self, file_stream: IO[bytes]):
        file_stream.seek(0)
        self.client.save_file(
            self.azure_location.container, self.azure_location.blob, file_stream
        )

    def get_file_size(self) -> int:
        properties = self.client.get_blob_properties(
            self.azure_location.container, self.azure_location.blob
        )
        return properties.size

    def get_file_url(self) -> str:
        file_url = self.client.generate_url(
            self.azure_location.container,
            self.azure_location.blob,
            self.signed_url_expiration_seconds,
        )

        return file_url

    def does_file_exist(self) -> bool:
        return self.client.does_file_exist(
            self.azure_location.container, self.azure_location.blob
        )

    def get_file_upload_post_data(
        self, filename: str, max_file_size_bytes: Optional[int] = None
    ) -> dict:
        pass
