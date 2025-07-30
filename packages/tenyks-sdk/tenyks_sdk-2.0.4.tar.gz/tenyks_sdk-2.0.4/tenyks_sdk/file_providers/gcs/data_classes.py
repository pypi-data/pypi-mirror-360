from dataclasses import dataclass, field
from typing import Dict, List

from dataclasses_json import dataclass_json

from tenyks_sdk.file_providers.config import StorageLocationType
from tenyks_sdk.file_providers.data_classes import FileSelectorDefinition


@dataclass_json
@dataclass
class GCSLocation:
    gcs_uri: str
    credentials: Dict[str, str]
    type: StorageLocationType
    selectors: List[FileSelectorDefinition] = field(default_factory=list)
