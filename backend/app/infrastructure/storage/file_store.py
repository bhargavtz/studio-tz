"""
NCD INAI - Unified File Storage Service
Combines R2 cloud storage with database metadata
Replaces the old file_manager.py
"""

import logging
from typing import Optional, Dict, List, BinaryIO
from uuid import UUID
from pathlib import Path
import io

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.storage.r2_client import r2_client
from app.core.exceptions import (
    FileUploadError, 
    FileDownloadError, 
    FileNotFoundError,
    StorageQuotaExceededError
)

logger = logging.getLogger(__name__)


class UnifiedFileStore:
    """
    Unified file storage combining R2 and database.
    
    This replaces the old file_manager.py with a production-ready
    implementation that stores files in R2 and metadata in database.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize file store with database session.
        
        Args:
            db: SQLAlchemy async session
        """
        self.db = db
        self.file_repo = FileRepository(db)
        self.user_repo = UserRepository(db)
        self.r2 = r2_client
    
    async def save_file(
        self,
        session_id: UUID,
        filename: str,
        content: str | bytes,
        file_type: str = "html",
        user_id: Optional[UUID] = None
    ) -> Dict[str, any]:
        """
        Save a file to R2 and record metadata in database.
        
        Args:
            session_id: Session UUID
            filename: File name (e.g., "index.html")
            content: File content (string or bytes)
            file_type: Type of file (html, css, js, etc.)
            user_id: Optional user ID for quota tracking
        
        Returns:
            Dict with file info including r2_url and database record
        
        Raises:
            FileUploadError: If upload fails
            StorageQuotaExceededError: If user exceeds quota
        """
        try:
            # Convert string to bytes
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            file_size = len(content_bytes)
            
            # Check user quota if user_id provided
            if user_id:
                user = await self.user_repo.get_by_id(user_id)
                if user:
                    remaining = user.storage_remaining_bytes  # Property, not method
                    if file_size > remaining:
                        raise StorageQuotaExceededError(
                            user_id=str(user_id),
                            usage=user.storage_used_bytes,
                            limit=user.storage_limit_bytes
                        )
            
            # Generate R2 key
            r2_key = f"sessions/{session_id}/{filename}"
            
            # Determine MIME type
            mime_type = self._get_mime_type(filename)
            
            # Upload to R2
            file_obj = io.BytesIO(content_bytes)
            r2_result = self.r2.upload_fileobj(
                file_obj,
                r2_key,
                mime_type
            )
            
            logger.info(f"✅ Uploaded {filename} to R2: {r2_key}")
            
            # Save metadata to database
            db_file = await self.file_repo.create(
                session_id=session_id,
                file_name=filename,
                file_path=r2_key,
                file_type=file_type,
                r2_key=r2_result['r2_key'],
                r2_url=r2_result['r2_url'],
                size_bytes=r2_result['size_bytes'],
                mime_type=mime_type
            )
            
            # Update user storage usage
            if user_id:
                await self.user_repo.update_storage_usage(user_id, file_size)
            
            return {
                'file_id': str(db_file.id),
                'filename': filename,
                'r2_url': r2_result['r2_url'],
                'r2_key': r2_result['r2_key'],
                'size_bytes': r2_result['size_bytes'],
                'file_type': file_type
            }
        
        except StorageQuotaExceededError:
            raise
        except Exception as e:
            logger.error(f"Failed to save file {filename}: {e}")
            raise FileUploadError(filename, str(e))
    
    async def get_file(
        self,
        session_id: UUID,
        filename: str
    ) -> Optional[bytes]:
        """
        Get file content from R2.
        
        Args:
            session_id: Session UUID
            filename: File name
        
        Returns:
            File content as bytes, or None if not found
        
        Raises:
            FileDownloadError: If download fails
        """
        try:
            # Get file metadata from database
            files = await self.file_repo.get_session_files(session_id)
            file_record = next((f for f in files if f.file_name == filename), None)
            
            if not file_record:
                logger.warning(f"File not found in database: {filename}")
                return None
            
            # Download from R2
            content = self.r2.get_file_content(file_record.r2_key)
            
            logger.info(f"✅ Downloaded {filename} from R2")
            return content
        
        except Exception as e:
            logger.error(f"Failed to get file {filename}: {e}")
            raise FileDownloadError(filename, str(e))
    
    async def get_file_url(
        self,
        session_id: UUID,
        filename: str
    ) -> Optional[str]:
        """
        Get public URL for a file.
        
        Args:
            session_id: Session UUID
            filename: File name
        
        Returns:
            Public R2 URL or None if not found
        """
        files = await self.file_repo.get_session_files(session_id)
        file_record = next((f for f in files if f.file_name == filename), None)
        
        if file_record:
            return file_record.r2_url
        
        return None
    
    async def list_session_files(
        self,
        session_id: UUID
    ) -> List[Dict[str, any]]:
        """
        List all files for a session.
        
        Args:
            session_id: Session UUID
        
        Returns:
            List of file info dicts
        """
        files = await self.file_repo.get_session_files(session_id)
        
        return [
            {
                'file_id': str(f.id),
                'filename': f.file_name,
                'file_type': f.file_type,
                'r2_url': f.r2_url,
                'size_bytes': f.size_bytes,
                'mime_type': f.mime_type,
                'created_at': f.created_at.isoformat()
            }
            for f in files
        ]
    
    async def delete_file(
        self,
        session_id: UUID,
        filename: str,
        user_id: Optional[UUID] = None
    ) -> bool:
        """
        Delete a file from R2 and database.
        
        Args:
            session_id: Session UUID
            filename: File name
            user_id: Optional user ID for quota tracking
        
        Returns:
            True if deleted, False if not found
        """
        try:
            # Get file record
            files = await self.file_repo.get_session_files(session_id)
            file_record = next((f for f in files if f.file_name == filename), None)
            
            if not file_record:
                return False
            
            # Delete from R2
            self.r2.delete_file(file_record.r2_key)
            
            # Update user storage usage
            if user_id:
                await self.user_repo.update_storage_usage(user_id, -file_record.size_bytes)
            
            # Delete from database
            await self.file_repo.delete(file_record.id)
            
            logger.info(f"✅ Deleted file: {filename}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete file {filename}: {e}")
            return False
    
    async def delete_session_files(
        self,
        session_id: UUID,
        user_id: Optional[UUID] = None
    ) -> int:
        """
        Delete all files for a session.
        
        Args:
            session_id: Session UUID
            user_id: Optional user ID for quota tracking
        
        Returns:
            Number of files deleted
        """
        try:
            # Get all files
            files = await self.file_repo.get_session_files(session_id)
            
            if not files:
                return 0
            
            # Calculate total size for quota
            total_size = sum(f.size_bytes for f in files)
            
            # Delete from R2
            r2_keys = [f.r2_key for f in files]
            self.r2.delete_files(r2_keys)
            
            # Update user storage usage
            if user_id and total_size > 0:
                await self.user_repo.update_storage_usage(user_id, -total_size)
            
            # Delete from database
            count = await self.file_repo.delete_session_files(session_id)
            
            logger.info(f"✅ Deleted {count} files for session {session_id}")
            return count
        
        except Exception as e:
            logger.error(f"Failed to delete session files: {e}")
            return 0
    
    def _get_mime_type(self, filename: str) -> str:
        """Determine MIME type from filename."""
        ext = Path(filename).suffix.lower()
        
        mime_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.zip': 'application/zip'
        }
        
        return mime_types.get(ext, 'application/octet-stream')


# Factory function for dependency injection
def get_file_store(db: AsyncSession) -> UnifiedFileStore:
    """
    Factory function to create UnifiedFileStore instance.
    
    Args:
        db: Database session
    
    Returns:
        UnifiedFileStore instance
    """
    return UnifiedFileStore(db)
