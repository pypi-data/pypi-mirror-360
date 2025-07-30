from abc import ABC, abstractmethod
from typing import List

from PIL import Image
from werkzeug.datastructures import FileStorage


class DatasetImagesFileProvider(ABC):
    @abstractmethod
    def get_images_dir_files_relative_paths(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def get_image(self, relative_image_path: str) -> Image:
        raise NotImplementedError

    @abstractmethod
    def save_image(self, source_image_path: str, file_name: str):
        raise NotImplementedError

    @abstractmethod
    def get_image_url(self, image_filename) -> str:
        raise NotImplementedError

    @abstractmethod
    def save_file(
        self, file_storage: FileStorage, relative_destination_folder: str
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def delete_dataset_image_dir(self) -> None:
        raise NotImplementedError
