from dataclasses import dataclass

from dataclasses_json import dataclass_json

from tenyks_sdk.file_providers.selectors.file_selector_interface import (
    FileSelectorInterface,
)


@dataclass_json
@dataclass
class FileSelectorByFolderParams:
    folder_path: str


class FileSelectorByFolder(FileSelectorInterface):
    def __init__(self, params: FileSelectorByFolderParams) -> None:
        self.folder_path = params.folder_path

    def is_accepted_path(self, relative_path: str) -> bool:
        is_accepted = relative_path.startswith(self.folder_path)

        return is_accepted
