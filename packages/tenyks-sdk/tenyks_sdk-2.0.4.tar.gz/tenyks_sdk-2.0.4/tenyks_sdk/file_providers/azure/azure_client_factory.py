from functools import lru_cache
from tenyks_sdk.file_providers.azure.data_classes import AzureCredentials
from tenyks_sdk.file_providers.azure.azure_client import AzureBlobClient


class AzureBlobClientFactory:
    @staticmethod
    def create_client(azure_credentials: AzureCredentials) -> AzureBlobClient:
        """Original method without caching for backward compatibility"""
        return AzureBlobClient(azure_credentials)

    @staticmethod
    @lru_cache(maxsize=32)
    def create_client_with_cache(
        azure_credentials: AzureCredentials,
    ) -> AzureBlobClient:
        """New method with caching for better performance"""
        return AzureBlobClient(azure_credentials)
