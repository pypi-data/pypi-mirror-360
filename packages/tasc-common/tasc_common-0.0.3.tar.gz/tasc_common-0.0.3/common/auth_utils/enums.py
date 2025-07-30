from enum import Enum
from typing import List, Union
from common.config import common_settings


class ActionType(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = "manage"

    @classmethod
    def all(cls) -> List["ActionType"]:
        return [
            cls.CREATE,
            cls.READ,
            cls.UPDATE,
            cls.DELETE,
            cls.MANAGE,
        ]

    @classmethod
    def crud(cls) -> List["ActionType"]:
        return [
            cls.CREATE,
            cls.READ,
            cls.UPDATE,
            cls.DELETE,
        ]

    @classmethod
    def rud(cls) -> List["ActionType"]:
        return [
            cls.READ,
            cls.UPDATE,
            cls.DELETE,
        ]


class ContactType(str, Enum):
    PHONE = "phone"
    EMAIL = "email"

    @property
    def details_key(self) -> str:
        return {
            ContactType.PHONE: "phone_number",
            ContactType.EMAIL: "email",
        }[self]

    @property
    def webhook_url(self) -> str:
        return {
            ContactType.PHONE: common_settings.services.comms.sms_send_url,
            ContactType.EMAIL: common_settings.services.comms.email_send_url,
        }[self]

    @property
    def recipient_key(self) -> str:
        return {
            ContactType.PHONE: "phone_number",
            ContactType.EMAIL: "email_address",
        }[self]


class ContactPrincipalType(str, Enum):
    GROUP = "group"
    USER = "user"


class Oauth2PrincipalType(str, Enum):
    USER = "user"
    GROUP = "group"


class UsageSessionTokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
