import json
import re
import uuid
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable

from loguru import logger
from jose import jwt, ExpiredSignatureError, JWTError
from cryptography.fernet import Fernet
from fastapi import Request

from common.config import common_settings, CommonSettings
from common.services import ServiceType


def validate_identifier(identifier: str) -> str:
    """Validates and normalizes account identifiers to match GitHub repository naming conventions.

    Args:
        identifier: The account identifier to validate

    Returns:
        Normalized (lowercase) identifier if valid

    Raises:
        ValueError: If the identifier is invalid
    """
    if not identifier:
        raise ValueError("identifier cannot be empty")

    # Check for valid characters and pattern
    if not re.match(
        r"^[a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$", identifier
    ):
        raise ValueError(
            "identifier must contain only alphanumeric characters, hyphens, or "
            "underscores, and cannot start or end with a hyphen"
        )

    # Check for consecutive hyphens
    if "--" in identifier:
        raise ValueError("identifier cannot contain consecutive hyphens")

    return identifier.lower()  # normalize to lowercase for consistency


def email_to_username(email: str) -> str:
    """Converts an email address to a valid username.

    Args:
        email: Email address to convert

    Returns:
        A valid username derived from the email address

    Raises:
        ValueError: If a valid username cannot be generated from the email
    """
    if not email or "@" not in email:
        raise ValueError("Invalid email address")

    # Get the part before @ and replace invalid chars with underscore
    username = email.split("@")[0]
    username = re.sub(r"[^a-zA-Z0-9-]", "_", username)

    # Remove consecutive underscores
    username = re.sub(r"_+", "_", username)

    # Ensure it starts and ends with alphanumeric
    username = username.strip("_-")

    # If empty after cleaning, raise error
    if not username:
        raise ValueError("Could not generate valid username from email")

    # Validate and normalize using existing function
    return validate_identifier(username)


def extract_access_token(request: Request) -> str | None:
    token_string = request.headers.get(common_settings.ACCESS_TOKEN_HEADER)
    if token_string is None:
        return None
    return token_string.split(" ")[-1]


def extract_service_key(request: Request) -> str | None:
    key_string = request.headers.get(common_settings.SERVICE_KEY_HEADER)
    if key_string is None:
        return None
    return key_string


def extract_service_type(request: Request) -> str | None:
    from common.services import ServiceType

    type_string = request.headers.get(common_settings.SERVICE_TYPE_HEADER)
    if type_string is None:
        return None
    return ServiceType(type_string).value


def has_service_key(request: Request) -> bool:
    """Check if a service key is present in the request headers.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        bool: True if service key header is present and non-empty
    """
    key_string = request.headers.get(common_settings.SERVICE_KEY_HEADER)
    return key_string is not None and key_string.strip() != ""


def has_service_type(request: Request) -> bool:
    """Check if a service type is present in the request headers.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        bool: True if service type header is present and non-empty
    """
    type_string = request.headers.get(common_settings.SERVICE_TYPE_HEADER)
    return type_string is not None and type_string.strip() != ""



def imbue_header_with_access_token(
    token: str, headers: dict, in_place: bool = True
) -> dict:
    if not in_place:
        headers = deepcopy(headers)
    headers[common_settings.ACCESS_TOKEN_HEADER] = f"Bearer {token}"
    return headers


def imbue_header_with_service_key(
    key: str, headers: dict, in_place: bool = True
) -> dict:
    if not in_place:
        headers = deepcopy(headers)
    headers[common_settings.SERVICE_KEY_HEADER] = key
    return headers


def imbue_header_with_service_type(
    service_type: str | ServiceType, headers: dict, in_place: bool = True
) -> dict:
    if not in_place:
        headers = deepcopy(headers)
    headers[common_settings.SERVICE_TYPE_HEADER] = ServiceType(service_type).value
    return headers


def generate_encryption_key() -> str:
    """Generate a new encryption key as a string.

    Returns:
        str: A new encryption key ready for storage
    """
    return Fernet.generate_key().decode()


def encrypt_text(text: str, key: str) -> str:
    """Encrypt a string using a key.

    Args:
        text: The text to encrypt
        key: The encryption key as a string

    Returns:
        str: The encrypted text

    Raises:
        ValueError: If the key is invalid
    """
    f = Fernet(key.encode())
    encrypted_data = f.encrypt(text.encode())
    return encrypted_data.decode()


def decrypt_text(encrypted_text: str, key: str) -> str:
    """Decrypt an encrypted string using a key.

    Args:
        encrypted_text: The text to decrypt
        key: The encryption key as a string

    Returns:
        str: The decrypted text

    Raises:
        ValueError: If the key is invalid or the text can't be decrypted
    """
    try:
        f = Fernet(key.encode())
        decrypted_data = f.decrypt(encrypted_text.encode())
        return decrypted_data.decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}") from e


def generate_jwt(
    payload: Dict[str, Any],
    secret_key: str,
    expiry: Optional[datetime] = None,
    expiry_minutes: Optional[float] = None,
    algorithm: str = "HS256",
    encryption_key: Optional[str] = None,
    encrypted_payload_key: str = "encrypted_payload",
) -> str:
    """Generate a JWT token with the given payload.

    Args:
        payload: Dictionary containing the claims to encode in the JWT
        secret_key: Key used to sign the JWT
        expiry: Optional explicit expiry datetime
        expiry_minutes: Optional minutes until token expires (ignored if expiry is set)
        algorithm: JWT algorithm to use (default: HS256)
        encryption_key: Optional key to encrypt the payload
        encrypted_payload_key: Key under which to store the encrypted payload

    Returns:
        A signed JWT string
    """
    claims = {**payload, "iat": datetime.utcnow().timestamp(), "jti": uuid.uuid4().hex}

    if expiry:
        claims["exp"] = expiry.timestamp()
    elif expiry_minutes is not None:
        claims["exp"] = (
            datetime.utcnow() + timedelta(minutes=expiry_minutes)
        ).timestamp()

    # Encrypt payload if encryption key is provided
    if encryption_key:
        claims_str = json.dumps(claims)
        encrypted_claims = encrypt_text(claims_str, encryption_key)
        claims = {encrypted_payload_key: encrypted_claims}

    return jwt.encode(claims, secret_key, algorithm=algorithm)


def verify_jwt(
    token: str,
    secret_key: str,
    encryption_key: Optional[str] = None,
    algorithm: str = "HS256",
    encrypted_payload_key: str = "encrypted_payload",
) -> Dict[str, Any]:
    """Verify and decode a JWT token.

    Args:
        token: The JWT token to verify
        secret_key: Key used to verify the JWT signature
        encryption_key: Optional key to decrypt the payload
        algorithm: JWT algorithm to use (default: HS256)
        encrypted_payload_key: Key under which the encrypted payload is stored

    Returns:
        The decoded payload if valid

    Raises:
        jose.exceptions.JWTError: If the token is invalid or expired
    """
    try:
        # Be explicit about allowed algorithms
        decoded = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],  # Use constant instead of parameter
            options={
                "verify_signature": True,
                "require_exp": False,  # Don't require expiration
                "verify_exp": True,  # But verify it if present
            },
        )

        # If payload was encrypted, decrypt it
        if encryption_key and encrypted_payload_key in decoded:
            try:
                decrypted_text = decrypt_text(
                    decoded[encrypted_payload_key], encryption_key
                )
                claims = json.loads(decrypted_text)

                # Check expiry
                if "exp" in claims and claims["exp"] < datetime.utcnow().timestamp():
                    raise ExpiredSignatureError("Token has expired")

                return claims
            except ValueError as e:
                raise PermissionError(f"Failed to decrypt payload: {str(e)}")

        return decoded
    except ExpiredSignatureError as e:
        raise PermissionError("Token has expired") from e
    except JWTError as e:
        raise PermissionError(f"Invalid token: {str(e)}")


def decode_jwt_unverified(
    token: str,
    encryption_key: Optional[str] = None,
    algorithm: str = "HS256",
    encrypted_payload_key: str = "encrypted_payload",
) -> Dict[str, Any]:
    """Decode a JWT token WITHOUT signature verification.

    WARNING: This function does NOT verify the token signature or authenticity.
    The returned data should NEVER be trusted for security-critical decisions.
    Use this only for extracting metadata like routing information, logging context, etc.

    Args:
        token: The JWT token to decode
        encryption_key: Optional key to decrypt the payload
        algorithm: JWT algorithm (used for decoding format, not verification)
        encrypted_payload_key: Key under which the encrypted payload is stored

    Returns:
        The decoded payload (UNVERIFIED - do not trust for security decisions)

    Raises:
        jose.exceptions.JWTError: If the token is malformed or cannot be decoded
        ValueError: If decryption fails
    """
    try:
        # Decode without signature verification
        decoded = jwt.decode(
            token,
            key="",
            algorithms=[algorithm],
            options={
                "verify_signature": False,  # This is the key difference
                "verify_exp": False,  # Don't verify expiration either
                "verify_aud": False,  # Don't verify audience
                "verify_iss": False,  # Don't verify issuer
            },
        )

        # If payload was encrypted, decrypt it
        if encryption_key and encrypted_payload_key in decoded:
            try:
                decrypted_text = decrypt_text(
                    decoded[encrypted_payload_key], encryption_key
                )
                claims = json.loads(decrypted_text)
                return claims
            except ValueError as e:
                raise ValueError(f"Failed to decrypt payload: {str(e)}")

        return decoded

    except JWTError as e:
        raise ValueError(f"Failed to decode token (malformed): {str(e)}")


async def validate_internal_service_request(
    request: Request,
    settings: CommonSettings | None = None,
    exception_callable: Callable = None,
) -> None:
    if settings is None:
        settings = common_settings
    service_type = extract_service_type(request)
    service_key = extract_service_key(request)
    if not service_type or not service_key:
        if not service_type:
            logger.error("Service type missing from headers.")
        if not service_key:
            logger.error("Service key missing from headers.")
        raise exception_callable()

    try:
        await validate_service_credentials(
            settings=settings, service_type=service_type, service_key=service_key
        )
    except PermissionError:
        logger.error(
            f"Failed to validate service credentials for service: {service_type}"
        )
        raise


async def validate_service_credentials(
    service_type: str, service_key: str, settings: CommonSettings | None = None
) -> bool:
    """
    Validate service credentials for contact-based operations.

    Args:
        service_type: The type of service making the request
        service_key: The service's authentication key
        settings: The CommonSettings instance containing service configurations

    Returns:
        bool: True if credentials are valid

    Raises:
        PermissionError: If credentials are invalid
    """
    if settings is None:
        settings = common_settings
    try:
        service_config = settings.services.get(ServiceType(service_type))
        key_valid = service_config.validate_service_key(service_key)
        if not key_valid:
            raise PermissionError("Invalid service key")
        return True
    except (KeyError, ValueError):
        raise PermissionError("Invalid service type")
