import io
import os
from typing import Dict, List

from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.aws.boto_s3_client_factory import Boto3S3ClientFactory
from tenyks_sdk.file_providers.aws.data_classes import AWSLocation
from tenyks_sdk.file_providers.aws.s3_client import S3Client
from tenyks_sdk.file_providers.aws.s3_url_parser import S3Url, S3UrlParser
from tenyks_sdk.file_providers.directory_provider import DirectoryProvider


class AwsDirectoryProvider(DirectoryProvider):
    def __init__(self, location: Dict) -> None:
        self.location: AWSLocation = AWSLocation.from_dict(location)

        self.s3_client: S3Client = Boto3S3ClientFactory.create_client(
            self.location.credentials
        )
        self.s3_url: S3Url = S3UrlParser(self.location.s3_uri).parse()

    def list_files(self, file_extensions: list = None) -> List[str]:
        content = self.s3_client.list_objects_v2(self.s3_url.bucket, self.s3_url.path)
        file_names = [item["Key"].replace(self.s3_url.path, "") for item in content]

        if file_extensions is not None:
            clean_file_extensions = [
                (f".{ext}" if not ext.startswith(".") else ext).lower()
                for ext in file_extensions
            ]
            file_names = list(
                filter(
                    lambda filename: (
                        os.path.splitext(filename)[1].lower() in clean_file_extensions
                    ),
                    file_names,
                )
            )

        return file_names

    def get_file(self, filename: str) -> FileStorage:
        filepath = os.path.join(self.s3_url.path, filename)
        response = self.s3_client.get_object(self.s3_url.bucket, filepath)

        file_stream = response["Body"]
        file_storage = FileStorage(stream=file_stream, filename=filename)

        return file_storage

    def save_file(self, file_storage: FileStorage) -> dict:
        buffer = io.BytesIO()
        buffer.write(file_storage.stream.read())
        buffer.seek(0)

        self.s3_client.upload_fileobj(
            buffer,
            self.s3_url.bucket,
            os.path.join(self.s3_url.path, file_storage.filename),
        )

        location = self.location
        location.s3_uri = os.path.join(location.s3_uri, file_storage.filename)
        return location.to_dict()

    def get_size(self) -> int:
        total_size = 0
        content = self.s3_client.list_objects_v2(self.s3_url.bucket, self.s3_url.path)

        for item in content:
            total_size += item["Size"]

        return total_size
