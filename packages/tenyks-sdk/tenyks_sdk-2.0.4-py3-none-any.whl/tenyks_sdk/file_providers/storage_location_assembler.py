import os
from typing import Union

from tenyks_sdk.file_providers.aws.data_classes import AWSLocation
from tenyks_sdk.file_providers.azure.data_classes import AzureLocation
from tenyks_sdk.file_providers.config import StorageLocationType
from tenyks_sdk.file_providers.data_classes import StorageLocation
from tenyks_sdk.file_providers.gcs.data_classes import GCSLocation


class StorageLocationAssembler:
    def convert_dict_to_storage_location(
        storage_location: dict,
    ) -> Union[StorageLocation, AWSLocation, GCSLocation, AzureLocation]:
        assert storage_location["type"] in list(
            StorageLocationType
        ), f"Storage location {storage_location['type']} is not supported"

        if storage_location["type"] == StorageLocationType.AWS_S3:
            storage_location["s3_uri"] = os.path.join(storage_location["s3_uri"], "")

            return AWSLocation(
                **storage_location,
            )

        if storage_location["type"] == StorageLocationType.GCS:
            storage_location["gcs_uri"] = os.path.join(storage_location["gcs_uri"], "")

            return GCSLocation(
                **storage_location,
            )

        if storage_location["type"] == StorageLocationType.AZURE:
            storage_location["azure_uri"] = os.path.join(
                storage_location["azure_uri"], ""
            )

            return AzureLocation(
                **storage_location,
            )
