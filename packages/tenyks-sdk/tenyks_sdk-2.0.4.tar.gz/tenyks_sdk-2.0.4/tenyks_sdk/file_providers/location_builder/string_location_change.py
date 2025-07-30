import os


class StringLocationChange:
    @staticmethod
    def folder_up(path: str) -> str:
        folder_path = os.path.dirname(path)
        chunked = folder_path.split("/")
        if len(chunked) < 3:
            return path

        without_folder = "/".join(chunked[:-1])
        combined = without_folder + "/"

        return combined

    @staticmethod
    def go_to_folder(path: str, folder_name: str) -> str:
        combined_path = os.path.join(path, folder_name, "")

        return combined_path

    @staticmethod
    def add_file_to_path(path: str, filename: str) -> str:
        just_folder = StringLocationChange.remove_file_from_path(path)

        combined_path = os.path.join(just_folder, filename)
        return combined_path

    @staticmethod
    def remove_file_from_path(path: str) -> str:
        if path.endswith("/"):
            return path

        all_but_last_chunk = path.split("/")[:-1]
        without_file = "/".join(all_but_last_chunk)
        result = os.path.join(without_file, "")

        return result
