import os
from io import BytesIO
from typing import List

from PIL import Image
from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.config import (
    GCS_SIGNED_URL_EXPIRATION_SECONDS,
    IMAGES_THUMBNAILS_PATH,
)
from tenyks_sdk.file_providers.dataset_metadata_file_provider import (
    DatasetMetadataFileProvider,
)
from tenyks_sdk.file_providers.gcs.data_classes import GCSLocation
from tenyks_sdk.file_providers.gcs.gcs_client_factory import GCSClientFactory
from tenyks_sdk.file_providers.gcs.gcs_url_parser import GCSUrlParser


class GCSDatasetMetadataFileProvider(DatasetMetadataFileProvider):
    def __init__(
        self,
        metadata_location: dict,
        signed_url_expiration_seconds: int = GCS_SIGNED_URL_EXPIRATION_SECONDS,
    ) -> None:
        self.metadata_location: GCSLocation = GCSLocation.from_dict(metadata_location)
        self.client = GCSClientFactory.create_client(self.metadata_location.credentials)
        self.gcs_location = GCSUrlParser.parse_gcs_url(self.metadata_location.gcs_uri)
        self.signed_url_expiration_seconds = signed_url_expiration_seconds

    def get_thumbnail_image_url(self, original_image_relative_filename: str) -> str:
        thumbnail_path = self.__get_thumbnail_path(original_image_relative_filename)
        url = self.client.generate_url(
            self.gcs_location.bucket, thumbnail_path, self.signed_url_expiration_seconds
        )
        return url

    def get_predictions_file(self, model_key: str) -> FileStorage:
        path = self.__get_predictions_file_path(model_key)
        blob = self.client.get_blob(self.gcs_location.bucket, path)
        blob_bytes = BytesIO(blob.download_as_bytes())
        file = FileStorage(blob_bytes, filename=self.PREDICTIONS_FILE_NAME)
        return file

    def save_thumbnail(self, image: Image, original_image_relative_path: str):
        file_stream = BytesIO()
        image.save(file_stream, format=image.format)
        file_stream.seek(0)
        self.client.save_file(
            self.gcs_location.bucket,
            self.__get_thumbnail_path(original_image_relative_path),
            file_stream,
        )

    def save_predictions_file(self, file: FileStorage, model_key: str):
        file.stream.seek(0)
        self.client.save_file(
            self.gcs_location.bucket,
            self.__get_predictions_file_path(model_key),
            file.stream,
        )

    def delete_dataset_metadata_dir(self) -> None:
        self.client.delete_by_prefix(self.gcs_location.bucket, self.gcs_location.path)

    def delete_model_metadata_dir(self, model_key) -> None:
        model_path = self.__get_model_folder_path(model_key)
        self.client.delete_by_prefix(self.gcs_location.bucket, model_path)

    def delete_thumbnails(self, original_image_relative_paths: List[str]):
        for current_image_relative_path in original_image_relative_paths:
            self.client.delete_file(
                self.gcs_location.bucket,
                self.__get_thumbnail_path(current_image_relative_path),
            )

    def __get_predictions_file_path(self, model_key: str) -> str:
        model_folder = self.__get_model_folder_path(model_key)
        return os.path.join(model_folder, self.PREDICTIONS_FILE_NAME)

    def __get_model_folder_path(self, model_key: str) -> str:
        return os.path.join(self.gcs_location.path, self.MODELS_FOLDER, model_key)

    def __get_thumbnail_path(self, image_relative_path: str = "") -> str:
        file_path = os.path.join(
            self.gcs_location.path, IMAGES_THUMBNAILS_PATH, image_relative_path
        )

        return file_path

    def check_empty_metadata_dir(self) -> bool:
        prefix = self.gcs_location.path
        if not prefix.endswith("/"):
            prefix += "/"

        objects = self.client.list_files(self.gcs_location.bucket, prefix)
        return len(objects) == 0
