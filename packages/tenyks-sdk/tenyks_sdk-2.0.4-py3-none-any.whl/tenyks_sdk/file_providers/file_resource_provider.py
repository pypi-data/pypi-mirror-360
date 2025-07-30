from abc import ABC
from typing import List

from werkzeug.datastructures import FileStorage


class FileResourceProvider(ABC):
    def get_file(self, relative_path: str) -> FileStorage:
        pass

    def save_file(self, file_storage: FileStorage, relative_path: str) -> None:
        pass

    def get_url(self, relative_path: str = "") -> str:
        pass

    def list_files_relative_paths(self, relative_path: str = "") -> List[str]:
        pass
