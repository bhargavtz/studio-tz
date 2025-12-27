"""
NCD INAI - File Repository Implementation
Database operations for generated files
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.infrastructure.repositories import IFileRepository
from app.database.models import GeneratedFile


class FileRepository(IFileRepository):
    """SQLAlchemy implementation of file repository."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        session_id: UUID,
        file_name: str,
        file_path: str,
        file_type: str,
        r2_key: str,
        r2_url: str,
        size_bytes: int,
        mime_type: str
    ) -> GeneratedFile:
        """Create file record."""
        file = GeneratedFile(
            session_id=session_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            r2_key=r2_key,
            r2_url=r2_url,
            size_bytes=size_bytes,
            mime_type=mime_type
        )
        self.db.add(file)
        await self.db.commit()
        await self.db.refresh(file)
        return file
    
    async def get_by_id(self, file_id: UUID) -> Optional[GeneratedFile]:
        """Get file by ID."""
        result = await self.db.execute(
            select(GeneratedFile).where(GeneratedFile.id == file_id)
        )
        return result.scalar_one_or_none()
    
    async def get_session_files(self, session_id: UUID) -> List[GeneratedFile]:
        """Get all files for a session."""
        result = await self.db.execute(
            select(GeneratedFile)
            .where(GeneratedFile.session_id == session_id)
            .order_by(GeneratedFile.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def delete(self, file_id: UUID) -> bool:
        """Delete file record."""
        file = await self.get_by_id(file_id)
        if not file:
            return False
        
        await self.db.delete(file)
        await self.db.commit()
        return True
    
    async def delete_session_files(self, session_id: UUID) -> int:
        """Delete all files for a session. Returns count of deleted files."""
        result = await self.db.execute(
            delete(GeneratedFile).where(GeneratedFile.session_id == session_id)
        )
        await self.db.commit()
        return result.rowcount or 0
