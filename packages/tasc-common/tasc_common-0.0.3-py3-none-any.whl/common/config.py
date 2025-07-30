import secrets
from typing import Dict, Literal, Optional
import os

from pydantic import (
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml

from common.database.utils import build_database_url
from common.services import ServiceRegistry
from common.aws_utils import AWSClients
from loguru import logger


class SecretsManagerMixin:
    @classmethod
    def get_secrets(cls, secret_name: str) -> Dict:
        """Get secrets from AWS Secrets Manager"""
        try:
            client = AWSClients.get_secrets_client()
            response = client.get_secret_value(SecretId=secret_name)
            secrets = yaml.safe_load(response["SecretString"])
            return secrets
        except Exception as e:
            logger.error(
                f"Failed to fetch secrets: {str(e)}, secret_name: {secret_name}"
            )
            raise


class CommonSettings(BaseSettings, SecretsManagerMixin):
    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        extra="ignore",
    )

    # Core settings
    SERVICE_NAME: str | None = None
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENVIRONMENT: str = "local"
    PROMPT_DIR: str = "prompts"
    DOMAIN: str = "localhost"
    ROOT_DIRECTORY: str | None = None
    PROTOCOL_NAME: str = "tiptree"
    # --- should look like: service:actx-server.xxxxxx:tasx-runner.yyyyy:tasx-provider.zzzzz:...
    SERVICE_KEYS: str | None = None
    SERVICE_KEY_PREFIX: str = "service:"

    # API settings
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"

    # Auth
    ENABLE_AUTH: bool = True
    ACCESS_TOKEN_HEADER: str = "Authorization"
    SERVICE_KEY_HEADER: str = "X-TASC-Service-Key"
    SERVICE_TYPE_HEADER: str = "X-TASC-Service-Type"
    RUNNER_CALLBACK_TOKEN_HEADER: str = "X-Tasx-Runner-Callback-Token"

    # Postgres
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_ASYNC: bool = True

    # Elasticsearch
    ELASTICSEARCH_SERVER: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200

    # Redis
    REDIS_URL: str | None = None

    # Filestore settings
    FILESTORE_TYPE: Literal["s3", "local"] = "local"
    FILESTORE_ROOT: str = "file:///tmp/tasc-filestore"

    # Cloudfront settings
    CLOUDFRONT_DOMAIN: str | None = None
    CLOUDFRONT_KEY_ID: str | None = None
    CLOUDFRONT_PRIVATE_KEY: str | None = None

    # Model Settings
    DEFAULT_FLAGSHIP_MODEL: str = "claude-3-5-sonnet-20241022"
    DEFAULT_FLAGSHIP_VISION_MODEL: str = "claude-3-5-sonnet-20241022"
    DEFAULT_FAST_LONG_CONTEXT_MODEL: str = "groq/meta-llama/llama-4-scout-17b-16e-instruct"
    DEFAULT_FAST_REASONING_MODEL: str = "groq/qwen-qwq-32b"
    DEFAULT_CHEAP_MODEL: str = "gpt-4o-mini-2024-07-18"

    DEFAULT_SMALL_EMBEDDING_MODEL: str = "text-embedding-3-small"
    DEFAULT_LARGE_EMBEDDING_MODEL: str = "text-embedding-3-large"

    @model_validator(mode="before")
    @classmethod
    def load_secrets(cls, values: Dict) -> Dict:
        """Load secrets from AWS Secrets Manager if configured"""
        # Get service name from the actual class (including subclasses)
        service_name = values.get("SERVICE_NAME")
        environment = values.get("ENVIRONMENT")

        if not service_name or not environment or environment == "local":
            logger.debug("Skipping secrets load - local environment or missing config")
            return values
        else:
            logger.debug(f"Loading secrets for {service_name} in {environment}")

        # Use SecretsManagerMixin directly instead of creating a new instance
        secrets_dict = cls.get_secrets(f"{environment}/{service_name}/secrets")
        logger.debug(f"Updating values with secrets keys: {list(secrets_dict.keys())}")

        # Export secrets to environment variables
        for key, value in secrets_dict.items():
            os.environ[key] = str(value)

        values.update(secrets_dict)
        return values

    @computed_field
    @property
    def server_host(self) -> str:
        return f"https://{self.DOMAIN}"

    @computed_field
    @property
    def services(self) -> ServiceRegistry:
        """Access to all service URLs and configurations"""
        return ServiceRegistry(
            server_host=self.server_host, service_keys=self.SERVICE_KEYS
        )

    @computed_field
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return build_database_url(
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            server=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            db=self.POSTGRES_DB,
            asyncpg=self.POSTGRES_ASYNC,
        )

    @computed_field
    @property
    def SYNC_DATABASE_URL_STRING(self) -> str:
        return str(
            MultiHostUrl.build(
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    @computed_field
    @property
    def ELASTICSEARCH_URL_STRING(self) -> str:
        return f"http://{self.ELASTICSEARCH_SERVER}:{self.ELASTICSEARCH_PORT}"


common_settings = CommonSettings()
