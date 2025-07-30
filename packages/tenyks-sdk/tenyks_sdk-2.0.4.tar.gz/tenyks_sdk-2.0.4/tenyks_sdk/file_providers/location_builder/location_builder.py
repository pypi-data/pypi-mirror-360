from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict


class LocationBuilder(ABC):
    @abstractmethod
    def folder_up() -> LocationBuilder:
        pass

    @abstractmethod
    def go_to_folder(self, folder_name: str) -> LocationBuilder:
        pass

    @abstractmethod
    def get_location_dictionary() -> Dict[str, object]:
        pass

    @abstractmethod
    def get_location_path() -> str:
        pass

    @abstractmethod
    def select_file(self, filename: str) -> LocationBuilder:
        pass

    @abstractmethod
    def remove_file(self) -> LocationBuilder:
        pass
