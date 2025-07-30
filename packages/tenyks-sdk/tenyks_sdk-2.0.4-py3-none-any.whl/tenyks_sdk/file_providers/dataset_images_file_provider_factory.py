from tenyks_sdk.file_providers.aws.aws_dataset_images_file_provider import (
    AWSDatasetImagesFileProvider,
)
from tenyks_sdk.file_providers.azure.azure_dataset_images_file_provider import (
    AzureDatasetImagesFileProvider,
)
from tenyks_sdk.file_providers.config import StorageLocationType
from tenyks_sdk.file_providers.dataset_images_file_provider import (
    DatasetImagesFileProvider,
)
from tenyks_sdk.file_providers.gcs.gcs_client_factory import GCSClientFactory
from tenyks_sdk.file_providers.gcs.gcs_dataset_images_file_provider import (
    GCSDatasetImagesFileProvider,
)


class DatasetImagesFileProviderFactory:
    @staticmethod
    def create_file_provider(
        images_location: dict,
    ) -> DatasetImagesFileProvider:
        assert images_location["type"] in list(
            StorageLocationType
        ), f"Image location {images_location['type']} is not supported"

        images_location_type = StorageLocationType(images_location["type"])

        if images_location_type == StorageLocationType.AWS_S3:
            dataset_images_file_provider = AWSDatasetImagesFileProvider(
                images_location=images_location,
                cache=False,
            )
        elif images_location_type == StorageLocationType.GCS:
            client = GCSClientFactory.create_client(images_location["credentials"])

            dataset_images_file_provider = GCSDatasetImagesFileProvider(
                images_location, client
            )
        elif images_location_type == StorageLocationType.AZURE:
            dataset_images_file_provider = AzureDatasetImagesFileProvider(
                images_location, cache=False
            )

        return dataset_images_file_provider

    @staticmethod
    def create_file_provider_with_cache(
        images_location: dict,
    ) -> DatasetImagesFileProvider:
        assert images_location["type"] in list(
            StorageLocationType
        ), f"Image location {images_location['type']} is not supported"

        images_location_type = StorageLocationType(images_location["type"])

        if images_location_type == StorageLocationType.AWS_S3:
            dataset_images_file_provider = AWSDatasetImagesFileProvider(
                images_location=images_location, cache=True
            )
        elif images_location_type == StorageLocationType.GCS:
            client = GCSClientFactory.create_client_with_cache(
                images_location["credentials"]
            )

            dataset_images_file_provider = GCSDatasetImagesFileProvider(
                images_location, client
            )
        elif images_location_type == StorageLocationType.AZURE:
            dataset_images_file_provider = AzureDatasetImagesFileProvider(
                images_location, cache=True
            )

        return dataset_images_file_provider
