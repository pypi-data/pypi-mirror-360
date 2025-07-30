from typing import IO, Dict, List, Type, TypeVar
from tenyks_sdk.file_providers.directory_provider_factory import (
    DirectoryProviderFactory,
)

T = TypeVar("T")


class JsonlDirectoryReader:

    def __init__(self, location: Dict, deserialize_into: Type[T]) -> None:
        self.directory_provider = DirectoryProviderFactory.get_provider(location)
        self.filenames = self.directory_provider.list_files()
        self.deserialize_into = deserialize_into

    def get_all(self) -> List[T]:
        all_files_content = []
        for filename in self.filenames:
            file = self.directory_provider.get_file(filename)
            lines = self.__read_stream_and_deserialize(file.stream)
            all_files_content.extend(lines)

        return all_files_content

    def get_all_batched(self) -> List[List[T]]:
        all_files_content = []
        for filename in self.filenames:
            file = self.directory_provider.get_file(filename)
            lines = self.__read_stream_and_deserialize(file.stream)

            all_files_content.append(lines)

        return all_files_content

    def __read_stream_and_deserialize(self, stream: IO[bytes]) -> List[T]:
        file_content = ""
        for chunk in stream:
            file_content = file_content + chunk.decode("utf-8")

        lines = file_content.strip().split("\n")
        deserialized = [self.deserialize_into.from_json(record) for record in lines]
        return deserialized
