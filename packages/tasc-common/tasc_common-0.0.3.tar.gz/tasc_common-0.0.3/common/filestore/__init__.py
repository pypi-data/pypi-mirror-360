from typing import Optional
from .interface import FileStore
from .s3 import S3Store
from .local import LocalStore
from ..config import common_settings as settings


def get_filestore(
    store_type: Optional[str] = None,
    filestore_root: Optional[str] = None,
) -> FileStore:
    """Get a filestore implementation based on configuration.

    Args:
        store_type: One of 's3' or 'local'. Defaults to settings.FILESTORE_TYPE
        filestore_root: directory or url for the filestore. Defaults to settings.FILESTORE_ROOT
    """
    store_type = store_type or settings.FILESTORE_TYPE
    filestore_root = filestore_root or settings.FILESTORE_ROOT

    if store_type == "s3":
        return S3Store(
            filestore_root=filestore_root,
            cloudfront_domain=settings.CLOUDFRONT_DOMAIN,
            cloudfront_key_id=settings.CLOUDFRONT_KEY_ID,
            cloudfront_private_key=settings.CLOUDFRONT_PRIVATE_KEY,
        )
    elif store_type == "local":
        return LocalStore(
            filestore_root=filestore_root,
        )
    else:
        raise ValueError(f"Unknown store type: {store_type}")


common_filestore = get_filestore()
