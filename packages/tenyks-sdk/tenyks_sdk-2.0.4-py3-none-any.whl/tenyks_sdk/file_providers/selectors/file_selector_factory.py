from tenyks_sdk.file_providers.config import FileSelectorType
from tenyks_sdk.file_providers.data_classes import FileSelectorDefinition
from tenyks_sdk.file_providers.selectors.by_external_file_types.file_selector_by_external_file_factory import (
    FileSelectorByExternalFileFactory,
    FileSelectorByExternalParams,
)
from tenyks_sdk.file_providers.selectors.by_folder.file_selector_by_folder import (
    FileSelectorByFolder,
    FileSelectorByFolderParams,
)
from tenyks_sdk.file_providers.selectors.by_list.file_selector_by_list import (
    FileSelectorByList,
    FileSelectorByListParams,
)
from tenyks_sdk.file_providers.selectors.file_selector_interface import (
    FileSelectorInterface,
)


class FileSelectorFactory:
    @staticmethod
    def get_file_selector(
        file_selector_definition: FileSelectorDefinition,
    ) -> FileSelectorInterface:
        type = FileSelectorType(file_selector_definition.type)

        if type == FileSelectorType.LIST:
            return FileSelectorByList(
                FileSelectorByListParams.from_dict(file_selector_definition.params)
            )
        elif type == FileSelectorType.FILE:
            return FileSelectorByExternalFileFactory.get_file_selector_by_external_file(
                FileSelectorByExternalParams.from_dict(file_selector_definition.params)
            )
        elif type == FileSelectorType.FOLDER:
            return FileSelectorByFolder(
                FileSelectorByFolderParams.from_dict(file_selector_definition.params)
            )

        raise ValueError(
            f"Unsupported file selector type {file_selector_definition.type}"
        )
