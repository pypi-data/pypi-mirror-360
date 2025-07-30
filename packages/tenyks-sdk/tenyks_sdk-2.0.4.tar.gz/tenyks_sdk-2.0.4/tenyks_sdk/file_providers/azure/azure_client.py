import re
from datetime import datetime, timedelta
from io import BytesIO
from typing import List

from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged
from azure.storage.blob import (
    BlobClient,
    BlobProperties,
    BlobSasPermissions,
    BlobServiceClient,
    ContainerClient,
    generate_blob_sas,
)

from tenyks_sdk.file_providers.azure.data_classes import (
    AzureCredentials,
    AzureTokenType,
)


class AzureBlobClient:
    def __init__(self, azure_credentials: AzureCredentials) -> None:
        if azure_credentials.type == AzureTokenType.CONNECTION_STRING:
            self.client = BlobServiceClient.from_connection_string(
                azure_credentials.value
            )
            self.account_name, self.account_key = self._parse_connection_string(
                azure_credentials.value
            )
        elif azure_credentials.type == AzureTokenType.SAS_TOKEN:
            self.container_client = ContainerClient.from_container_url(
                azure_credentials.value
            )
            self.client = None  # Not used with container SAS URL
            self.account_name = re.search(
                "https?://(.+?).blob.core.windows.net", azure_credentials.value
            ).group(1)
            self.account_key = None
        else:
            raise ValueError(
                "Either a connection string or a container SAS URL must be provided."
            )

    def _parse_connection_string(self, connection_string: str):
        account_name_match = re.search("AccountName=([^;]+)", connection_string)
        account_key_match = re.search("AccountKey=([^;]+)", connection_string)
        account_name = account_name_match.group(1) if account_name_match else None
        account_key = account_key_match.group(1) if account_key_match else None
        return account_name, account_key

    def get_container_client(self, container_name: str) -> ContainerClient:
        if self.client:
            return self.client.get_container_client(container_name)
        elif (
            self.container_client
            and self.container_client.container_name == container_name
        ):
            return self.container_client
        else:
            raise ValueError(
                "Container client cannot be retrieved without proper initialization."
            )

    def get_blob_client(self, container_name: str, blob_name: str) -> BlobClient:
        container_client = self.get_container_client(container_name)
        return container_client.get_blob_client(blob=blob_name)

    def generate_url(
        self, container_name: str, blob_name: str, expiration_seconds: int
    ) -> str:
        if (
            self.account_key
        ):  # Generate SAS token if initialized with a connection string
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=container_name,
                blob_name=blob_name,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(seconds=expiration_seconds),
            )
            blob_client = self.get_blob_client(container_name, blob_name)
            blob_url = f"{blob_client.url}?{sas_token}"
        else:
            blob_client = self.get_blob_client(container_name, blob_name)
            blob_url = blob_client.url
        return blob_url

    def list_blobs(
        self, container_name: str, prefix: str = ""
    ) -> ItemPaged[BlobProperties]:
        container_client = self.get_container_client(container_name)
        blob_list = container_client.list_blobs(name_starts_with=prefix)
        return blob_list

    def list_files(self, container_name: str, prefix: str = "") -> List[str]:
        blob_list = self.list_blobs(container_name, prefix)
        return [blob.name for blob in blob_list if not blob.name.endswith("/")]

    def does_file_exist(self, container_name: str, blob_name: str) -> bool:
        blob_client = self.get_blob_client(container_name, blob_name)
        try:
            blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False

    def save_file(self, container_name: str, blob_name: str, file: BytesIO):
        blob_client = self.get_blob_client(container_name, blob_name)
        blob_client.upload_blob(file, overwrite=True)

    def delete_file(self, container_name: str, blob_name: str):
        blob_client = self.get_blob_client(container_name, blob_name)
        blob_client.delete_blob()

    def delete_by_prefix(self, container_name: str, prefix: str):
        container_client = self.get_container_client(container_name)
        blob_list = container_client.list_blobs(name_starts_with=prefix)
        for blob in blob_list:
            blob_client = self.get_blob_client(container_name, blob.name)
            blob_client.delete_blob()

    def get_blob_stream(self, container_name: str, blob_name: str) -> BytesIO:
        blob_client = self.get_blob_client(container_name, blob_name)
        download_stream = blob_client.download_blob()
        return BytesIO(download_stream.readall())

    def get_blob_properties(self, container_name: str, blob_name: str):
        blob_client = self.get_blob_client(container_name, blob_name)
        return blob_client.get_blob_properties()
