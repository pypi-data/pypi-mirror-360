from typing import Dict

from tenyks_sdk.file_providers.aws.aws_single_file_provider import AWSSingleFileProvider
from tenyks_sdk.file_providers.aws.boto_s3_client_factory import Boto3S3ClientFactory
from tenyks_sdk.file_providers.aws.data_classes import AWSS3Credentials
from tenyks_sdk.file_providers.azure.azure_single_file_provider import (
    AzureSingleFileProvider,
)
from tenyks_sdk.file_providers.config import StorageLocationType
from tenyks_sdk.file_providers.gcs.gcs_client_factory import GCSClientFactory
from tenyks_sdk.file_providers.gcs.gcs_single_file_provider import GCSSingleFileProvider
from tenyks_sdk.file_providers.single_file_provider import SingleFileProvider


class SingleFileProviderFactory:
    @staticmethod
    def create_file_provider_from_location(
        file_location: Dict[str, object],
    ) -> SingleFileProvider:
        assert file_location["type"] in list(
            StorageLocationType
        ), f"File location {type} is not supported"
        storage_location_type = StorageLocationType(file_location["type"])

        if storage_location_type == StorageLocationType.AWS_S3:
            s3_credentials = AWSS3Credentials.from_dict(file_location["credentials"])
            client = Boto3S3ClientFactory.create_client(s3_credentials)

            dataset_images_file_provider = AWSSingleFileProvider(file_location, client)
        elif storage_location_type == StorageLocationType.GCS:
            client = GCSClientFactory.create_client(file_location["credentials"])

            dataset_images_file_provider = GCSSingleFileProvider(file_location, client)
        elif storage_location_type == StorageLocationType.AZURE:
            dataset_images_file_provider = AzureSingleFileProvider(file_location)

        return dataset_images_file_provider
