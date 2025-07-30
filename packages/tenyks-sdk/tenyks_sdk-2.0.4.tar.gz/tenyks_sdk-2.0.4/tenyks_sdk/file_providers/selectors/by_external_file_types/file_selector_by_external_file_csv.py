import csv
import io

from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.selectors.file_selector_interface import (
    FileSelectorInterface,
)


class FileSelectorByExternalTypeCsv(FileSelectorInterface):
    def __init__(self, csv_file: FileStorage) -> None:
        self.list_of_keys = []
        text_stream = io.TextIOWrapper(csv_file.stream, encoding="utf-8")

        reader = csv.reader(text_stream)
        for row in reader:
            self.list_of_keys.append(row[0])

    def is_accepted_path(self, relative_path: str) -> bool:
        is_accepted = relative_path in self.list_of_keys

        return is_accepted
