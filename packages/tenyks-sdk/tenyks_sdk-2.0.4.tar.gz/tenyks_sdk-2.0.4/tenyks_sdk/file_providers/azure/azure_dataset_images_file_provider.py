import logging
import os
from typing import List

from PIL import Image
from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.azure.azure_client_factory import AzureBlobClientFactory
from tenyks_sdk.file_providers.azure.azure_url_parser import AzureBlobUrlParser
from tenyks_sdk.file_providers.azure.data_classes import AzureLocation
from tenyks_sdk.file_providers.config import (
    AZURE_SIGNED_URL_EXPIRATION_SECONDS,
    IMAGE_TYPES,
)
from tenyks_sdk.file_providers.dataset_images_file_provider import (
    DatasetImagesFileProvider,
)
from tenyks_sdk.file_providers.selectors.file_selector_pipeline_factory import (
    FileSelectorPipelineFactory,
)


class AzureDatasetImagesFileProvider(DatasetImagesFileProvider):
    def __init__(
        self,
        images_location: dict,
        signed_url_expiration_seconds: int = AZURE_SIGNED_URL_EXPIRATION_SECONDS,
        cache: bool = False,
    ) -> None:
        self.images_location: AzureLocation = AzureLocation.from_dict(images_location)
        if cache:
            self.client = AzureBlobClientFactory.create_client_with_cache(
                self.images_location.credentials
            )
        else:
            self.client = AzureBlobClientFactory.create_client(
                self.images_location.credentials
            )
        self.azure_blob_location = AzureBlobUrlParser(
            self.images_location.azure_uri
        ).parse()
        self.signed_url_expiration_seconds = signed_url_expiration_seconds
        self.selector_pipeline = FileSelectorPipelineFactory.create_from_definitions(
            self.images_location.selectors
        )

    def get_image(self, relative_image_path: str) -> Image:
        full_path = self.__get_dataset_full_path(relative_image_path)
        stream = self.client.get_blob_stream(
            self.azure_blob_location.container, full_path
        )
        image = Image.open(stream)

        return image

    def get_image_url(self, relative_image_path: str) -> str:
        full_path = self.__get_dataset_full_path(relative_image_path)
        url = self.client.generate_url(
            self.azure_blob_location.container,
            full_path,
            self.signed_url_expiration_seconds,
        )

        return url

    def get_images_dir_files_relative_paths(self) -> List[str]:
        file_paths_only = self.client.list_files(
            self.azure_blob_location.container, self.azure_blob_location.blob
        )

        # Remove non-relevant parent-folders
        relative_paths_only = [
            file_path.replace(self.azure_blob_location.blob, "")
            for file_path in file_paths_only
        ]

        image_files = list(
            filter(
                lambda filename: (os.path.splitext(filename)[1].lower() in IMAGE_TYPES),
                relative_paths_only,
            )
        )

        matching_selectors = [
            image_file
            for image_file in image_files
            if self.selector_pipeline.is_accepted_path(image_file)
        ]

        return matching_selectors

    def delete_dataset_image_dir(self) -> None:
        # we don't delete user images
        logging.warn(
            f"Attempted to delete Azure-hosted {self.__get_dataset_full_path()}. Ignoring."
        )
        pass

    def __get_dataset_full_path(self, relative_image_path: str = "") -> str:
        relative_image_path = relative_image_path.lstrip("/")
        full_path = os.path.join(self.azure_blob_location.blob, relative_image_path)
        return full_path

    def save_file(
        self, file_storage: FileStorage, relative_destination_folder: str
    ) -> str:
        file_storage.stream.seek(0)
        self.client.save_file(
            self.azure_blob_location.container,
            os.path.join(self.azure_blob_location.blob, file_storage.filename),
            file_storage.stream,
        )

        file_metadata_location: AzureLocation = AzureLocation.from_dict(
            self.images_location.to_dict()
        )

        file_metadata_location.azure_uri = os.path.join(
            file_metadata_location.azure_uri,
            relative_destination_folder,
            file_storage.filename,
        )

    def save_image(self, source_image_path: str, file_name: str):
        pass
