from abc import ABC, abstractmethod


class FileSelectorInterface(ABC):
    @abstractmethod
    def is_accepted_path(self, relative_path: str) -> bool:
        pass
