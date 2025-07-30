from typing import Dict

from tenyks_sdk.file_providers.location_builder.base_location_builder import (
    BaseLocationBuilder,
)


class GcsLocationBuilder(BaseLocationBuilder):
    PROPERTY = "gcs_uri"

    def __init__(self, location: Dict[str, object]) -> None:
        super().__init__(location, self.PROPERTY)
