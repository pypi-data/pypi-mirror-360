from dataclasses import dataclass, field
from enum import Enum
from typing import List
from urllib.parse import parse_qs, urlparse

from dataclasses_json import dataclass_json

from tenyks_sdk.file_providers.config import StorageLocationType
from tenyks_sdk.file_providers.data_classes import FileSelectorDefinition


class AzureTokenType(str, Enum):
    CONNECTION_STRING = "connection_string"
    SAS_TOKEN = "sas"


@dataclass_json
@dataclass
class AzureCredentials:
    type: AzureTokenType
    value: str

    def __hash__(self) -> int:
        return hash((self.value, self.type))

    def __eq__(self, other) -> bool:
        if not isinstance(other, AzureCredentials):
            return False
        return self.value == other.value and self.type == other.type


@dataclass_json
@dataclass
class AzureLocation:
    azure_uri: str
    credentials: AzureCredentials
    type: StorageLocationType
    selectors: List[FileSelectorDefinition] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.credentials, dict):
            self.credentials = AzureCredentials.from_dict(self.credentials)

        if self.credentials.type == AzureTokenType.CONNECTION_STRING:
            if not self.is_valid_connection_string():
                raise ValueError(
                    "Invalid Azure connection string format. Use the following format: "
                    "DefaultEndpointsProtocol=https;"
                    "AccountName=your_account_name;"
                    "AccountKey=your_account_key;EndpointSuffix=core.windows.net"
                )
        elif self.credentials.type == AzureTokenType.SAS_TOKEN:
            if not self.is_sas_url_valid():
                raise ValueError(
                    "Invalid Azure container SAS URL. Use the following format: "
                    "https://<storage_account>.<service>.core.windows.net/<resource_path>?<sas_token>"
                )
        else:
            raise ValueError(f"Unknown Azure token type {self.credentials.type}.")

    def is_sas_url_valid(self) -> bool:
        try:
            parsed_url = urlparse(self.credentials.value)
            parameters = parse_qs(parsed_url.query)

            if parsed_url.scheme.lower() != "https":
                return False

            # Required SAS token fields
            required_fields = ["sv", "sp", "se", "sig"]

            if all(field in parameters for field in required_fields):
                return True
            else:
                return False
        except Exception:
            return False

    def is_valid_connection_string(self) -> bool:
        required_parts = ["AccountName", "AccountKey"]
        return all(part in self.credentials.value for part in required_parts)
