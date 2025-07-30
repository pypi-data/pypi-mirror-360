import uuid
from enum import Enum
import traceback

from loguru import logger
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Column

from common.core.utils import get_time
from common.database.base_models import BaseSQLModel


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogSQLModel(BaseSQLModel):
    __tablename__ = "log"
    id: str = Field(default_factory=lambda: f"log_{uuid.uuid4().hex}", primary_key=True)

    # Meta
    created_at: float = Field(default_factory=get_time)

    # Main attributes
    level: LogLevel = Field(default=LogLevel.INFO)
    source: str | None = Field(default=None)
    meta: dict | None = Field(sa_column=Column(JSONB), default=None)
    message: str | None = Field(default=None)
    payload: dict | None = Field(sa_column=Column(JSONB), default=None)

    @classmethod
    async def robust_create(cls, robust: bool = True, **kwargs):
        try:
            return await cls.create(**kwargs)
        except Exception as e:
            logger.exception(f"Error creating log: {e}")
            if not robust:
                raise

    @classmethod
    async def error(
        cls,
        error: Exception,
        message: str | None = None,
        source: str | None = None,
        meta: dict | None = None,
        payload: dict | None = None,
        include_traceback: bool = True,
        robust: bool = True,
    ) -> "LogSQLModel":
        """Log an exception with its traceback."""
        error_info = {
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            **(payload or {}),
        }

        if include_traceback:
            error_info["traceback"] = traceback.format_exc()

        return await cls.robust_create(
            level=LogLevel.ERROR,
            message=message or str(error),
            source=source,
            payload=error_info,
            meta=meta,
            robust=robust,
        )

    @classmethod
    async def info(
        cls,
        message: str,
        source: str | None = None,
        meta: dict | None = None,
        payload: dict | None = None,
        robust: bool = True,
    ) -> "LogSQLModel":
        """Log any event with custom level and metadata."""
        return await cls.robust_create(
            level=LogLevel.INFO,
            source=source,
            message=message,
            meta=meta,
            payload=payload,
            robust=robust,
        )

    @classmethod
    async def critical(
        cls,
        message: str,
        source: str | None = None,
        meta: dict | None = None,
        payload: dict | None = None,
        robust: bool = True,
    ) -> "LogSQLModel":
        """Convenience method for critical logs."""
        return await cls.robust_create(
            message=message,
            level=LogLevel.CRITICAL,
            source=source,
            meta=meta,
            payload=payload,
            robust=robust,
        )

    @classmethod
    async def debug(
        cls,
        message: str,
        source: str | None = None,
        meta: dict | None = None,
        payload: dict | None = None,
        robust: bool = True,
    ) -> "LogSQLModel":
        """Convenience method for debug logs."""
        return await cls.robust_create(
            message=message,
            level=LogLevel.DEBUG,
            source=source,
            meta=meta,
            payload=payload,
            robust=robust,
        )
