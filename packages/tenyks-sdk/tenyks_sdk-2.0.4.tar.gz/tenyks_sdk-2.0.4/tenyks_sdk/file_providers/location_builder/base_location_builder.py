import copy
from typing import Dict

from tenyks_sdk.file_providers.location_builder.location_builder import LocationBuilder
from tenyks_sdk.file_providers.location_builder.string_location_change import (
    StringLocationChange,
)


class BaseLocationBuilder(LocationBuilder):
    def __init__(self, location: Dict[str, object], property: str) -> None:
        self.location = copy.deepcopy(location)
        self.property = property
        self.current_path = self.location[self.property]

    def go_to_folder(self, folder_name: str) -> LocationBuilder:
        self.current_path = StringLocationChange.go_to_folder(
            self.current_path, folder_name
        )

        return self

    def folder_up(self) -> LocationBuilder:
        self.current_path = StringLocationChange.folder_up(self.current_path)

        return self

    def get_location_dictionary(self) -> Dict[str, object]:
        self.location[self.property] = self.current_path

        return self.location

    def get_location_path(self):
        return self.current_path

    def select_file(self, filename: str) -> LocationBuilder:
        self.current_path = StringLocationChange.add_file_to_path(
            self.current_path, filename
        )

        return self

    def remove_file(self) -> LocationBuilder:
        self.current_path = StringLocationChange.remove_file_from_path(
            self.current_path
        )

        return self
