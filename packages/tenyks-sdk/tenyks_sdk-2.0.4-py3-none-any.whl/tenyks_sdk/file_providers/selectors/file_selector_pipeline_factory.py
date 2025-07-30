from typing import List

from tenyks_sdk.file_providers.data_classes import FileSelectorDefinition
from tenyks_sdk.file_providers.selectors.file_selector_factory import (
    FileSelectorFactory,
)
from tenyks_sdk.file_providers.selectors.file_selector_interface import (
    FileSelectorInterface,
)
from tenyks_sdk.file_providers.selectors.file_selector_pipeline import (
    FileSelectorPipeline,
)


class FileSelectorPipelineFactory:
    @staticmethod
    def create_from_selectors(
        file_selectors: List[FileSelectorInterface],
    ) -> FileSelectorPipeline:
        pipeline = FileSelectorPipeline(file_selectors)

        return pipeline

    @staticmethod
    def create_from_definitions(definitions: List[FileSelectorDefinition]):
        file_selectors = [
            FileSelectorFactory.get_file_selector(definition)
            for definition in definitions
        ]

        return FileSelectorPipelineFactory.create_from_selectors(file_selectors)
