from pydantic import BaseModel

from common.api_utils import APIResponse, OTPAPIResponse
from common.auth_utils.interface_models import (
    ContactCreate,
    ContactDetails,
    ContactRead,
    MagicLinkRequest,
    MagicLinkSignupRequest,
    AnonymizedUserRead,
    NewAccountAndRootUser,
    UserInfo,
    Oauth2ProviderCreate,
    Oauth2ProviderUpdate,
    Oauth2ProviderRead,
    ResourceListRequest,
    ResourceRead,
    InternalServiceTokenRequest,
    ApiKeyResponse,
    ApiSessionRead,
    OTPSignupRequest,
)
from common.auth_utils.interface_models import TokenResponseRead
from typing import Callable, List, Optional

from pathlib import PurePosixPath

from common.services import ServiceType, ServiceConfig
import httpx
from fastapi import Request, HTTPException, FastAPI

from common.auth_utils import (
    ActionType,
    ResourcePath,
    Actions,
    ContactRead,
    UsageSessionValidityRead,
    ResourcePermissionCheck,
    ResourcePermissionCheckResult,
    ResourceRegistration,
    ResourceRegistrationResult,
    extract_access_token,
    extract_service_key,
    extract_service_type,
    imbue_header_with_access_token,
    imbue_header_with_service_type,
    imbue_header_with_service_key,
)
from common.config import common_settings as settings
from loguru import logger

from common.auth_utils.interface_models import Oauth2AuthUrl


class AuthClientState(BaseModel):
    api_url: str
    resource_path_prefix: str
    enabled: bool = True
    exclude_paths: List[str] | None = None


class AuthClient:
    def __init__(
        self,
        api_base: str | None = None,
        resource_path_prefix: str | None = None,
        enabled: bool = True,
        exclude_paths: List[str] = None,
        service_type: str | None = None,
        service_key: str | None = None,
    ):
        self.api_url = api_base or settings.services.get_internal_url(ServiceType.AUTH)
        self.resource_path_prefix = resource_path_prefix
        self.enabled = enabled
        self.exclude_paths = exclude_paths or []
        self.service_type = service_type
        self.service_key = service_key

    def get_state(self) -> AuthClientState:
        return AuthClientState(
            api_url=self.api_url,
            resource_path_prefix=self.resource_path_prefix,
            enabled=self.enabled,
            exclude_paths=self.exclude_paths,
        )

    @classmethod
    def from_state(cls, state: AuthClientState) -> "AuthClient":
        client = cls(
            api_base=state.api_url,
            resource_path_prefix=state.resource_path_prefix,
            enabled=state.enabled,
            exclude_paths=state.exclude_paths,
        )
        return client

    @staticmethod
    def get_access_token(
        *,
        access_token: str | None = None,
        request: Request | None = None,
        raise_error: bool = False,
    ):
        if access_token is not None:
            return access_token
        if request is not None:
            return extract_access_token(request)
        if raise_error:
            raise ValueError("Either access_token or request must be provided.")
        return None

    @staticmethod
    def get_service_key(
        *,
        service_key: str | None = None,
        request: Request | None = None,
        raise_error: bool = False,
    ):
        if service_key is not None:
            return service_key
        if request is not None:
            return extract_service_key(request)
        if raise_error:
            raise ValueError("Either service_key or request must be provided.")
        return None

    @staticmethod
    def get_service_type(
        *,
        service_type: str | None = None,
        request: Request | None = None,
        raise_error: bool = False,
    ):
        if service_type is not None:
            return service_type
        if request is not None:
            return extract_service_type(request)
        if raise_error:
            raise ValueError("Either service_type or request must be provided.")
        return None

    def add_middleware(self, app: FastAPI) -> "AuthClient":
        @app.middleware("http")
        async def session_validation_middleware(request: Request, call_next: Callable):
            if any(request.url.path.endswith(path) for path in self.exclude_paths):
                return await call_next(request)

            await self.assert_session_valid(request)
            response = await call_next(request)
            return response

        return self

    def resource(self, path: str | None) -> ResourcePath:
        if self.resource_path_prefix is not None:
            base_path = PurePosixPath(self.resource_path_prefix)
        else:
            base_path = PurePosixPath()
        if path is None:
            final_path = base_path
        else:
            final_path = base_path / path
        return ResourcePath(path=str(final_path))

    @staticmethod
    def action(
        action: str | Actions,
        recursive: bool = False,
    ) -> Actions:
        if isinstance(action, Actions):
            return action
        if action == "crud":
            actions = ActionType.crud()
        elif action == "all":
            actions = ActionType.all()
        else:
            actions = [ActionType(action)]
        return Actions(actions=actions, recursive=recursive)

    async def _make_request(
        self,
        method: str,
        path: str,
        access_token: str | None = None,
        service_type: str | None = None,
        service_key: str | None = None,
        **kwargs,
    ) -> dict:
        path = path.lstrip("/")
        base_url = self.api_url.rstrip("/")
        url = f"{base_url}/{path}"

        headers = {}
        if access_token:
            headers = imbue_header_with_access_token(access_token, headers)

        if service_type is not None:
            headers = imbue_header_with_service_type(service_type, headers)

        if service_key is not None:
            headers = imbue_header_with_service_key(service_key, headers)

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            return await self._handle_response(response, path)

    async def _handle_response(self, response: httpx.Response, path: str) -> dict:
        """Handle the response from the server.

        For 200 responses, return the JSON response.
        For error responses, return the error message if available.
        """
        if response.status_code == 200:
            return response.json()

        # Try to get error details from response
        try:
            error_data = response.json()
            error_msg = (
                error_data.get("detail") or error_data.get("message") or response.text
            )
        except:
            error_msg = response.text or f"HTTP {response.status_code}"

        # Raise HTTPException with the error message
        raise HTTPException(status_code=response.status_code, detail=error_msg)

    async def check_if_session_valid(self, request: Request) -> bool:
        if not self.enabled:
            return True

        access_token = extract_access_token(request)
        if access_token is None:
            return False

        service_key = extract_service_key(request)
        service_type = extract_service_type(request)

        result = await self._make_request(
            "GET",
            "/usage-session/valid",
            access_token=access_token,
            service_key=service_key,
            service_type=service_type,
        )
        validity = UsageSessionValidityRead.model_validate(result)
        return validity.is_valid

    async def assert_session_valid(self, request: Request) -> "AuthClient":
        is_valid = await self.check_if_session_valid(request)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return self

    async def check_permission(
        self,
        resource: ResourcePath,
        action: str | Actions,
        *,
        request: Request | None = None,
        access_token: str | None = None,
        service_type: str | None = None,
        service_key: str | None = None,
    ) -> bool:
        if not self.enabled:
            return True

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )
        service_type = self.get_service_type(
            service_type=service_type, request=request, raise_error=False
        )
        service_key = self.get_service_key(
            service_key=service_key, request=request, raise_error=False
        )

        logger.info(
            f"Checking permission for resource: {resource} and action: {action}"
        )

        resource_permission_check = ResourcePermissionCheck(
            resource_path=resource,
            actions=self.action(action),
        )
        logger.info(f"Resource permission check: {resource_permission_check}")
        result = await self._make_request(
            "POST",
            "/resource/permission/check",
            access_token=access_token,
            service_type=service_type,
            service_key=service_key,
            json=resource_permission_check.model_dump(),
        )
        logger.info(f"Resource permission check result: {result}")
        result = ResourcePermissionCheckResult.model_validate(result)
        return result.is_permitted

    async def assert_permission(
        self,
        resource: ResourcePath,
        action: str | Actions,
        *,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> "AuthClient":
        has_permission = await self.check_permission(
            resource, action, request=request, access_token=access_token
        )
        if not has_permission:
            raise HTTPException(status_code=403, detail="Unauthorized")
        return self

    async def register_resource(
        self,
        resource: ResourcePath,
        action: str | Actions,
        *,
        request: Request | None = None,
        access_token: str | None = None,
        service_type: str | None = None,
        service_key: str | None = None,
    ) -> "AuthClient":
        if not self.enabled:
            return self

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )
        service_type = self.get_service_type(
            service_type=service_type, request=request, raise_error=False
        )
        service_key = self.get_service_key(
            service_key=service_key, request=request, raise_error=False
        )

        registration = ResourceRegistration(
            resource_path=resource,
            actions=self.action(action),
        )

        result = await self._make_request(
            "POST",
            "/resource/register",
            access_token=access_token,
            service_type=service_type,
            service_key=service_key,
            json=registration.model_dump(),
        )
        logger.info(f"Resource registration result: {result}")
        result = ResourceRegistrationResult.model_validate(result)
        if not result.success:
            raise HTTPException(
                status_code=400,
                detail="Failed to register resource",
            )

        return self

    async def list_resources(
        self,
        path_postfix_pattern: ResourcePath,
        *,
        request: Request | None = None,
        access_token: str | None = None,
        service_type: str | None = None,
        service_key: str | None = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = True,
    ) -> list[ResourceRead]:
        """List resources matching the given path postfix pattern.

        Args:
            path_postfix_pattern: Pattern to match resource paths against as a ResourcePath
            request: Optional request object containing the access token
            access_token: Optional explicit access token
            service_type: Optional service type
            service_key: Optional service key
            offset: Number of items to skip
            limit: Maximum number of items to return
            sort_by: Field to sort by ('created_at', 'updated_at', or 'path_postfix')
            sort_desc: Sort in descending order if True, ascending if False

        Returns:
            list[ResourceRead]: List of matching resources if successful, empty list if auth is disabled

        Raises:
            HTTPException: If unauthorized or resources cannot be retrieved
        """
        if not self.enabled:
            return []

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )
        service_type = self.get_service_type(
            service_type=service_type, request=request, raise_error=False
        )
        service_key = self.get_service_key(
            service_key=service_key, request=request, raise_error=False
        )

        result = await self._make_request(
            "POST",
            "/resource/list",
            json=ResourceListRequest(
                path_postfix_pattern=path_postfix_pattern,
                offset=offset,
                limit=limit,
                sort_by=sort_by,
                sort_desc=sort_desc,
            ).model_dump(),
            access_token=access_token,
            service_type=service_type,
            service_key=service_key,
        )
        return [ResourceRead.model_validate(item) for item in result]

    async def request_magic_link(
        self,
        magic_link_request: MagicLinkRequest,
        request: Request | None = None,
        service_key: str | None = None,
        service_type: str | None = None,
        headers: dict | None = None,
    ) -> APIResponse | None:
        """Request a magic link token for authentication."""
        if not self.enabled:
            return None

        service_key = self.get_service_key(
            request=request,
            service_key=service_key or self.service_key,
        )
        service_type = self.get_service_type(
            request=request,
            service_type=service_type or self.service_type,
        )

        if headers is None:
            headers = request.headers if request else None

        result = await self._make_request(
            "POST",
            "/magic-link/signin",
            json=magic_link_request.model_dump(),
            headers=headers,
            service_key=service_key,
            service_type=service_type,
        )
        return APIResponse.model_validate(result)

    async def verify_magic_link(
        self,
        token: str,
    ) -> TokenResponseRead | None:
        """Verify a magic link token."""
        if not self.enabled:
            return None

        result = await self._make_request(
            "GET",
            f"/magic-link/verify/signin/{token}",
        )
        return TokenResponseRead.model_validate(result)

    async def signup_with_magic_link(
        self,
        magic_link_request: MagicLinkSignupRequest,
        request: Request | None = None,
        service_key: str | None = None,
        service_type: str | None = None,
        headers: dict | None = None,
    ) -> APIResponse | None:
        """Request a magic link token for signup."""
        if not self.enabled:
            return None

        service_key = self.get_service_key(
            request=request,
            service_key=service_key or self.service_key,
        )
        service_type = self.get_service_type(
            request=request,
            service_type=service_type or self.service_type,
        )

        if headers is None:
            headers = request.headers if request else None

        result = await self._make_request(
            "POST",
            "/magic-link/signup",
            json=magic_link_request.model_dump(),
            headers=headers,
            service_key=service_key,
            service_type=service_type,
        )
        return APIResponse.model_validate(result)

    async def verify_signup_magic_link(
        self, token: str, request: Request | None = None
    ) -> TokenResponseRead | None:
        """Verify a signup magic link token."""
        if not self.enabled:
            return None

        result = await self._make_request(
            "GET",
            f"/magic-link/verify/signup/{token}",
        )
        return TokenResponseRead.model_validate(result)

    async def signup_with_otp(
        self,
        otp_request: OTPSignupRequest,
        service_type: str | None = None,
        service_key: str | None = None,
    ) -> OTPAPIResponse | None:
        """Request an OTP for signup.

        Args:
            otp_request: OTPSignupRequest containing email and user details
            service_type: Optional service type for authentication
            service_key: Optional service key for authentication

        Returns:
            OTPAPIResponse: Response containing token and OTP if successful, None if auth is disabled

        Raises:
            HTTPException: If email is already registered or other errors occur
        """
        if not self.enabled:
            return None

        service_type = service_type or self.service_type
        service_key = service_key or self.service_key

        result = await self._make_request(
            "POST",
            "/otp/signup",
            json=otp_request.model_dump(),
            service_type=service_type,
            service_key=service_key,
        )
        return OTPAPIResponse.model_validate(result)

    async def verify_signup_with_otp(
        self,
        token: str,
        otp: str,
        no_redirect_on_error: bool = False,
    ) -> TokenResponseRead | None:
        """Verify an OTP and complete the signup process.

        Args:
            token: The token received from signup_with_otp
            otp: The OTP code entered by the user
            no_redirect_on_error: If True, don't redirect on error (return error response instead)

        Returns:
            TokenResponseRead: Authentication tokens if successful, None if auth is disabled

        Raises:
            HTTPException: If OTP is invalid, expired, or too many attempts
        """
        if not self.enabled:
            return None

        headers = {}
        if no_redirect_on_error:
            headers["X-No-Redirect-On-Error"] = "true"

        result = await self._make_request(
            "POST",
            f"/otp/verify/signup/{token}",
            json={"otp": otp},
            headers=headers,
        )

        return TokenResponseRead.model_validate(result)

    async def signin_with_otp(
        self,
        email: str,
        service_type: str | None = None,
        service_key: str | None = None,
    ) -> OTPAPIResponse | None:
        """Request an OTP for sign-in.

        Args:
            email: Email address to send the OTP to
            service_type: Optional service type for authentication
            service_key: Optional service key for authentication

        Returns:
            OTPAPIResponse: Response containing token and OTP if successful, None if auth is disabled

        Raises:
            HTTPException: If email is not registered or other errors occur
        """
        if not self.enabled:
            return None

        service_type = service_type or self.service_type
        service_key = service_key or self.service_key

        result = await self._make_request(
            "POST",
            "/otp/signin",
            json={"email": email},
            service_type=service_type,
            service_key=service_key,
        )
        return OTPAPIResponse.model_validate(result)

    async def verify_signin_with_otp(
        self,
        token: str,
        otp: str,
        no_redirect_on_error: bool = False,
    ) -> TokenResponseRead | None:
        """Verify an OTP and complete the sign-in process.

        Args:
            token: The token received from request_signin_otp
            otp: The OTP code entered by the user
            no_redirect_on_error: If True, don't redirect on error (return error response instead)

        Returns:
            TokenResponseRead: Authentication tokens if successful, None if auth is disabled

        Raises:
            HTTPException: If OTP is invalid, expired, or too many attempts
        """
        if not self.enabled:
            return None

        headers = {}
        if no_redirect_on_error:
            headers["X-No-Redirect-On-Error"] = "true"

        result = await self._make_request(
            "POST",
            f"/otp/verify/signin/{token}",
            json={"otp": otp},
            headers=headers,
        )

        return TokenResponseRead.model_validate(result)

    async def exchange_token(
        self,
        *,
        code: str | None = None,
        refresh_token: str | None = None,
    ) -> TokenResponseRead | None:
        """Exchange authorization code for tokens or refresh an existing token."""
        if not self.enabled:
            return None

        if code is not None:
            data = {
                "grant_type": "authorization_code",
                "code": code,
            }
        elif refresh_token is not None:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        else:
            raise ValueError("Either code or refresh_token must be provided")

        result = await self._make_request(
            "POST",
            "/token",
            params=data,
        )
        return TokenResponseRead.model_validate(result)

    async def verified_contact_exists(
        self,
        contact_details: ContactDetails,
        service_type: str | None = None,
        service_key: str | None = None,
    ) -> bool:
        if not self.enabled:
            return False

        service_type = service_type or self.service_type
        service_key = service_key or self.service_key

        result = await self._make_request(
            "GET",
            "/contact/exists",
            params=contact_details.model_dump(),
            service_type=service_type,
            service_key=service_key,
        )
        return result

    async def create_contact(
        self,
        contact: ContactCreate,
    ) -> ContactRead | None:
        if not self.enabled:
            return None

        result = await self._make_request(
            "POST",
            "/contact",
            json=contact.model_dump(),
        )
        return ContactRead.model_validate(result)

    async def get_user_id(
        self, request: Request | None = None, access_token: str | None = None
    ) -> str | None:
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        result = await self._make_request(
            "GET",
            "/user/id",
            access_token=access_token,
        )
        if result is not None:
            return AnonymizedUserRead.model_validate(result).hashed_id
        else:
            raise ValueError("Malformed response.")

    async def create_service_token(
        self,
        payload: dict,
        *,
        expires_in_seconds: float | None = None,
        single_use: bool = False,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> str | None:
        """Create a new service token with the given payload."""
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        request_body = {
            "payload": payload,
            "expires_in_seconds": expires_in_seconds,
            "single_use": single_use,
        }

        result = await self._make_request(
            "POST",
            "/token-service",
            json=request_body,
            access_token=access_token,
        )
        return result["token_string"]

    async def read_service_token(
        self,
        token: str,
        *,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> dict | None:
        """Read the payload from a service token."""
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        result = await self._make_request(
            "GET",
            f"/token-service/{token}",
            access_token=access_token,
        )
        return result["payload"]

    async def generate_token_from_contact(
        self,
        contact_details: ContactDetails,
        service_type: str | None = None,
        service_key: str | None = None,
    ) -> TokenResponseRead | None:
        """Generate an access token for a verified contact method.

        Args:
            contact_details: ContactDetails containing either email_address or phone_number
            service_type: Optional service type
            service_key: Optional service key

        Returns:
            TokenResponseRead: Generated oauth2 tokens if successful, None if auth is disabled

        Raises:
            HTTPException: If no verified contact found with provided details
        """
        if not self.enabled:
            return None

        service_type = service_type or self.service_type
        service_key = service_key or self.service_key

        result = await self._make_request(
            "POST",
            "/token/from-contact",
            json=contact_details.model_dump(exclude_none=True),
            service_type=service_type,
            service_key=service_key,
        )
        return TokenResponseRead.model_validate(result)

    async def get_user_info(
        self,
        *,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> UserInfo | None:
        """Get information about the authenticated user.

        Args:
            request: Optional request object containing the access token
            access_token: Optional explicit access token

        Returns:
            UserInfo: User information if successful, None if auth is disabled

        Raises:
            HTTPException: If unauthorized or user info cannot be retrieved
        """
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        result = await self._make_request(
            "GET",
            "/user/info",
            access_token=access_token,
        )
        return UserInfo.model_validate(result)

    async def delete_user(
        self,
        user_id: str,
    ) -> bool:
        """Delete a user."""
        if not self.enabled:
            return False

        success = await self._make_request(
            "DELETE",
            f"/user/{user_id}",
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete user")
        return True

    async def request_email_verification_token(
        self, email_address: str, access_token: str
    ) -> OTPAPIResponse:
        """
        Calls the Auth Server to generate an email verification token (OTP)
        """
        response = await self._make_request(
            "POST",
            "/contact/email/request-verification",
            access_token=access_token,
            json={"email_address": email_address},
        )
        return OTPAPIResponse.model_validate(response)

    async def verify_email_address(
        self, code: str, token: str, access_token: str
    ) -> ContactRead:
        """
        Calls the Auth Server to verify an email with the OTP code
        """
        response = await self._make_request(
            "POST",
            "/contact/email/verify",
            access_token=access_token,
            json={"code": code, "token": token},
        )
        return ContactRead.model_validate(response)

    async def request_phone_verification_token(
        self, phone_number: str, access_token: str
    ) -> OTPAPIResponse:
        """
        Calls the Auth Server to generate a phone verification token (OTP).
        Returns both token and OTP from the response.
        """
        response = await self._make_request(
            "POST",
            "/contact/phone/request-verification",
            access_token=access_token,
            json={"phone_number": phone_number},
        )
        # The response should contain: status, message, token, and otp
        return OTPAPIResponse.model_validate(response)

    async def verify_phone_number(
        self, token: str, code: str, access_token: str
    ) -> ContactRead:
        """
        Calls the Auth Server to verify a phone number with the OTP code.
        """
        response = await self._make_request(
            "POST",
            "/contact/phone/verify",
            access_token=access_token,
            json={"token": token, "code": code},
        )
        return ContactRead.model_validate(response)

    async def list_oauth2_providers(
        self,
        *,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> list[Oauth2ProviderRead]:
        """List all OAuth2 providers."""
        if not self.enabled:
            return []

        result = await self._make_request(
            "GET",
            "/oauth2/providers",
            access_token=access_token,
        )
        return [Oauth2ProviderRead.model_validate(item) for item in result]

    async def get_oauth2_provider(
        self,
        provider_id: str,
        *,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> Oauth2ProviderRead | None:
        """Get a specific OAuth2 provider by ID or descriptor."""
        if not self.enabled:
            return None

        result = await self._make_request(
            "GET",
            f"/oauth2/providers/{provider_id}",
            access_token=access_token,
        )
        return Oauth2ProviderRead.model_validate(result)

    async def create_oauth2_provider(
        self,
        provider: Oauth2ProviderCreate,
        *,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> Oauth2ProviderRead | None:
        """Create a new OAuth2 provider."""
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        result = await self._make_request(
            "POST",
            "/oauth2/providers",
            json=provider.model_dump(),
            access_token=access_token,
        )
        return Oauth2ProviderRead.model_validate(result)

    async def update_oauth2_provider(
        self,
        provider_id: str,
        provider: Oauth2ProviderUpdate,
        *,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> Oauth2ProviderRead | None:
        """Update an existing OAuth2 provider."""
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        result = await self._make_request(
            "PUT",
            f"/oauth2/providers/{provider_id}",
            json=provider.model_dump(exclude_none=True),
            access_token=access_token,
        )
        return Oauth2ProviderRead.model_validate(result)

    async def delete_oauth2_provider(
        self,
        provider_id: str,
        *,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> None:
        """Delete an OAuth2 provider."""
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        await self._make_request(
            "DELETE",
            f"/oauth2/providers/{provider_id}",
            access_token=access_token,
        )

    async def create_account(
        self,
        new_account: NewAccountAndRootUser,
    ) -> APIResponse:
        """
        Creates a new root user and account.
        Raises an HTTPException if there's a server-side error.
        """
        result = await self._make_request(
            "POST",
            "/account/create",
            json=new_account.model_dump(),
        )
        return APIResponse.model_validate(result)

    async def login_with_password(
        self,
        username: str,
        password: str,
    ) -> TokenResponseRead:
        """
        Logs in using password-based authentication and returns tokens.
        Raises an HTTPException if credentials are invalid or email is unverified.
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "username": username,
            "password": password,
        }
        response = await self._make_request(
            "POST",
            "/login/password",
            headers=headers,
            data=data,
        )
        return TokenResponseRead.model_validate(response)

    async def get_internal_service_token(
        self,
        *,
        target_service_type: str | ServiceType,
        target_service_key: str,
        request: Request | None = None,
        access_token: str | None = None,
        service_type: str | None = None,
        service_key: str | None = None,
    ) -> str | None:
        """Get an internal service token for making authenticated requests between services.

        Args:
            target_service_type: The service type of the target service
            target_service_key: The service key of the target service
            request: Optional request object containing the access token and service info
            access_token: Optional explicit access token
            service_type: Optional explicit service type
            service_key: Optional explicit service key

        Returns:
            str: The encoded internal service token if successful, None if auth is disabled

        Raises:
            HTTPException: If unauthorized or token cannot be generated
        """
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )
        service_key = self.get_service_key(
            service_key=service_key, request=request, raise_error=False
        )
        service_type = self.get_service_type(
            service_type=service_type, request=request, raise_error=False
        )

        result = await self._make_request(
            "POST",
            "/internal/service-token",
            access_token=access_token,
            service_type=service_type,
            service_key=service_key,
            json=InternalServiceTokenRequest(
                target_service_type=ServiceType(target_service_type).value,
                target_service_key=target_service_key,
            ).model_dump(),
        )
        return result["token_string"]

    async def delete_internal_service_token(
        self,
        *,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> None:
        """Delete an internal service token.

        Args:
            request: Optional request object containing the access token
            access_token: Optional explicit access token

        Returns:
            None

        Raises:
            HTTPException: If unauthorized or token cannot be deleted
        """
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        await self._make_request(
            "DELETE",
            "/internal/service-token",
            access_token=access_token,
        )

    async def create_api_key(
        self,
        *,
        request: Request | None = None,
        access_token: str | None = None,
        expires_at: float | None = None,
        validity_duration: float | None = None,
        info: dict | None = None,
    ) -> ApiKeyResponse | None:
        """Create a new API key for the authenticated user.

        Args:
            request: Optional request object to extract access token from
            access_token: Optional explicit access token
            expires_at: Optional explicit expiration timestamp
            validity_duration: Optional duration in seconds from now until expiration
            info: Optional metadata about the API key

        Returns:
            APIKeyResponse containing the new API key, or None if auth is disabled
        """
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        params = {}
        if expires_at is not None:
            params["expires_at"] = expires_at
        if validity_duration is not None:
            params["validity_duration"] = validity_duration
        if info is not None:
            params["info"] = info

        result = await self._make_request(
            "POST",
            "/api-key",
            access_token=access_token,
            json=params,
        )
        return ApiKeyResponse.model_validate(result)

    async def revoke_api_key(
        self,
        *,
        api_key: str | None = None,
        api_session_id: str | None = None,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> APIResponse | None:
        """Revoke an API key by key or session ID.

        Args:
            api_key: Optional API key to revoke
            api_session_id: Optional API session ID to revoke
            request: Optional request object to extract access token from
            access_token: Optional explicit access token

        Returns:
            APIResponse: Success response if revoked successfully, None if auth is disabled

        Raises:
            HTTPException: If neither api_key nor api_session_id is provided,
                      if unauthorized, or if API key cannot be revoked
        """
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        json_data = {}
        if api_key is not None:
            json_data["api_key"] = api_key
        if api_session_id is not None:
            json_data["api_session_id"] = api_session_id

        result = await self._make_request(
            "POST",
            "/api-key/revoke",
            access_token=access_token,
            json=json_data,
        )

        return APIResponse.model_validate(result)

    async def list_api_sessions(
        self,
        *,
        request: Request | None = None,
        access_token: str | None = None,
    ) -> List[ApiSessionRead] | None:
        """List all API keys for the authenticated user.

        Args:
            request: Optional request object to extract access token from
            access_token: Optional explicit access token

        Returns:
            List of ApiSessionRead objects containing API key details, or None if auth is disabled
        """
        if not self.enabled:
            return None

        access_token = self.get_access_token(
            access_token=access_token, request=request, raise_error=True
        )

        result = await self._make_request(
            "GET",
            "/api-session",
            access_token=access_token,
        )
        return [ApiSessionRead.model_validate(item) for item in result]

    async def get_contacts(self, *, access_token: str) -> List[ContactRead]:
        result = await self._make_request("GET", "/contact", access_token=access_token)
        return [ContactRead.model_validate(item) for item in result]

    async def delete_contact(
        self, *, contact_id: str, access_token: str
    ) -> APIResponse:
        result = await self._make_request(
            "DELETE", f"/contact/{contact_id}", access_token=access_token
        )
        return result

    async def make_contact_primary(
        self, *, contact_id: str, access_token: str
    ) -> APIResponse:
        result = await self._make_request(
            "POST",
            f"/contact/{contact_id}/make-primary",
            json={},
            access_token=access_token,
        )
        return result

    async def oauth2_integration_authorize(
        self, *, json: dict, access_token: str = None
    ) -> Oauth2AuthUrl:
        result = await self._make_request(
            "POST",
            "/oauth2/integration/authorize",
            json=json,
            access_token=access_token,
        )
        return Oauth2AuthUrl.model_validate(result)

    async def oauth2_login_authorize(self, *, payload: dict) -> Oauth2AuthUrl:
        result = await self._make_request(
            "POST", "/oauth2/login/authorize", json=payload
        )
        return Oauth2AuthUrl.model_validate(result)
