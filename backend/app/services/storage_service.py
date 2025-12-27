"""
NCD INAI - Integrated Storage Service
Handles both R2 file storage and database metadata
"""

from typing import BinaryIO, Optional
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from app.storage.r2_client import r2_client
from app.database import crud


class IntegratedStorageService:
    """Service that coordinates R2 storage and database metadata."""
    
    def __init__(self):
        self.r2 = r2_client
    
    async def save_generated_file(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        file_content: str | bytes,
        file_name: str,
        file_type: str,  # 'html', 'css', 'js', 'json'
        mime_type: str = 'text/html'
    ) -> dict:
        """
        Save a generated file to R2 and record metadata in database.
        
        Args:
            db: Database session
            session_id: Session UUID
            file_content: File content (string or bytes)
            file_name: Original filename (e.g., 'index.html')
            file_type: Type of file for categorization
            mime_type: MIME type for the file
        
        Returns:
            dict with file info including r2_url and database record
        """
        # Convert string to bytes if needed
        if isinstance(file_content, str):
            content_bytes = file_content.encode('utf-8')
        else:
            content_bytes = file_content
        
        # Generate R2 key (path in bucket)
        r2_key = f"sessions/{session_id}/{file_name}"
        
        # Upload to R2
        import io
        file_obj = io.BytesIO(content_bytes)
        r2_result = self.r2.upload_fileobj(
            file_obj,
            r2_key,
            mime_type
        )
        
        # Save metadata to database
        db_file = await crud.create_generated_file(
            db=db,
            session_id=session_id,
            file_name=file_name,
            file_path=r2_key,
            file_type=file_type,
            r2_key=r2_result['r2_key'],
            r2_url=r2_result['r2_url'],
            size_bytes=r2_result['size_bytes'],
            mime_type=mime_type
        )
        
        return {
            'file_id': str(db_file.id),
            'r2_url': r2_result['r2_url'],
            'r2_key': r2_result['r2_key'],
            'size_bytes': r2_result['size_bytes'],
            'file_name': file_name,
            'file_type': file_type
        }
    
    async def save_multiple_files(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        files: list[dict]
    ) -> list[dict]:
        """
        Save multiple generated files at once.
        
        Args:
            files: List of dicts with keys: content, filename, file_type, mime_type
        
        Returns:
            List of saved file info dicts
        """
        results = []
        for file_info in files:
            result = await self.save_generated_file(
                db=db,
                session_id=session_id,
                file_content=file_info['content'],
                file_name=file_info['filename'],
                file_type=file_info.get('file_type', 'html'),
                mime_type=file_info.get('mime_type', 'text/html')
            )
            results.append(result)
        return results
    
    async def get_session_files(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> list[dict]:
        """Get all files for a session with their R2 URLs."""
        files = await crud.get_session_files(db, session_id)
        return [
            {
                'file_id': str(f.id),
                'file_name': f.file_name,
                'file_type': f.file_type,
                'r2_url': f.r2_url,
                'size_bytes': f.size_bytes,
                'created_at': f.created_at.isoformat()
            }
            for f in files
        ]
    
    async def delete_session_files(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ):
        """Delete all files for a session from R2 and database."""
        # Get file records
        files = await crud.get_session_files(db, session_id)
        
        # Delete from R2
        r2_keys = [f.r2_key for f in files]
        if r2_keys:
            self.r2.delete_files(r2_keys)
        
        # Delete from database
        await crud.delete_session_files(db, session_id)


# Global instance
storage_service = IntegratedStorageService()
