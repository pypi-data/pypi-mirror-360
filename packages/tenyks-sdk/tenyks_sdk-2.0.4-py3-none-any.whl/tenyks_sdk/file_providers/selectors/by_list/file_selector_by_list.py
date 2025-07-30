from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from tenyks_sdk.file_providers.selectors.file_selector_interface import (
    FileSelectorInterface,
)


@dataclass_json
@dataclass
class FileSelectorByListParams:
    relative_paths: List[str]


class FileSelectorByList(FileSelectorInterface):
    def __init__(self, params: FileSelectorByListParams) -> None:
        self.relative_paths = params.relative_paths

    def is_accepted_path(self, relative_path: str) -> bool:
        is_accepted = relative_path in self.relative_paths

        return is_accepted
