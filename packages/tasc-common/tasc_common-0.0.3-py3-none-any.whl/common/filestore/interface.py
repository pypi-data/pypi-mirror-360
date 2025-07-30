from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, BinaryIO, Tuple
from datetime import timedelta

class FileStore(ABC):
    """Abstract interface for file storage operations"""
    
    @abstractmethod
    async def get_object(self, key: str) -> AsyncIterator[bytes]:
        """Get an object from storage"""
        pass
    
    @abstractmethod
    async def put_object(
        self, 
        key: str, 
        data: bytes | BinaryIO | str,
        content_type: Optional[str] = None,
        content_disposition: Optional[str] = None,
        cache_control: Optional[str] = None,
    ) -> None:
        """Put an object into storage"""
        pass
    
    @abstractmethod
    async def delete_object(self, key: str) -> None:
        """Delete an object from storage"""
        pass
    
    @abstractmethod
    async def object_exists(self, key: str) -> bool:
        """Check if an object exists"""
        pass
    
    @abstractmethod
    async def get_url(
        self,
        key: str,
    ) -> str:
        """Get a URL for accessing a file. The implementation will decide:
        - For public files: Return a CDN/public URL
        - For private files: Return a signed URL with appropriate expiry
        - For local development: Handle appropriately for the dev environment
        """
        pass

    @abstractmethod
    def sync_get_url(
        self,
        key: str,
    ) -> str:
        """Synchronous version of get_url. The implementation will decide:
        - For public files: Return a CDN/public URL
        - For private files: Return a signed URL with appropriate expiry
        - For local development: Handle appropriately for the dev environment
        """
        pass
    
    @abstractmethod
    async def get_signed_url(
        self,
        key: str,
        expiry: timedelta,
    ) -> str:
        """Get a signed URL for temporary access to a private object"""
        pass



    @abstractmethod
    async def verify_url(
        self,
        key: str,
        token: Optional[str] = None,
    ) -> Tuple[bool, Optional[dict]]:
        """Verify a URL and its token if provided.
        Returns:
        - bool: Whether the URL is valid and accessible
        - dict: Optional claims from token verification (content_type, etc)
        """
        pass 
