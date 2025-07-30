from dataclasses import dataclass
from urllib.parse import urlparse

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class GCSUrl:
    bucket: str
    path: str


class GCSUrlParser:
    @staticmethod
    def parse_gcs_url(gcs_url: str) -> GCSUrl:
        parse_result = urlparse(gcs_url)
        gcs_url = GCSUrl(parse_result.netloc, parse_result.path[1:])
        return gcs_url
