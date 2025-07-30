import os
import aiofiles
from typing import AsyncIterator, Optional, BinaryIO, Tuple
from common.config import common_settings as settings
from datetime import datetime, timedelta
import jwt
from pathlib import Path

from loguru import logger
from common.filestore.interface import FileStore


class LocalStore(FileStore):
    def __init__(
        self,
        filestore_root: str,
        public_url_base: Optional[str] = None,
        signing_secret: Optional[str] = None,
    ):
        # Parse the filestore_root to handle file:// URLs
        if filestore_root.startswith("file://"):
            # Remove file:// prefix and ensure proper path
            root_path = filestore_root.replace("file://", "")
            # Handle both absolute paths (/tmp/...) and relative paths (tmp/...)
            if not root_path.startswith("/"):
                root_path = "/" + root_path
        else:
            root_path = filestore_root

        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)
        self.public_url_base = public_url_base or f"{settings.server_host}/files"
        self.signing_secret = signing_secret or settings.SECRET_KEY

    def _get_path(self, key: str) -> Path:
        path = self.root / key
        logger.debug(f"Getting path for key: {key}, path: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _sign_url(self, url: str, expiry: timedelta, **claims) -> str:
        """Sign a URL with JWT, including expiry and optional claims"""
        token = jwt.encode(
            {"url": url, "exp": datetime.utcnow() + expiry, **claims},
            self.signing_secret,
            algorithm="HS256",
        )
        return f"{url}?token={token}"

    def _verify_signature(self, token: str) -> dict:
        """Verify a signed URL token"""
        try:
            return jwt.decode(token, self.signing_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ValueError("URL has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid signature")

    async def get_object(self, key: str) -> AsyncIterator[bytes]:
        path = self._get_path(key)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {key}")

        async with aiofiles.open(path, "rb") as f:
            while chunk := await f.read(8192):  # 8KB chunks
                yield chunk

    async def put_object(
        self,
        key: str,
        data: bytes | BinaryIO | str,
        content_type: Optional[str] = None,
        content_disposition: Optional[str] = None,
        cache_control: Optional[str] = None,
    ) -> None:
        logger.debug(f"Putting object into local store: {key}")
        path = self._get_path(key)
        logger.debug(f"Path: {path}")

        if isinstance(data, str):
            data = data.encode("utf-8")

        if isinstance(data, bytes):
            async with aiofiles.open(path, "wb") as f:
                await f.write(data)
        else:
            # Handle file-like objects
            async with aiofiles.open(path, "wb") as f:
                while chunk := data.read(8192):
                    await f.write(chunk)

    async def delete_object(self, key: str) -> None:
        path = self._get_path(key)
        if path.exists():
            path.unlink()

    async def object_exists(self, key: str) -> bool:
        return self._get_path(key).exists()

    async def get_signed_url(
        self,
        key: str,
        expiry: timedelta,
    ) -> str:
        """Generate a signed URL with JWT"""
        if not await self.object_exists(key):
            raise FileNotFoundError(f"File not found: {key}")
        return self._sign_url(f"{self.public_url_base}/{key}", expiry)

    async def get_url(
        self,
        key: str,
    ) -> str:
        """Get a URL for accessing a file in local development.
        Public files get a direct URL, private files get a signed URL.
        """
        if not await self.object_exists(key):
            raise FileNotFoundError(f"File not found: {key}")

        if key.startswith("public/"):
            return f"{self.public_url_base}/{key}"
        else:
            return await self.get_signed_url(
                key=key,
                expiry=timedelta(minutes=15),
            )

    def sync_get_url(
        self,
        key: str,
    ) -> str:
        """Synchronous version of get_url for local development.
        Public files get a direct URL, private files get a signed URL.
        """
        path = self._get_path(key)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {key}")

        if key.startswith('public/'):
            return f"{self.public_url_base}/{key}"
        else:
            # For sync version, we'll use a longer expiry since we can't await
            url = f"{self.public_url_base}/{key}"
            expire_time = datetime.utcnow() + timedelta(hours=1)
            return self._sign_url(url, expire_time)

    async def verify_url(
        self,
        key: str,
        token: Optional[str] = None,
    ) -> Tuple[bool, Optional[dict]]:
        """Verify a URL and its token if provided."""
        if not await self.object_exists(key):
            return False, None

        # Public files don't need token verification
        if key.startswith("public/"):
            return True, None

        # Private files require a valid token
        if not token:
            return False, None

        try:
            claims = self._verify_signature(token)
            if claims["url"] != f"{self.public_url_base}/{key}":
                return False, None
            return True, claims
        except ValueError:
            return False, None
