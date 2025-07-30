import os
from enum import Enum


class StorageLocationType(str, Enum):
    AWS_S3 = "aws_s3"
    GCS = "gcs"
    AZURE = "azure"


class FileSelectorType(str, Enum):
    LIST = "list"
    FILE = "file"
    FOLDER = "folder"


PREDICTIONS_FILE = "predictions"
IMAGES_THUMBNAILS_PATH = "thumbnails"
IMAGE_TYPES = [".jpg", ".png", ".jpeg"]
STATIC_RESOURCES_ENCRYPTION_KEY = "TENYKS_STATIC_RESOURCES"
S3_PRESIGNED_URL_EXPIRATION = os.environ.get("S3_PRESIGNED_URL_EXPIRATION", 604800)
GCS_SIGNED_URL_EXPIRATION_SECONDS = os.environ.get(
    "GCS_SIGNED_URL_EXPIRATION_SECONDS", 604800
)
AZURE_SIGNED_URL_EXPIRATION_SECONDS = os.environ.get(
    "AZURE_SIGNED_URL_EXPIRATION_SECONDS", 604800
)
