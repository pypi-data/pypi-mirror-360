from typing import Dict
from functools import lru_cache
from google.cloud.storage import Client
from tenyks_sdk.file_providers.gcs.gcs_client import GCSClient


class GCSClientFactory:
    @staticmethod
    def create_client(gcs_credentials: Dict) -> GCSClient:
        """Original method without caching for backward compatibility"""
        gcs_client = GCSClient(Client.from_service_account_info(gcs_credentials))
        return gcs_client

    @staticmethod
    @lru_cache(maxsize=32)
    def create_client_cached(gcs_credentials_tuple: tuple) -> GCSClient:
        """New method with caching for better performance"""
        gcs_credentials = dict(gcs_credentials_tuple)
        gcs_client = GCSClient(Client.from_service_account_info(gcs_credentials))
        return gcs_client

    @classmethod
    def create_client_with_cache(cls, gcs_credentials: Dict) -> GCSClient:
        """Convenience method to use cached version with a dict"""
        credentials_tuple = tuple(sorted(gcs_credentials.items()))
        return cls.create_client_cached(credentials_tuple)
