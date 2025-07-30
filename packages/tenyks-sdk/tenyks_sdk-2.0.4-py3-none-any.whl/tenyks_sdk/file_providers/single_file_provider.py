from abc import ABC, abstractmethod
from typing import IO, Dict, Optional

from werkzeug.datastructures import FileStorage


class SingleFileProvider(ABC):
    @abstractmethod
    def get_file(self) -> FileStorage:
        raise NotImplementedError

    @abstractmethod
    def save_file(self, file_storage: FileStorage) -> Dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def save_content(self, file_stream: IO[bytes]):
        raise NotImplementedError

    @abstractmethod
    def get_file_size(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def get_file_url(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_file_upload_post_data(
        self, filename: str, max_file_size_bytes: Optional[int] = None
    ) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def does_file_exist(self) -> bool:
        raise NotImplementedError()
