import os
from io import BytesIO
from typing import IO, Dict, Optional

from werkzeug.datastructures import FileStorage

from tenyks_sdk.file_providers.config import GCS_SIGNED_URL_EXPIRATION_SECONDS
from tenyks_sdk.file_providers.gcs.data_classes import GCSLocation
from tenyks_sdk.file_providers.gcs.gcs_client import GCSClient
from tenyks_sdk.file_providers.gcs.gcs_url_parser import GCSUrlParser
from tenyks_sdk.file_providers.single_file_provider import SingleFileProvider


class GCSSingleFileProvider(SingleFileProvider):
    def __init__(
        self,
        metadata_location: GCSLocation,
        client: GCSClient,
        signed_url_expiration_seconds: int = GCS_SIGNED_URL_EXPIRATION_SECONDS,
    ) -> None:
        self.metadata_location: GCSLocation = GCSLocation.from_dict(metadata_location)
        self.client = client
        self.signed_url_expiration_seconds = signed_url_expiration_seconds
        self.gcs_location = GCSUrlParser.parse_gcs_url(self.metadata_location.gcs_uri)

    def get_file(self) -> FileStorage:
        blob = self.client.get_blob(self.gcs_location.bucket, self.gcs_location.path)
        blob_bytes = BytesIO(blob.download_as_bytes())
        file = FileStorage(
            blob_bytes, filename=os.path.basename(self.gcs_location.path)
        )
        return file

    def save_file(self, file_storage: FileStorage) -> Dict[str, object]:
        file_storage.stream.seek(0)
        self.client.save_file(
            self.gcs_location.bucket,
            os.path.join(self.gcs_location.path, file_storage.filename),
            file_storage.stream,
        )

        file_metadata_location: GCSLocation = GCSLocation.from_dict(
            self.metadata_location.to_dict()
        )

        file_metadata_location.gcs_uri = os.path.join(
            file_metadata_location.gcs_uri, file_storage.filename
        )

        return file_metadata_location.to_dict()

    def save_content(self, file_stream: IO[bytes]):
        file_stream.seek(0)

        self.client.save_file(
            self.gcs_location.bucket, self.gcs_location.path, file_stream
        )

    def get_file_size(self) -> int:
        blob = self.client.get_blob(self.gcs_location.bucket, self.gcs_location.path)
        return blob.size

    def get_file_url(self) -> str:
        file_url = self.client.generate_url(
            self.gcs_location.bucket,
            self.gcs_location.path,
            self.signed_url_expiration_seconds,
        )
        return file_url

    def does_file_exist(self) -> bool:
        exists = self.client.does_file_exist(
            self.gcs_location.bucket, self.gcs_location.path
        )

        return exists

    def get_file_upload_post_data(
        self, filename: str, max_file_size_bytes: Optional[int] = None
    ) -> dict:
        pass
