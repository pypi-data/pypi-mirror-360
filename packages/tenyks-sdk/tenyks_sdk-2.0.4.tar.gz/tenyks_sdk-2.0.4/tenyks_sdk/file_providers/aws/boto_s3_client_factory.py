from functools import lru_cache

import boto3
from botocore.config import Config

from tenyks_sdk.file_providers.aws.data_classes import AWSS3Credentials
from tenyks_sdk.file_providers.aws.s3_client import S3Client


class Boto3S3ClientFactory:
    # Configure boto3 client for optimal performance
    _boto_config = Config(
        retries={"max_attempts": 2},  # Minimal retries
        parameter_validation=False,  # Skip parameter validation
    )

    @staticmethod
    def create_client(aws_s3_credentials: AWSS3Credentials) -> S3Client:
        """Original method without caching for backward compatibility"""
        if aws_s3_credentials.aws_session_token is not None:
            client = boto3.client(
                "s3",
                aws_access_key_id=aws_s3_credentials.aws_access_key_id,
                aws_secret_access_key=aws_s3_credentials.aws_secret_access_key,
                aws_session_token=aws_s3_credentials.aws_session_token,
                region_name=aws_s3_credentials.region_name,
                config=Boto3S3ClientFactory._boto_config,
            )
        else:
            client = boto3.client(
                "s3",
                aws_access_key_id=aws_s3_credentials.aws_access_key_id,
                aws_secret_access_key=aws_s3_credentials.aws_secret_access_key,
                region_name=aws_s3_credentials.region_name,
                config=Boto3S3ClientFactory._boto_config,
            )

        return S3Client(client)

    @staticmethod
    @lru_cache(maxsize=32)
    def create_client_with_cache(aws_s3_credentials: AWSS3Credentials) -> S3Client:
        """New method with caching for better performance"""
        if aws_s3_credentials.aws_session_token is not None:
            client = boto3.client(
                "s3",
                aws_access_key_id=aws_s3_credentials.aws_access_key_id,
                aws_secret_access_key=aws_s3_credentials.aws_secret_access_key,
                aws_session_token=aws_s3_credentials.aws_session_token,
                region_name=aws_s3_credentials.region_name,
                config=Boto3S3ClientFactory._boto_config,
            )
        else:
            client = boto3.client(
                "s3",
                aws_access_key_id=aws_s3_credentials.aws_access_key_id,
                aws_secret_access_key=aws_s3_credentials.aws_secret_access_key,
                region_name=aws_s3_credentials.region_name,
                config=Boto3S3ClientFactory._boto_config,
            )

        return S3Client(client)
