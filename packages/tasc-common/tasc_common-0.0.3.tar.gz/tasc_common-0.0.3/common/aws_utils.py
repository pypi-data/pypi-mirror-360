import aioboto3
import boto3
import os
from typing import Optional

class AWSClients:
    _session: Optional[boto3.Session] = None
    _secrets_client: Optional[boto3.client] = None
    _s3_client: Optional[aioboto3.Session] = None
    
    @classmethod
    def get_session(cls) -> boto3.Session:
        if cls._session is None:
            cls._session = boto3.session.Session(
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
                region_name=os.environ.get('AWS_REGION', 'us-west-2')
            )
        return cls._session
    
    @classmethod
    def get_secrets_client(cls) -> boto3.client:
        if cls._secrets_client is None:
            cls._secrets_client = cls.get_session().client('secretsmanager')
        return cls._secrets_client
    
    @classmethod
    def get_s3_client(cls):
        """Returns an async context manager for S3 operations"""
        return aioboto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-west-2')
        ).client('s3')
    
    @classmethod
    def update_secret(cls, secret_name: str, secret_value: str) -> dict:
        """Update or create a secret in AWS Secrets Manager"""
        client = cls.get_secrets_client()
        try:
            return client.update_secret(
                SecretId=secret_name,
                SecretString=secret_value
            )
        except client.exceptions.ResourceNotFoundException:
            return client.create_secret(
                Name=secret_name,
                SecretString=secret_value
            ) 