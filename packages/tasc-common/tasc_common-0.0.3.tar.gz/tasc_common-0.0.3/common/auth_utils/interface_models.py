from copy import deepcopy
from datetime import datetime

from starlette.responses import RedirectResponse

from common.api_utils import WebhookModel
from common.auth_utils.enums import ContactType
from pydantic import Field, field_validator

from pathlib import PurePosixPath
from typing import Any, List, Dict, Optional

from pydantic import BaseModel

from common.auth_utils import ActionType
from common.auth_utils.permissions import SupportsPermission
from common.services import ServiceType
from common.utils import format_string


# **************************
# *** Accounts and Users ***
# **************************


class NewAccountAndRootUser(BaseModel):
    account_name: str
    user_name: str
    primary_email: str
    password: str | None = None
    verified: bool = False
    first_name: str | None = None
    last_name: str | None = None


class AnonymizedUserRead(BaseModel):
    hashed_id: str


# *****************
# *** Resources ***
# *****************


class ResourcePath(BaseModel):
    path: str

    def __truediv__(self, other):
        return ResourcePath(path=str(PurePosixPath(self.path) / str(other)))

    def __str__(self):
        return str(self.path)

    @property
    def instance(self) -> "ResourcePath":
        return self / "instance"

    def in_account(self, account: SupportsPermission) -> "ResourcePath":
        return ResourcePath(
            path=str(PurePosixPath(account.path) / PurePosixPath(self.path))
        )


class Actions(BaseModel):
    actions: List[ActionType]
    recursive: bool = False


class ResourcePermissionCheck(BaseModel):
    resource_path: ResourcePath
    actions: Actions


class ResourceListRequest(BaseModel):
    path_postfix_pattern: ResourcePath
    offset: Optional[int] = None
    limit: Optional[int] = None
    sort_by: Optional[str] = None
    sort_desc: bool = True


class ResourcePermissionCheckResult(BaseModel):
    is_permitted: bool


class ResourceRegistration(BaseModel):
    resource_path: ResourcePath
    actions: Actions


class ResourceRegistrationResult(BaseModel):
    success: bool
    reason: str | None = None


class ResourceRead(BaseModel):
    id: str

    created_at: float

    path_postfix: str
    info: dict | None = None

    @property
    def name(self):
        return PurePosixPath(self.path_postfix).name


# *********************
# *** Usage Session ***
# *********************


class UsageSessionValidityRead(BaseModel):
    is_valid: bool


# *******************
# *** API Session ***
# *******************

class ApiKeyResponse(BaseModel):
    id: str
    api_key: str
    created_at: float
    expires_at: float
    revoked_at: float | None = None


class ApiKeyValidityRead(BaseModel):
    is_valid: bool


class ApiSessionRead(BaseModel):
    id: str
    created_at: float
    expires_at: float
    revoked_at: float | None = None
    info: dict | None = None


# ************************
# *** Token Generation ***
# ************************


class MagicLinkRequest(BaseModel):
    email: str


class MagicLinkSignupRequest(BaseModel):
    email: str
    user_name: str | None = None
    account_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class OTPSignupRequest(MagicLinkSignupRequest):
    pass

class OTPVerifyRequest(BaseModel):
    otp: str
    token: str


# **********************
# *** Contact Models ***
# **********************


class ContactDetails(BaseModel):
    email_address: str | None = None
    phone_number: str | None = None
    webhook: WebhookModel | None = None


class ContactRead(BaseModel):
    id: str
    contact_type: ContactType
    contact_details: ContactDetails
    verified: bool


class ContactCreate(ContactRead):
    pass


# *****************
# *** Redirects ***
# *****************


class RedirectRequest(BaseModel):
    redirect_url: str = Field(description="The URL to redirect to. Can be a template.")
    headers: Dict[str, str] | None = Field(
        default=None,
        description=(
            "Header key-value pairs to include in the redirect request. "
            "Values can be templates."
        ),
    )

    def to_response(self, **format_kwargs) -> RedirectResponse:
        if self.headers is None:
            headers = None
        else:
            headers = deepcopy(self.headers)
            for key, value in headers.items():
                headers[key] = format_string(value, **format_kwargs)

        url = format_string(self.redirect_url, **format_kwargs)
        return RedirectResponse(url, headers=headers)


# **************
# *** Oauth2 ***
# **************


class Oauth2ProviderRead(BaseModel):
    id: str
    descriptor: str
    display_name: str | None
    client_id: str
    authorization_url: str
    token_url: str
    userinfo_url: str | None
    refresh_url: str | None
    revocation_url: str | None
    redirect_uri: str | None
    scopes: list[str]
    provider_config: dict | None


class Oauth2AuthUrl(BaseModel):
    """OAuth2 authorization URL."""

    auth_url: str


class Oauth2ProviderCreate(BaseModel):
    descriptor: str
    display_name: str | None = None
    client_id: str
    client_secret: str | None = None
    authorization_url: str
    token_url: str
    userinfo_url: str | None = None
    refresh_url: str | None = None
    revocation_url: str | None = None
    redirect_uri: str | None = None
    scopes: list[str] = Field(default_factory=list)
    provider_config: dict | None = None


class Oauth2ProviderUpdate(BaseModel):
    """
    Fields that may be updated on an existing provider. All are optional.
    """

    display_name: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    authorization_url: str | None = None
    token_url: str | None = None
    userinfo_url: str | None = None
    refresh_url: str | None = None
    revocation_url: str | None = None
    redirect_uri: str | None = None
    scopes: list[str] | None = None
    provider_config: dict | None = None


class UserInfo(BaseModel):
    """Standardized user info across providers."""

    hashed_id: Optional[str] = None
    email: str
    email_verified: bool = True
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture_url: Optional[str] = None
    external_id: Optional[str] = None  # 'sub' in OpenID Connect
    dossier: Optional[str] = None
    usecases: Optional[List[Dict[str, Any]]] = None


class TokenResponseRead(BaseModel):
    """Standardized token response across providers."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: float
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

    @property
    def expires_at(self) -> float:
        """Calculate expiration timestamp."""
        return datetime.now().timestamp() + self.expires_in


class TokenServiceResponse(BaseModel):
    token_string: str | None = None
    payload: dict | None = None


class InternalServiceTokenRequest(BaseModel):
    target_service_type: str
    target_service_key: str

    @field_validator("target_service_type")
    @classmethod
    def validate_target_service_type(cls, v: str | ServiceType) -> str:
        return ServiceType(v).value
