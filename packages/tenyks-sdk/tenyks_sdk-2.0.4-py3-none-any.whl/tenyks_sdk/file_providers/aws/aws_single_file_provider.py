import os
from io import BytesIO
from typing import IO, Dict, Optional

from botocore.exceptions import ClientError
from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.aws.data_classes import AWSLocation
from tenyks_sdk.file_providers.aws.s3_client import S3Client
from tenyks_sdk.file_providers.aws.s3_url_parser import S3Url, S3UrlParser
from tenyks_sdk.file_providers.config import S3_PRESIGNED_URL_EXPIRATION
from tenyks_sdk.file_providers.single_file_provider import SingleFileProvider


class AWSSingleFileProvider(SingleFileProvider):
    def __init__(
        self,
        aws_location: Dict[str, object],
        client: S3Client,
        s3_presigned_url_expiration: int = S3_PRESIGNED_URL_EXPIRATION,
    ) -> None:
        self.aws_location: AWSLocation = AWSLocation.from_dict(aws_location)
        self.s3_client: S3Client = client
        self.s3_presigned_url_expiration = s3_presigned_url_expiration
        self.s3_url: S3Url = S3UrlParser(self.aws_location.s3_uri).parse()

    def get_file(self) -> FileStorage:
        response = self.s3_client.get_object(self.s3_url.bucket, self.s3_url.path)
        file_stream = BytesIO(response["Body"].read())
        file_storage = FileStorage(
            stream=file_stream, filename=os.path.basename(self.s3_url.path)
        )
        return file_storage

    def save_file(self, file_storage: FileStorage) -> Dict[str, object]:
        file_storage.stream.seek(0)

        self.s3_client.upload_fileobj(
            file_storage.stream,
            self.s3_url.bucket,
            os.path.join(self.s3_url.path, file_storage.filename),
        )

        file_location: AWSLocation = AWSLocation.from_dict(self.aws_location.to_dict())

        file_location.s3_uri = os.path.join(file_location.s3_uri, file_storage.filename)

        return file_location.to_dict()

    def save_content(self, file_stream: IO[bytes]):
        file_stream.seek(0)

        self.s3_client.upload_fileobj(file_stream, self.s3_url.bucket, self.s3_url.path)

    def get_file_size(self) -> int:
        response = self.s3_client.head_object(self.s3_url.bucket, self.s3_url.path)
        size = response["ContentLength"]

        return size

    def get_file_url(self) -> str:
        file_url = self.s3_client.generate_presigned_url(
            self.s3_url.bucket,
            self.s3_url.path,
            self.s3_presigned_url_expiration,
        )

        return file_url

    def get_file_upload_post_data(
        self, filename: str, max_file_size_bytes: Optional[int] = None
    ) -> dict:
        conditions = []

        if max_file_size_bytes:
            conditions.append(["content-length-range", 0, max_file_size_bytes])

        file_upload_url = self.s3_client.generate_presigned_post(
            self.s3_url.bucket,
            os.path.join(self.s3_url.path, filename),
            self.s3_presigned_url_expiration,
            conditions,
        )

        return file_upload_url

    def does_file_exist(self) -> bool:
        try:
            self.s3_client.head_object(self.s3_url.bucket, self.s3_url.path)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise e
