from dataclasses import dataclass
from urllib.parse import urlparse

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class S3Url:
    bucket: str
    path: str


class S3UrlParser:
    def __init__(self, s3_uri: str) -> None:
        self.s3_uri = s3_uri

    def parse(self):
        parse_result = urlparse(self.s3_uri)
        s3_url = S3Url(parse_result.netloc, parse_result.path[1:])
        return s3_url
