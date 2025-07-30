from dataclasses import dataclass
from urllib.parse import urlparse

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class AzureBlobUrl:
    account_name: str
    container: str
    blob: str


class AzureBlobUrlParser:
    def __init__(self, azure_blob_uri: str) -> None:
        self.azure_blob_uri = azure_blob_uri

    def parse(self) -> AzureBlobUrl:
        parse_result = urlparse(self.azure_blob_uri)

        # Extract the account name and container/blob path from the netloc and path
        account_name = parse_result.netloc.split(".")[0]
        path_parts = parse_result.path.lstrip("/").split("/", 1)
        container = path_parts[0]
        blob = path_parts[1] if len(path_parts) > 1 else ""

        azure_blob_url = AzureBlobUrl(account_name, container, blob)
        return azure_blob_url
