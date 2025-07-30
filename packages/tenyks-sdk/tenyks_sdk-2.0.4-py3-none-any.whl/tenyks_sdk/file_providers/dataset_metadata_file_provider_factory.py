from tenyks_sdk.file_providers.aws.aws_dataset_metadata_file_provider import (
    AWSDatasetMetadataFileProvider,
)
from tenyks_sdk.file_providers.azure.azure_dataset_metadata_file_provider import (
    AzureDatasetMetadataFileProvider,
)
from tenyks_sdk.file_providers.config import StorageLocationType
from tenyks_sdk.file_providers.dataset_metadata_file_provider import (
    DatasetMetadataFileProvider,
)
from tenyks_sdk.file_providers.gcs.gcs_dataset_metadata_file_provider import (
    GCSDatasetMetadataFileProvider,
)


class DatasetMetadataFileProviderFactory:
    @staticmethod
    def create_file_provider(
        metadata_location: dict,
    ) -> DatasetMetadataFileProvider:
        assert metadata_location["type"] in list(
            StorageLocationType
        ), f"Metadata location {metadata_location['type']} is not supported"

        metadata_location_type = StorageLocationType(metadata_location["type"])

        if metadata_location_type == StorageLocationType.AWS_S3:
            dataset_metadata_file_provider = AWSDatasetMetadataFileProvider(
                metadata_location=metadata_location,
            )
        elif metadata_location_type == StorageLocationType.GCS:
            dataset_metadata_file_provider = GCSDatasetMetadataFileProvider(
                metadata_location
            )
        elif metadata_location_type == StorageLocationType.AZURE:
            dataset_metadata_file_provider = AzureDatasetMetadataFileProvider(
                metadata_location
            )

        return dataset_metadata_file_provider
