from abc import ABC, abstractmethod
from typing import List

from werkzeug.datastructures import FileStorage


class DirectoryProvider(ABC):

    @abstractmethod
    def list_files(self, file_extensions: list = None) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def get_file(self, filename: str) -> FileStorage:
        raise NotImplementedError()

    @abstractmethod
    def save_file(self, file_storage: FileStorage) -> dict:
        # not touching user data
        raise NotImplementedError

    @abstractmethod
    def get_size(self) -> int:
        raise NotImplementedError()
