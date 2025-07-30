from typing import Dict

from tenyks_sdk.file_providers.aws.aws_directory_provider import AwsDirectoryProvider
from tenyks_sdk.file_providers.azure.azure_directory_provider import (
    AzureDirectoryProvider,
)
from tenyks_sdk.file_providers.config import StorageLocationType
from tenyks_sdk.file_providers.directory_provider import DirectoryProvider
from tenyks_sdk.file_providers.gcs.gcs_directory_provider import GcsDirectoryProvider


class DirectoryProviderFactory:
    @staticmethod
    def get_provider(location: Dict) -> DirectoryProvider:

        location_type = StorageLocationType(location["type"])

        if location_type == StorageLocationType.AWS_S3:
            return AwsDirectoryProvider(location)
        elif location_type == StorageLocationType.GCS:
            return GcsDirectoryProvider(location)
        elif location_type == StorageLocationType.AZURE:
            return AzureDirectoryProvider(location)

        raise NotImplementedError(f"Location {location['type']} is not supported")
