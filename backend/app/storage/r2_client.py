"""
NCD INAI - Cloudflare R2 Storage Client
"""

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
import mimetypes
import os
from pathlib import Path

from app.config import settings


class R2Client:
    """Cloudflare R2 Object Storage client (S3-compatible)."""
    
    def __init__(self):
        """Initialize R2 client with credentials from settings."""
        self.bucket_name = settings.r2_bucket_name
        self.public_url = settings.r2_public_url
        
        # Create S3 client configured for R2
        self.client = boto3.client(
            's3',
            endpoint_url=settings.r2_endpoint,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(
                signature_version='s3v4',
                region_name='auto'  # R2 uses 'auto' region
            )
        )
    
    def upload_file(
        self,
        file_path: str,
        object_key: str,
        content_type: Optional[str] = None
    ) -> dict:
        """
        Upload a file to R2.
        
        Args:
            file_path: Local path to file to upload
            object_key: R2 object key (path in bucket)
            content_type: MIME type (auto-detected if not provided)
        
        Returns:
            dict with 'r2_key' and 'r2_url'
        """
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or 'application/octet-stream'
        
        try:
            with open(file_path, 'rb') as f:
                self.client.upload_fileobj(
                    f,
                    self.bucket_name,
                    object_key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'CacheControl': 'public, max-age=31536000',  # 1 year cache
                    }
                )
            
            # Generate public URL
            public_url = f"{self.public_url}/{object_key}"
            
            return {
                'r2_key': object_key,
                'r2_url': public_url,
                'size_bytes': os.path.getsize(file_path)
            }
        
        except ClientError as e:
            raise Exception(f"Failed to upload file to R2: {str(e)}")
    
    def upload_fileobj(
        self,
        file_obj: BinaryIO,
        object_key: str,
        content_type: str = 'application/octet-stream'
    ) -> dict:
        """
        Upload a file object to R2.
        
        Args:
            file_obj: File-like object to upload
            object_key: R2 object key (path in bucket)
            content_type: MIME type
        
        Returns:
            dict with 'r2_key' and 'r2_url'
        """
        try:
            # Get file size before upload
            current_pos = file_obj.tell()
            file_obj.seek(0, 2)  # Seek to end
            size_bytes = file_obj.tell()
            file_obj.seek(current_pos)  # Reset to original position
            
            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'CacheControl': 'public, max-age=31536000',
                }
            )
            
            public_url = f"{self.public_url}/{object_key}"
            
            return {
                'r2_key': object_key,
                'r2_url': public_url,
                'size_bytes': size_bytes
            }
        
        except ClientError as e:
            raise Exception(f"Failed to upload file to R2: {str(e)}")
    
    def download_file(self, object_key: str, download_path: str):
        """
        Download a file from R2.
        
        Args:
            object_key: R2 object key
            download_path: Local path to save file
        """
        try:
            # Ensure directory exists
            Path(download_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.client.download_file(
                self.bucket_name,
                object_key,
                download_path
            )
        
        except ClientError as e:
            raise Exception(f"Failed to download file from R2: {str(e)}")
    
    def get_file_content(self, object_key: str) -> bytes:
        """
        Get file content from R2 as bytes.
        
        Args:
            object_key: R2 object key
        
        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return response['Body'].read()
        
        except ClientError as e:
            raise Exception(f"Failed to get file content from R2: {str(e)}")

    
    def delete_file(self, object_key: str):
        """
        Delete a file from R2.
        
        Args:
            object_key: R2 object key to delete
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
        
        except ClientError as e:
            raise Exception(f"Failed to delete file from R2: {str(e)}")
    
    def delete_files(self, object_keys: list[str]):
        """
        Delete multiple files from R2.
        
        Args:
            object_keys: List of R2 object keys to delete
        """
        if not object_keys:
            return
        
        try:
            objects = [{'Key': key} for key in object_keys]
            self.client.delete_objects(
                Bucket=self.bucket_name,
                Delete={'Objects': objects}
            )
        
        except ClientError as e:
            raise Exception(f"Failed to delete files from R2: {str(e)}")
    
    def get_file_url(self, object_key: str) -> str:
        """
        Get public URL for an R2 object.
        
        Args:
            object_key: R2 object key
        
        Returns:
            Public URL string
        """
        return f"{self.public_url}/{object_key}"
    
    def file_exists(self, object_key: str) -> bool:
        """
        Check if a file exists in R2.
        
        Args:
            object_key: R2 object key
        
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
        except ClientError:
            return False
    
    def get_file_metadata(self, object_key: str) -> dict:
        """
        Get metadata for an R2 object.
        
        Args:
            object_key: R2 object key
        
        Returns:
            Dictionary with metadata
        """
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            return {
                'content_type': response.get('ContentType'),
                'size_bytes': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag', '').strip('"'),
            }
        
        except ClientError as e:
            raise Exception(f"Failed to get file metadata: {str(e)}")


# Global R2 client instance
r2_client = R2Client()
