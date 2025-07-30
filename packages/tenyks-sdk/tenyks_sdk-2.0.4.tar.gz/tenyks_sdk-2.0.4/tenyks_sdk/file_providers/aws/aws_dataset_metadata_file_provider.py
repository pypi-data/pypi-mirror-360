import os
from io import BytesIO
from typing import Dict, List

from PIL import Image
from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.aws.boto_s3_client_factory import Boto3S3ClientFactory
from tenyks_sdk.file_providers.aws.data_classes import AWSLocation
from tenyks_sdk.file_providers.aws.s3_client import S3Client
from tenyks_sdk.file_providers.aws.s3_url_parser import S3Url, S3UrlParser
from tenyks_sdk.file_providers.config import (
    IMAGES_THUMBNAILS_PATH,
    S3_PRESIGNED_URL_EXPIRATION,
)
from tenyks_sdk.file_providers.dataset_metadata_file_provider import (
    DatasetMetadataFileProvider,
)


class AWSDatasetMetadataFileProvider(DatasetMetadataFileProvider):
    def __init__(
        self,
        metadata_location: Dict[str, object],
        s3_presigned_url_expiration: int = S3_PRESIGNED_URL_EXPIRATION,
    ) -> None:
        self.metadata_location: AWSLocation = AWSLocation.from_dict(metadata_location)
        self.s3_client: S3Client = Boto3S3ClientFactory.create_client(
            self.metadata_location.credentials
        )
        self.s3_url: S3Url = S3UrlParser(self.metadata_location.s3_uri).parse()

        self.s3_presigned_url_expiration = s3_presigned_url_expiration

    def get_thumbnail_image_url(self, original_image_relative_filename: str) -> str:
        thumbnail_url = self.s3_client.generate_presigned_url(
            self.s3_url.bucket,
            self.__get_thumbnail_image_key(original_image_relative_filename),
            self.s3_presigned_url_expiration,
        )

        return thumbnail_url

    def get_predictions_file(self, model_key: str) -> FileStorage:
        response = self.s3_client.get_object(
            self.s3_url.bucket, self.__get_predictions_file_path(model_key)
        )
        file_stream = response["Body"]
        file_storage = FileStorage(
            stream=file_stream, filename=self.PREDICTIONS_FILE_NAME
        )

        return file_storage

    def save_thumbnail(self, image: Image, original_image_relative_path: str):
        file_stream = BytesIO()
        image.save(file_stream, format=image.format)
        file_stream.seek(0)
        self.s3_client.upload_fileobj(
            file_stream,
            self.s3_url.bucket,
            self.__get_thumbnail_image_key(original_image_relative_path),
        )

    def save_predictions_file(self, file_storage: FileStorage, model_key: str):
        file_storage.stream.seek(0)

        self.s3_client.upload_fileobj(
            file_storage.stream,
            self.s3_url.bucket,
            self.__get_predictions_file_path(model_key),
        )

    def delete_dataset_metadata_dir(self) -> None:
        folder_prefix = self.s3_url.path
        self.__delete_s3_objects(folder_prefix)

    def delete_model_metadata_dir(self, model_key) -> None:
        model_path = self.__get_model_folder_path(model_key)
        self.__delete_s3_objects(model_path)

    def delete_thumbnails(self, original_image_relative_paths: List[str]):
        if len(original_image_relative_paths) > 0:
            thumbnail_urls = [
                self.__get_thumbnail_image_key(x) for x in original_image_relative_paths
            ]
            objects = [{"Key": x} for x in thumbnail_urls]
            self.s3_client.delete_objects(self.s3_url.bucket, objects)

    def __get_thumbnail_image_key(self, relative_image_path):
        image_key = os.path.join(
            self.s3_url.path, IMAGES_THUMBNAILS_PATH, relative_image_path
        )
        return image_key

    def __get_predictions_file_path(self, model_key: str) -> str:
        file_path = os.path.join(
            self.__get_model_folder_path(model_key), self.PREDICTIONS_FILE_NAME
        )
        return file_path

    def __get_model_folder_path(self, model_key: str) -> str:
        return os.path.join(self.s3_url.path, self.MODELS_FOLDER, model_key)

    def __delete_s3_objects(self, folder_prefix):
        responses = self.s3_client.list_objects_v2(self.s3_url.bucket, folder_prefix)

        if len(responses) > 0:
            objects = list(map(lambda x: {"Key": x["Key"]}, responses))
            self.s3_client.delete_objects(self.s3_url.bucket, objects)

    def check_empty_metadata_dir(self) -> bool:
        prefix = self.s3_url.path
        if not prefix.endswith("/"):
            prefix += "/"

        objects = self.s3_client.list_objects_v2(self.s3_url.bucket, prefix)
        return len(objects) == 0
