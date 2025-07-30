import secrets
from enum import Enum
from typing import Dict
from urllib.parse import urljoin
from pydantic import BaseModel

from common.utils import str_to_urlsafe_base64


class ServiceType(str, Enum):
    REGISTRY = "registry"
    RUNNER = "runner"
    PROVIDER = "provider"
    ACTX_SERVER = "actx"
    AUTH = "auth"
    FRONTEND = "frontend"
    PLATFORM = "platform"

class ServiceConfig(BaseModel):
    name: str
    path_prefix: str
    service_key: str | None = None

    @staticmethod
    def _extract_service_key(name: str, service_keys: str | None) -> str | None:
        if service_keys is None:
            service_key = None
        else:
            service_keys = service_keys.split(":")
            # Find the service key
            matching_service_keys = [
                key.split(".")[1]
                for key in service_keys  # Extract just the key part
                if key.startswith(f"{name}.")
            ]
            if len(matching_service_keys) == 0:
                service_key = None
            else:
                service_key = matching_service_keys[-1]
        return service_key

    def extract_service_key(self, service_keys: str | None) -> str | None:
        return self._extract_service_key(self.name, service_keys)

    @classmethod
    def build(
        cls, name: str, path_prefix: str, service_keys: str | None = None
    ) -> "ServiceConfig":
        return cls(
            name=name,
            path_prefix=path_prefix,
            service_key=cls._extract_service_key(name, service_keys),
        )

    def validate_service_key(self, service_key: str) -> bool:
        provided_service_key = self.extract_service_key(service_key)
        existing_service_key = self.service_key
        if existing_service_key is None:
            return True
        return existing_service_key == provided_service_key

    def get_service_key(self) -> str | None:
        if self.service_key is None:
            return None
        else:
            return f"{self.name}.{self.service_key}"


class CommsEndpoints:
    RECEIVE_MESSAGE = "receive_message"
    SEND_MESSAGE = "send_message"
    SMS = "sms"
    EMAIL = "email"
    APP = "app"
    WHATSAPP = "whatsapp"
    AGENT_SESSION = "agent_session"
    VOICE = "voice"
    COMMS_PATH = ""

    def __init__(self, server_host: str):
        self.server_host = server_host

    def build_url(self, endpoint_type: str, action: str) -> str:
        """Build a communications URL."""
        return urljoin(self.server_host, f"{self.COMMS_PATH}/{endpoint_type}/{action}")

    @property
    def sms_receive_url(self) -> str:
        return self.build_url(self.SMS, self.RECEIVE_MESSAGE)

    @property
    def sms_send_url(self) -> str:
        return self.build_url(self.SMS, self.SEND_MESSAGE)

    @property
    def email_receive_url(self) -> str:
        return self.build_url(self.EMAIL, self.RECEIVE_MESSAGE)

    @property
    def email_send_url(self) -> str:
        return self.build_url(self.EMAIL, self.SEND_MESSAGE)

    @property
    def app_send_url(self) -> str:
        return self.build_url(self.APP, self.SEND_MESSAGE)

    @property
    def app_receive_url(self) -> str:
        return self.build_url(self.APP, self.RECEIVE_MESSAGE)

    @property
    def whatsapp_send_url(self) -> str:
        return self.build_url(self.WHATSAPP, self.SEND_MESSAGE)

    @property
    def whatsapp_receive_url(self) -> str:
        return self.build_url(self.WHATSAPP, self.RECEIVE_MESSAGE)

    @property
    def voice_send_url(self) -> str:
        return self.build_url(self.VOICE, self.SEND_MESSAGE)

    @property
    def voice_receive_url(self) -> str:
        return self.build_url(self.VOICE, self.RECEIVE_MESSAGE)


class ServiceRegistry:
    def __init__(self, server_host: str, service_keys: str | None):
        self.server_host = server_host
        self._services: Dict[ServiceType, ServiceConfig] = {
            ServiceType.REGISTRY: ServiceConfig.build(
                name="tasx-registry", path_prefix="/registry", service_keys=service_keys
            ),
            ServiceType.RUNNER: ServiceConfig.build(
                name="tasx-runner", path_prefix="/runner", service_keys=service_keys
            ),
            ServiceType.PROVIDER: ServiceConfig.build(
                name="tasx-provider", path_prefix="/provider", service_keys=service_keys
            ),
            ServiceType.ACTX_SERVER: ServiceConfig.build(
                name="actx-server", path_prefix="/actx", service_keys=service_keys
            ),
            ServiceType.FRONTEND: ServiceConfig.build(
                name="frontend", path_prefix="/frontend", service_keys=service_keys
            ),
            ServiceType.AUTH: ServiceConfig.build(
                name="auth-server", path_prefix="/auth", service_keys=service_keys
            ),
            ServiceType.PLATFORM: ServiceConfig.build(
                name="platform-api", path_prefix="/platform-api", service_keys=service_keys
            ),
        }
        self.comms = CommsEndpoints(self.server_host)

    @property
    def path_prefixes(self) -> Dict[ServiceType, str]:
        """Get all path prefixes"""
        return {stype: config.path_prefix for stype, config in self._services.items()}

    def get_path_prefix(self, service_type: ServiceType) -> str:
        """Get path prefix for a specific service"""
        return self.get(service_type).path_prefix

    def get(self, service_type: ServiceType) -> ServiceConfig:
        """Get service configuration."""
        service_type = ServiceType(service_type)
        if service_type not in self._services:
            raise ValueError(f"Unknown service: {service_type}")
        return self._services[service_type]

    def get_internal_url(self, service_type: ServiceType) -> str:
        """Get the internal URL for a service."""
        internal_url = f"http://{self.get(service_type).name}"
        path_prefix = self.get(service_type).path_prefix
        return urljoin(internal_url, path_prefix)

    def get_external_url(self, service_type: ServiceType) -> str:
        """Get the external URL for a service."""
        path_prefix = self.get(service_type).path_prefix
        return urljoin(self.server_host, path_prefix)

    def get_service_key(self, service_type: ServiceType) -> str | None:
        """Get service key if configured."""
        return self.get(service_type).get_service_key()

    def validate_service_key(self, service_type: ServiceType, service_key: str) -> bool:
        """Validate service key."""
        service = self.get(service_type)
        return service.validate_service_key(service_key)

    def generate_service_keys(self) -> str:
        return ":".join(
            [
                f"{service.name}.{str_to_urlsafe_base64(secrets.token_urlsafe(16))}"
                for service in self._services.values()
            ]
        )