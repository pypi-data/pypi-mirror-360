from typing import List

from tenyks_sdk.file_providers.selectors.file_selector_interface import (
    FileSelectorInterface,
)


class FileSelectorPipeline:
    def __init__(self, file_selectors: List[FileSelectorInterface]) -> None:
        self.file_selectors = file_selectors

    def is_accepted_path(self, relative_path: str) -> bool:
        if len(self.file_selectors) == 0:
            return True

        # Assumed OR
        accepted_by_all = any(
            selector.is_accepted_path(relative_path) for selector in self.file_selectors
        )

        return accepted_by_all
