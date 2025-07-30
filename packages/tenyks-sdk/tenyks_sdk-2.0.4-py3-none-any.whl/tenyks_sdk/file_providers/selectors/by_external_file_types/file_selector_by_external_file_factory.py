from dataclasses import dataclass
from typing import Dict

from dataclasses_json import dataclass_json

from tenyks_sdk.file_providers.selectors.by_external_file_types.file_selector_by_external_file_csv import (
    FileSelectorByExternalTypeCsv,
)
from tenyks_sdk.file_providers.selectors.by_external_file_types.file_selector_by_external_files_dataclasses import (
    FileSelectorByExternalFilesType,
)
from tenyks_sdk.file_providers.single_file_provider_factory import (
    SingleFileProviderFactory,
)


@dataclass_json
@dataclass
class FileSelectorByExternalParams:
    file_location: Dict
    file_type: str = FileSelectorByExternalFilesType.CSV.value


class FileSelectorByExternalFileFactory:
    @staticmethod
    def get_file_selector_by_external_file(params: FileSelectorByExternalParams):
        file_provider = SingleFileProviderFactory.create_file_provider_from_location(
            params.file_location
        )
        file = file_provider.get_file()
        file_type = FileSelectorByExternalFilesType(params.file_type)

        if file_type == FileSelectorByExternalFilesType.CSV:
            return FileSelectorByExternalTypeCsv(file)

        raise ValueError("Unimplemented file selector for file type")
