from abc import ABC, abstractmethod
from typing import List

from PIL import Image
from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.config import PREDICTIONS_FILE


class DatasetMetadataFileProvider(ABC):
    PREDICTIONS_FILE_NAME = f"{PREDICTIONS_FILE}.json"
    MODELS_FOLDER = "models"

    @abstractmethod
    def get_thumbnail_image_url(self, original_image_relative_filename: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_predictions_file(self, model_key: str) -> FileStorage:
        raise NotImplementedError

    @abstractmethod
    def save_thumbnail(self, image: Image, original_image_relative_path: str):
        raise NotImplementedError

    @abstractmethod
    def delete_thumbnails(self, original_image_relative_paths: List[str]):
        raise NotImplementedError

    @abstractmethod
    def save_predictions_file(self, file_storage: FileStorage, model_key: str):
        raise NotImplementedError

    @abstractmethod
    def delete_dataset_metadata_dir(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_model_metadata_dir(self, model_key) -> None:
        raise NotImplementedError

    @abstractmethod
    def check_empty_metadata_dir(self) -> bool:
        raise NotImplementedError
