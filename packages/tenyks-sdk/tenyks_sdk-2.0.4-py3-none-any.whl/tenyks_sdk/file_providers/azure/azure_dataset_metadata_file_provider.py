import os
from io import BytesIO
from typing import List

from PIL import Image
from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.azure.azure_client import AzureBlobClient
from tenyks_sdk.file_providers.azure.azure_url_parser import (
    AzureBlobUrl,
    AzureBlobUrlParser,
)
from tenyks_sdk.file_providers.azure.data_classes import AzureLocation
from tenyks_sdk.file_providers.config import (
    AZURE_SIGNED_URL_EXPIRATION_SECONDS,
    IMAGES_THUMBNAILS_PATH,
)
from tenyks_sdk.file_providers.dataset_metadata_file_provider import (
    DatasetMetadataFileProvider,
)


class AzureDatasetMetadataFileProvider(DatasetMetadataFileProvider):
    def __init__(
        self,
        metadata_location: dict,
        signed_url_expiration_seconds: int = AZURE_SIGNED_URL_EXPIRATION_SECONDS,
    ) -> None:
        self.azure_location: AzureLocation = AzureLocation.from_dict(metadata_location)
        self.azure_blob_client = AzureBlobClient(self.azure_location.credentials)
        self.signed_url_expiration_seconds = signed_url_expiration_seconds
        self.azure_blob_url: AzureBlobUrl = AzureBlobUrlParser(
            self.azure_location.azure_uri
        ).parse()
        self.container_name = self.azure_blob_url.container
        self.metadata_path = self.azure_blob_url.blob

    def get_thumbnail_image_url(self, original_image_relative_filename: str) -> str:
        thumbnail_path = self.__get_thumbnail_path(original_image_relative_filename)
        url = self.azure_blob_client.generate_url(
            self.container_name, thumbnail_path, self.signed_url_expiration_seconds
        )
        return url

    def get_predictions_file(self, model_key: str) -> FileStorage:
        path = self.__get_predictions_file_path(model_key)
        stream = self.azure_blob_client.get_blob_stream(self.container_name, path)
        return FileStorage(stream=stream, filename=self.PREDICTIONS_FILE_NAME)

    def save_thumbnail(self, image: Image, original_image_relative_path: str):
        file_stream = BytesIO()
        image.save(file_stream, format=image.format)
        file_stream.seek(0)
        self.azure_blob_client.save_file(
            self.container_name,
            self.__get_thumbnail_path(original_image_relative_path),
            file_stream,
        )

    def save_predictions_file(self, file: FileStorage, model_key: str):
        file.stream.seek(0)
        self.azure_blob_client.save_file(
            self.container_name,
            self.__get_predictions_file_path(model_key),
            file.stream,
        )

    def delete_dataset_metadata_dir(self) -> None:
        self.azure_blob_client.delete_by_prefix(self.container_name, self.metadata_path)

    def delete_model_metadata_dir(self, model_key) -> None:
        model_path = self.__get_model_folder_path(model_key)
        self.azure_blob_client.delete_by_prefix(self.container_name, model_path)

    def delete_thumbnails(self, original_image_relative_paths: List[str]):
        for image_relative_path in original_image_relative_paths:
            self.azure_blob_client.delete_file(
                self.container_name, self.__get_thumbnail_path(image_relative_path)
            )

    def __get_predictions_file_path(self, model_key: str) -> str:
        model_folder = self.__get_model_folder_path(model_key)
        return os.path.join(model_folder, self.PREDICTIONS_FILE_NAME)

    def __get_model_folder_path(self, model_key: str) -> str:
        return os.path.join(self.metadata_path, self.MODELS_FOLDER, model_key)

    def __get_thumbnail_path(self, image_relative_path: str = "") -> str:
        image_relative_path = image_relative_path.lstrip("/")
        return os.path.join(
            self.metadata_path, IMAGES_THUMBNAILS_PATH, image_relative_path
        )

    def check_empty_metadata_dir(self) -> bool:
        prefix = self.metadata_path
        if not prefix.endswith("/"):
            prefix += "/"

        objects = self.azure_blob_client.list_files(
            self.container_name, self.metadata_path
        )
        return len(objects) == 0
