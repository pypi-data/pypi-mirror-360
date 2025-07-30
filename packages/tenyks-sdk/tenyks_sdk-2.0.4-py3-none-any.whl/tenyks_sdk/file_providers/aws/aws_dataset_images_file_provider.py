import os
from typing import Dict

from PIL import Image
from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.aws.boto_s3_client_factory import Boto3S3ClientFactory
from tenyks_sdk.file_providers.aws.data_classes import AWSLocation
from tenyks_sdk.file_providers.aws.s3_client import S3Client
from tenyks_sdk.file_providers.aws.s3_url_parser import S3Url, S3UrlParser
from tenyks_sdk.file_providers.config import IMAGE_TYPES, S3_PRESIGNED_URL_EXPIRATION
from tenyks_sdk.file_providers.dataset_images_file_provider import (
    DatasetImagesFileProvider,
)
from tenyks_sdk.file_providers.selectors.file_selector_pipeline_factory import (
    FileSelectorPipelineFactory,
)


class AWSDatasetImagesFileProvider(DatasetImagesFileProvider):
    def __init__(
        self,
        images_location: Dict[str, object],
        s3_presigned_url_expiration: int = S3_PRESIGNED_URL_EXPIRATION,
        cache: bool = False,
    ) -> None:
        self.images_location: AWSLocation = AWSLocation.from_dict(images_location)

        self.selector_pipeline = FileSelectorPipelineFactory.create_from_definitions(
            self.images_location.selectors
        )

        if cache:
            self.s3_client: S3Client = Boto3S3ClientFactory.create_client_with_cache(
                self.images_location.credentials
            )
        else:
            self.s3_client: S3Client = Boto3S3ClientFactory.create_client(
                self.images_location.credentials
            )
        self.s3_url: S3Url = S3UrlParser(self.images_location.s3_uri).parse()

        self.s3_presigned_url_expiration = s3_presigned_url_expiration

    def get_images_dir_files_relative_paths(self) -> str:
        content = self.s3_client.list_objects_v2(self.s3_url.bucket, self.s3_url.path)
        image_files = [item["Key"].replace(self.s3_url.path, "") for item in content]

        image_files = list(
            filter(
                lambda filename: (os.path.splitext(filename)[1].lower() in IMAGE_TYPES),
                image_files,
            )
        )

        image_files = [
            image_file
            for image_file in image_files
            if self.selector_pipeline.is_accepted_path(image_file)
        ]

        return image_files

    def get_image(self, relative_image_path: str) -> Image:
        image_key = self.__get_image_key(relative_image_path)
        object = self.s3_client.get_object(self.s3_url.bucket, image_key)
        image = Image.open(object["Body"])
        return image

    def save_image(self, source_image_path: str, file_name: str):
        object_key = os.path.join(self.s3_url.path, file_name)

        self.s3_client.boto3_s3_client.upload_file(
            source_image_path, self.s3_url.bucket, object_key
        )

    def get_image_url(self, image_filename) -> str:
        image_url = self.s3_client.generate_presigned_url(
            self.s3_url.bucket,
            self.__get_image_key(image_filename),
            self.s3_presigned_url_expiration,
        )

        return image_url

    def save_file(
        self, file_storage: FileStorage, relative_destination_folder: str
    ) -> str:
        if self.images_location.write_permission is True:
            file_storage.stream.seek(0)

            relative_file_path = os.path.join(
                self.s3_url.path, relative_destination_folder, file_storage.filename
            )
            self.s3_client.upload_fileobj(
                file_storage.stream, self.s3_url.bucket, relative_file_path
            )

    def delete_dataset_image_dir(self) -> None:
        if self.images_location.write_permission is True:
            files = self.s3_client.list_objects_v2(self.s3_url.bucket, self.s3_url.path)

            if len(files) > 0:
                objects = list(map(lambda x: {"Key": x["Key"]}, files))
                self.s3_client.delete_objects(self.s3_url.bucket, objects)

    def __get_image_key(self, relative_image_path):
        image_key = f"{self.s3_url.path}{relative_image_path}"
        return image_key
