import logging
import os
from io import BytesIO
from typing import List

from PIL import Image
from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.config import (
    GCS_SIGNED_URL_EXPIRATION_SECONDS,
    IMAGE_TYPES,
)
from tenyks_sdk.file_providers.dataset_images_file_provider import (
    DatasetImagesFileProvider,
)
from tenyks_sdk.file_providers.gcs.data_classes import GCSLocation
from tenyks_sdk.file_providers.gcs.gcs_client import GCSClient
from tenyks_sdk.file_providers.gcs.gcs_url_parser import GCSUrlParser
from tenyks_sdk.file_providers.selectors.file_selector_pipeline_factory import (
    FileSelectorPipelineFactory,
)


class GCSDatasetImagesFileProvider(DatasetImagesFileProvider):
    def __init__(
        self,
        images_location: dict,
        client=GCSClient,
        signed_url_expiration_seconds: int = GCS_SIGNED_URL_EXPIRATION_SECONDS,
    ) -> None:
        self.images_location: GCSLocation = GCSLocation.from_dict(images_location)
        self.client = client
        self.gcs_location = GCSUrlParser.parse_gcs_url(self.images_location.gcs_uri)
        self.signed_url_expiration_seconds = signed_url_expiration_seconds
        self.selector_pipeline = FileSelectorPipelineFactory.create_from_definitions(
            self.images_location.selectors
        )

    def __get_dataset_relative_path(self, relative_image_path: str = "") -> str:
        full_path = os.path.join(self.gcs_location.path, relative_image_path)
        return full_path

    def get_image(self, relative_image_path: str) -> Image:
        full_path = self.__get_dataset_relative_path(relative_image_path)
        blob = self.client.get_blob(self.gcs_location.bucket, full_path)
        blob_bytes = BytesIO(blob.download_as_bytes())
        image = Image.open(blob_bytes)

        return image

    def get_image_url(self, relative_image_path: str) -> str:
        full_path = self.__get_dataset_relative_path(relative_image_path)
        url = self.client.generate_url(
            self.gcs_location.bucket, full_path, self.signed_url_expiration_seconds
        )

        return url

    def get_images_dir_files_relative_paths(self) -> List[str]:
        file_paths_only = self.client.list_files(
            self.gcs_location.bucket, self.gcs_location.path
        )

        # Remove non-relevant parent-folders
        relative_paths_only = [
            file_path.replace(self.gcs_location.path, "")
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
            f"Attempted to delete GCS-hosted {self.__get_dataset_relative_path()}. Ignoring."
        )
        pass

    def save_file(
        self, file_storage: FileStorage, relative_destination_folder: str
    ) -> str:
        # not touching user data
        pass

    def save_image(self, source_image_path: str, file_name: str):
        pass
