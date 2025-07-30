from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json

from tenyks_sdk.file_providers.config import StorageLocationType
from tenyks_sdk.file_providers.data_classes import FileSelectorDefinition


@dataclass_json
@dataclass
class AWSS3Credentials:
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str
    aws_session_token: str = None

    def __hash__(self) -> int:
        if self.aws_session_token is not None:
            return hash(
                (
                    self.aws_access_key_id,
                    self.aws_secret_access_key,
                    self.region_name,
                    self.aws_session_token,
                )
            )
        else:
            return hash(
                (self.aws_access_key_id, self.aws_secret_access_key, self.region_name)
            )

    def __eq__(self, other) -> bool:
        if not isinstance(other, AWSS3Credentials):
            return False

        if self.aws_session_token is not None and other.aws_session_token is not None:
            return (
                self.aws_access_key_id == other.aws_access_key_id
                and self.aws_secret_access_key == other.aws_secret_access_key
                and self.region_name == other.region_name
                and self.aws_session_token == other.aws_session_token
            )
        elif self.aws_session_token is None and other.aws_session_token is None:
            return (
                self.aws_access_key_id == other.aws_access_key_id
                and self.aws_secret_access_key == other.aws_secret_access_key
                and self.region_name == other.region_name
            )
        else:
            return False


@dataclass_json
@dataclass
class AWSLocation:
    s3_uri: str
    credentials: AWSS3Credentials
    type: StorageLocationType
    selectors: List[FileSelectorDefinition] = field(default_factory=list)
    write_permission: bool = False


@dataclass_json
@dataclass
class AWSVideoLocation:
    type: StorageLocationType
    s3_uri: str
    credentials: AWSS3Credentials
