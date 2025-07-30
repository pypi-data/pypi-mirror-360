from dataclasses import dataclass, field
from typing import Any, List

from dataclasses_json import dataclass_json

from tenyks_sdk.file_providers.config import FileSelectorType, StorageLocationType


@dataclass_json
@dataclass
class FileSelectorDefinition:
    type: FileSelectorType
    params: Any


@dataclass_json
@dataclass
class StorageLocation:
    type: StorageLocationType
    selectors: List[FileSelectorDefinition] = field(default_factory=list)
