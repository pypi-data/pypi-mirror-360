import os
from typing import Dict

from tenyks_sdk.file_providers.aws.boto_s3_client_factory import Boto3S3ClientFactory
from tenyks_sdk.file_providers.aws.data_classes import AWSVideoLocation
from tenyks_sdk.file_providers.aws.s3_client import S3Client
from tenyks_sdk.file_providers.aws.s3_url_parser import S3Url, S3UrlParser
from tenyks_sdk.file_providers.config import S3_PRESIGNED_URL_EXPIRATION


class AWSVideoFileProvider:
    def __init__(
        self,
        video_location: Dict[str, object],
        s3_presigned_url_expiration: int = S3_PRESIGNED_URL_EXPIRATION,
    ) -> None:
        self.video_location: AWSVideoLocation = AWSVideoLocation.from_dict(
            video_location
        )
        self.s3_client: S3Client = Boto3S3ClientFactory.create_client(
            self.video_location.credentials
        )
        self.s3_url: S3Url = S3UrlParser(self.video_location.s3_uri).parse()
        self.s3_presigned_url_expiration = s3_presigned_url_expiration

    def download_video_from_s3(self, local_output_directory: str):
        contents = self.s3_client.list_objects_v2(self.s3_url.bucket, self.s3_url.path)

        os.makedirs(local_output_directory, exist_ok=True)

        for file in contents:
            object_key = file["Key"]
            file_path = os.path.join(
                local_output_directory, os.path.basename(object_key)
            )

            self.s3_client.boto3_s3_client.download_file(
                self.s3_url.bucket, object_key, file_path
            )
