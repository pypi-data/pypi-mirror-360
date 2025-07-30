from typing import Dict

from tenyks_sdk.file_providers.aws.aws_location_builder import AwsLocationBuilder
from tenyks_sdk.file_providers.azure.azure_location_builder import AzureLocationBuilder
from tenyks_sdk.file_providers.gcs.gcs_location_builder import GcsLocationBuilder
from tenyks_sdk.file_providers.location_builder.location_builder import LocationBuilder


class LocationBuilderFactory:
    @staticmethod
    def get_location_builder(location: Dict[str, object]) -> LocationBuilder:
        location_type = location["type"]

        if location_type == "aws_s3":
            return AwsLocationBuilder(location)
        elif location_type == "gcs":
            return GcsLocationBuilder(location)
        elif location_type == "azure":
            return AzureLocationBuilder(location)

        raise ValueError(f"Not implemented for {location_type}")
