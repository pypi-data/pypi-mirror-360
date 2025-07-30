import json
import time
from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import Any, Optional, Literal

from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from zoneinfo import ZoneInfo


class TransientStorage(BaseModel):
    storage: dict[str, Any] = {}

    def get(self, key: str, default: Any = None, ensure_exists: bool = False) -> Any:
        if ensure_exists and key not in self.storage:
            raise KeyError(f"Key '{key}' not found in storage.")
        return self.storage.get(key, default)

    def set(self, key: str, value: Any) -> "TransientStorage":
        self.storage[key] = value
        return self

    def delete(self, key: str) -> "TransientStorage":
        if key in self.storage:
            del self.storage[key]
        return self

    def clear(self) -> "TransientStorage":
        self.storage.clear()
        return self

    def keys(self) -> list[str]:
        return list(self.storage.keys())

    def values(self) -> list[Any]:
        return list(self.storage.values())

    def items(self) -> list[tuple[str, Any]]:
        return list(self.storage.items())

    def __contains__(self, key: str) -> bool:
        return key in self.storage

    def __iter__(self) -> Iterator[str]:
        return iter(self.storage)


class TransientStorageMixin:
    def get_or_create_transient_storage(self) -> TransientStorage:
        if "_transient_storage" not in self.__dict__:
            self.__dict__["_transient_storage"] = TransientStorage()
        return self.__dict__["_transient_storage"]


### SECURITY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def validate_token(token: str, secret_key: str) -> dict[str, Any]:
    payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    return payload


def create_access_token(
    subject: str | Any, expires_delta: timedelta, secret_key: str
) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_time(
    in_future: Optional[float] = None,
    units: Literal["hours", "minutes", "seconds", None] = None,
) -> float:
    if in_future is not None:
        if units == "hours":
            time_delta = in_future * 3600
        elif units == "minutes":
            time_delta = in_future * 60
        elif units == "seconds":
            time_delta = in_future
        else:
            time_delta = in_future
    else:
        time_delta = 0
    return time.time() + time_delta


def to_seconds(duration: float, units: Literal["hours", "minutes", "seconds"]) -> float:
    if units == "hours":
        return duration * 3600
    elif units == "minutes":
        return duration * 60
    elif units == "seconds":
        return duration
    else:
        raise ValueError(f"Invalid units: {units}")


def from_seconds(
    duration: float, units: Literal["hours", "minutes", "seconds"]
) -> float:
    if units == "hours":
        return duration / 3600
    elif units == "minutes":
        return duration / 60
    elif units == "seconds":
        return duration
    else:
        ValueError(f"Invalid units: {units}")


def format_time(
    seconds_since_epoch: float | None = None, 
    date_time_seperator: str = " ",
    include_day_of_week: bool = False,
    day_date_separator: str = " ",
    timezone: str | None = None
) -> str:
    """Format timestamp with optional timezone and day of week.
    
    Args:
        seconds_since_epoch: Unix timestamp (defaults to current time)
        date_time_seperator: Separator between date and time
        include_day_of_week: Whether to include day name
        day_date_separator: Separator between day name and date
        timezone: IANA timezone name (e.g. 'America/New_York'). If None, returns UTC with 'Z' suffix
    """
    if seconds_since_epoch is None:
        seconds_since_epoch = get_time()
    
    # Convert to datetime object
    dt = datetime.fromtimestamp(seconds_since_epoch, tz=ZoneInfo('UTC'))
    
    # Convert to target timezone if specified
    if timezone:
        dt = dt.astimezone(ZoneInfo(timezone))
    
    # Build format string
    format_str = "%Y-%m-%d"
    if include_day_of_week:
        format_str = f"%a{day_date_separator}" + format_str
    format_str += f"{date_time_seperator}%H:%M:%S"
    
    # Format the time
    formatted = dt.strftime(format_str)
    
    # Append timezone indicator
    if timezone:
        formatted += dt.strftime('%z')  # +HHMM or -HHMM format
    else:
        formatted += 'Z'  # UTC/Zulu time
        
    return formatted


def sanitize_for_jsonb(input_dict):
    def sanitize_string(s):
        result = []
        for char in s:
            code_point = ord(char)
            if (
                (0 <= code_point <= 8)
                or (11 <= code_point <= 31)
                or (code_point == 127)
            ):
                result.append(f"\\u{code_point:04x}")
            else:
                result.append(char)
        return "".join(result)

    def sanitize_value(value):
        if isinstance(value, str):
            return sanitize_string(value)
        elif isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(v) for v in value]
        else:
            return value

    sanitized_dict = sanitize_value(input_dict)

    # Convert to JSON string and back to ensure proper escaping of quotes, backslashes, etc.
    return json.loads(json.dumps(sanitized_dict))


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP code"""
    import random

    return "".join([str(random.randint(0, 9)) for _ in range(length)])
