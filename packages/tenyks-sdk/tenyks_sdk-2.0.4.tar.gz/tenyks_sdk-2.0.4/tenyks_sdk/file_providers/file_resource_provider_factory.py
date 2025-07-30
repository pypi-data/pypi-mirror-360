from typing import Dict

from tenyks_sdk.file_providers.aws.boto_s3_client_factory import Boto3S3ClientFactory
from tenyks_sdk.file_providers.aws.data_classes import AWSLocation
from tenyks_sdk.file_providers.aws.s3_resource_provider import S3ResourceProvider
from tenyks_sdk.file_providers.aws.s3_url_parser import S3Url, S3UrlParser
from tenyks_sdk.file_providers.azure.azure_client import AzureBlobClient
from tenyks_sdk.file_providers.azure.azure_resource_provider import (
    AzureResourceProvider,
)
from tenyks_sdk.file_providers.azure.azure_url_parser import (
    AzureBlobUrl,
    AzureBlobUrlParser,
)
from tenyks_sdk.file_providers.azure.data_classes import AzureLocation
from tenyks_sdk.file_providers.config import StorageLocationType
from tenyks_sdk.file_providers.file_resource_provider import FileResourceProvider
from tenyks_sdk.file_providers.gcs.data_classes import GCSLocation
from tenyks_sdk.file_providers.gcs.gcs_client import GCSClient
from tenyks_sdk.file_providers.gcs.gcs_client_factory import GCSClientFactory
from tenyks_sdk.file_providers.gcs.gcs_resource_provider import GCSResourceProvider
from tenyks_sdk.file_providers.gcs.gcs_url_parser import GCSUrl, GCSUrlParser


class FileResourceProviderFactory:
    @staticmethod
    def create_resource_provider(
        resource_location: Dict[str, object],
    ) -> FileResourceProvider:
        assert resource_location["type"] in list(
            StorageLocationType
        ), f"Resource location {resource_location['type']} is not supported"

        resource_type = StorageLocationType(resource_location["type"])

        if resource_type == StorageLocationType.AWS_S3:
            s3_resource_location: AWSLocation = AWSLocation.from_dict(resource_location)

            s3_client = Boto3S3ClientFactory.create_client(
                s3_resource_location.credentials
            )
            s3_url: S3Url = S3UrlParser(s3_resource_location.s3_uri).parse()
            return S3ResourceProvider(s3_url, s3_client)
        elif resource_type == StorageLocationType.GCS:
            gcs_resource_location: GCSLocation = GCSLocation.from_dict(
                resource_location
            )

            gcs_client: GCSClient = GCSClientFactory.create_client(
                gcs_resource_location.credentials
            )
            gcs_url: GCSUrl = GCSUrlParser.parse_gcs_url(gcs_resource_location.gcs_uri)

            return GCSResourceProvider(gcs_url, gcs_client)
        elif resource_type == StorageLocationType.AZURE:
            azure_resource_location: AzureLocation = AzureLocation.from_dict(
                resource_location
            )
            azure_client: AzureBlobClient = AzureBlobClient(
                azure_resource_location.credentials
            )
            azure_url: AzureBlobUrl = AzureBlobUrlParser(
                azure_resource_location.azure_uri
            ).parse()

            return AzureResourceProvider(azure_url, azure_client)

        raise NotImplementedError(
            f"The resource provider class does not exist for type {resource_type}"
        )
