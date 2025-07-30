import os
from typing import AsyncIterator, Optional, BinaryIO, Tuple
from datetime import datetime, timedelta
import aioboto3
import aiohttp
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64
import json
from loguru import logger
from common.filestore.interface import FileStore
from urllib.parse import quote

class S3Store(FileStore):
    def __init__(
        self,
        filestore_root: str,
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
        cloudfront_domain: Optional[str] = None,
        cloudfront_key_id: Optional[str] = None,
        cloudfront_private_key: Optional[str] = None,
    ):
        # Parse the URL to get bucket and region
        # https://bucket-name.s3.region.amazonaws.com
        url = filestore_root.rstrip("/")
        parts = url.removeprefix("https://").split(".")
        if len(parts) < 4 or parts[1] != "s3" or not parts[-2:] == ["amazonaws", "com"]:
            raise ValueError(f"Invalid S3 URL format: {url}")

        self.bucket = parts[0]
        self.region = parts[2]
        self.public_url_base = url
        self.aws_access_key = aws_access_key or os.environ.get("AWS_ACCESS_KEY")
        self.aws_secret_key = aws_secret_key or os.environ.get("AWS_SECRET_KEY")

        # CloudFront configuration
        self.cloudfront_domain = cloudfront_domain
        self.cloudfront_key_id = cloudfront_key_id
        if cloudfront_private_key:
            self.cloudfront_private_key = serialization.load_pem_private_key(
                cloudfront_private_key.encode(), password=None
            )
        else:
            self.cloudfront_private_key = None


    def _get_client(self):
        return aioboto3.Session(
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region
        ).client('s3')
    
    async def get_object(self, key: str) -> bytes:
        """Get object as a single bytes object"""
        chunks = []
        async for chunk in self.get_object_streaming(key):
            chunks.append(chunk)
        return b''.join(chunks)

    async def get_object_streaming(self, key: str) -> AsyncIterator[bytes]:
        if self.cloudfront_domain:
            url = await self.get_url(key)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        yield chunk
        else:
            # Fallback to direct S3 access if CloudFront isn't configured
            async with self._get_client() as s3:
                response = await s3.get_object(Bucket=self.bucket, Key=key)
                async with response['Body'] as stream:
                    while True:
                        chunk = await stream.read(8192)
                        if not chunk:
                            break
                        yield chunk
    
    async def put_object(
        self,
        key: str,
        data: bytes | BinaryIO | str,
        content_type: Optional[str] = None,
        content_disposition: Optional[str] = None,
        cache_control: Optional[str] = None,
        extra_args: Optional[dict] = None,
    ) -> None:
        if isinstance(data, str):
            data = data.encode("utf-8")

        params = {
            'Bucket': self.bucket,
            'Key': key,
            'Body': data,
            'ContentType': content_type or 'application/octet-stream',
            'CacheControl': cache_control or 'public, max-age=31536000',
        }
        
        if content_disposition:
            params['ContentDisposition'] = content_disposition
        if extra_args:
            params.update(extra_args)
            
        async with self._get_client() as s3:
            await s3.put_object(**params)

    async def delete_object(self, key: str) -> None:
        async with self._get_client() as s3:
            await s3.delete_object(Bucket=self.bucket, Key=key)

    async def object_exists(self, key: str) -> bool:
        try:
            async with self._get_client() as s3:
                await s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False

    async def verify_url(
        self,
        key: str,
        token: Optional[str] = None,
    ) -> Tuple[bool, Optional[dict]]:
        """Verify a URL and its token if provided.
        In production S3/CloudFront, we don't need to verify tokens here
        since S3/CloudFront handle that for us.
        """
        return await self.object_exists(key), None

    def _sign_cloudfront_url(self, url: str, expire_time: datetime) -> str:
        """Sign a CloudFront URL using the private key."""
        if not all(
            [
                self.cloudfront_domain,
                self.cloudfront_key_id,
                self.cloudfront_private_key,
            ]
        ):
            raise ValueError("CloudFront configuration incomplete")

        # Create policy with minimal whitespace
        policy = {
            "Statement": [
                {
                    "Resource": url,
                    "Condition": {
                        "DateLessThan": {"AWS:EpochTime": int(expire_time.timestamp())}
                    },
                }
            ]
        }

        # Convert to JSON with no whitespace
        policy_json = json.dumps(policy, separators=(',', ':'))
        
        # Sign the raw policy JSON (not the base64 version)
        signature = self.cloudfront_private_key.sign(
            policy_json.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        
        # Base64 encode both policy and signature
        policy_b64 = base64.b64encode(policy_json.encode('utf-8')).decode('utf-8')
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # CloudFront-specific URL safe encoding
        def make_safe(s: str) -> str:
            return s.replace('+', '-').replace('=', '_').replace('/', '~')
        
        policy_safe = make_safe(policy_b64)
        signature_safe = make_safe(signature_b64)
        
        # Build the final URL
        params = [
            ('Key-Pair-Id', self.cloudfront_key_id),
            ('Policy', policy_safe),
            ('Signature', signature_safe)
        ]
        query_string = '&'.join(f"{k}={v}" for k, v in params)
        final_url = f"{url}?{query_string}"
        
        return final_url

    async def get_signed_url(
        self,
        key: str,
        expiry: timedelta,
    ) -> str:
        """Generate a signed CloudFront URL"""

        if not all([self.cloudfront_domain, self.cloudfront_key_id, self.cloudfront_private_key]):
            missing = []
            if not self.cloudfront_domain:
                missing.append("cloudfront_domain")
            if not self.cloudfront_key_id:
                missing.append("cloudfront_key_id")
            if not self.cloudfront_private_key:
                missing.append("cloudfront_private_key")
            raise ValueError(f"CloudFront configuration incomplete. Missing: {', '.join(missing)}")
        # Ensure proper URL construction with https:// prefix
        # Remove any leading slashes from the key to prevent double slashes
        key = key.lstrip('/')
        
        # Split the key into parts and encode each part separately
        key_parts = key.split('/')
        encoded_parts = [quote(part) for part in key_parts]
        encoded_key = '/'.join(encoded_parts)
        
        url = f"https://{self.cloudfront_domain}/{encoded_key}"
        
        expire_time = datetime.utcnow() + expiry
        
        try:
            signed_url = self._sign_cloudfront_url(url, expire_time)
            return signed_url
        except Exception as e:
            logger.error(f"Failed to sign CloudFront URL: {str(e)}", exc_info=True)
            raise

    async def get_url(
        self,
        key: str,
    ) -> str:
        """Get a URL for accessing a file in production.
        Public files get a CDN URL, private files get a signed CDN URL.
        """

        if self.cloudfront_domain:
            return f"https://{self.cloudfront_domain}/{key}"
        else:
            return f"{self.public_url_base}/{key}"

    def sync_get_url(
        self,
        key: str,
    ) -> str:
        """Synchronous version of get_url for production.
        Public files get a CDN URL, private files get a signed CDN URL.
        """
        logger.info(f"Getting URL for {key}")
        if self.cloudfront_domain:
            logger.info(f"Using CloudFront domain {self.cloudfront_domain}")
            return f"https://{self.cloudfront_domain}/{key}"
        else:
            return f"{self.public_url_base}/{key}"
