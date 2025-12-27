"""
NCD INAI - Storage Quota Service
Manages user storage quotas and enforces R2 upload limits
"""

from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
import uuid

from app.database.models import User, Session as DBSession, GeneratedFile, Asset
from app.database.connection import get_db


# Storage constants
BYTES_IN_MB = 1024 * 1024
DEFAULT_QUOTA_MB = 200
DEFAULT_QUOTA_BYTES = DEFAULT_QUOTA_MB * BYTES_IN_MB  # 200MB


class StorageQuotaService:
    """Manages user storage quotas for R2 uploads."""
    
    @staticmethod
    def bytes_to_mb(bytes_value: int) -> float:
        """Convert bytes to megabytes (2 decimal places)."""
        return round(bytes_value / BYTES_IN_MB, 2)
    
    @staticmethod
    def mb_to_bytes(mb_value: float) -> int:
        """Convert megabytes to bytes."""
        return int(mb_value * BYTES_IN_MB)
    
    async def check_user_quota(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        required_bytes: int
    ) -> Tuple[bool, dict]:
        """
        Check if user has enough storage quota for an upload.
        
        Returns:
            Tuple of (can_upload: bool, quota_info: dict)
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False, {"error": "User not found"}
        
        remaining = user.storage_remaining_bytes
        can_upload = remaining >= required_bytes
        
        quota_info = {
            "can_upload": can_upload,
            "storage_used_bytes": user.storage_used_bytes,
            "storage_limit_bytes": user.storage_limit_bytes,
            "storage_remaining_bytes": remaining,
            "storage_used_mb": self.bytes_to_mb(user.storage_used_bytes),
            "storage_limit_mb": self.bytes_to_mb(user.storage_limit_bytes),
            "storage_remaining_mb": self.bytes_to_mb(remaining),
            "usage_percentage": round(user.storage_usage_percentage, 1),
            "required_bytes": required_bytes,
            "required_mb": self.bytes_to_mb(required_bytes),
        }
        
        if not can_upload:
            quota_info["error"] = (
                f"Storage limit exceeded. You've used {quota_info['storage_used_mb']}MB "
                f"of {quota_info['storage_limit_mb']}MB. "
                f"This upload requires {quota_info['required_mb']}MB but only "
                f"{quota_info['storage_remaining_mb']}MB is available. "
                f"Please delete old projects to free up space."
            )
        
        return can_upload, quota_info
    
    async def update_user_quota(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        delta_bytes: int,
        session_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Update user's storage usage after upload/delete.
        
        Args:
            user_id: User UUID
            delta_bytes: Positive for upload, negative for delete
            session_id: Optional session to update total_size_bytes
        
        Returns:
            True if successful
        """
        # Update user storage
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(storage_used_bytes=User.storage_used_bytes + delta_bytes)
        )
        
        # Update session total if provided
        if session_id:
            await db.execute(
                update(DBSession)
                .where(DBSession.id == session_id)
                .values(total_size_bytes=DBSession.total_size_bytes + delta_bytes)
            )
        
        await db.commit()
        return True
    
    async def get_quota_summary(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> dict:
        """
        Get detailed storage quota summary for user.
        
        Returns:
            Dictionary with storage details and top projects
        """
        # Get user
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {"error": "User not found"}
        
        # Get top storage-consuming sessions
        top_sessions = await db.execute(
            select(
                DBSession.id,
                DBSession.project_title,
                DBSession.total_size_bytes
            )
            .where(DBSession.user_id == user_id)
            .where(DBSession.total_size_bytes > 0)
            .order_by(DBSession.total_size_bytes.desc())
            .limit(5)
        )
        
        top_projects = []
        for session in top_sessions.fetchall():
            percentage = (session.total_size_bytes / user.storage_used_bytes * 100) if user.storage_used_bytes > 0 else 0
            top_projects.append({
                "session_id": str(session.id),
                "project_title": session.project_title or "Untitled",
                "total_size_bytes": session.total_size_bytes,
                "total_size_mb": f"{self.bytes_to_mb(session.total_size_bytes):.2f}",
                "percentage_of_used": round(percentage, 1)
            })
        
        # Count total projects
        count_result = await db.execute(
            select(func.count(DBSession.id))
            .where(DBSession.user_id == user_id)
        )
        total_projects = count_result.scalar()
        
        return {
            "storage_used_bytes": user.storage_used_bytes,
            "storage_limit_bytes": user.storage_limit_bytes,
            "storage_remaining_bytes": user.storage_remaining_bytes,
            "storage_used_mb": f"{self.bytes_to_mb(user.storage_used_bytes):.2f}",
            "storage_limit_mb": f"{self.bytes_to_mb(user.storage_limit_bytes):.2f}",
            "storage_remaining_mb": f"{self.bytes_to_mb(user.storage_remaining_bytes):.2f}",
            "usage_percentage": round(user.storage_usage_percentage, 1),
            "total_projects": total_projects,
            "top_projects": top_projects,
            "is_near_limit": user.storage_usage_percentage >= 80,
            "is_at_limit": user.storage_usage_percentage >= 95,
        }
    
    async def calculate_session_size(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> int:
        """Calculate total size of all files in a session."""
        # Sum generated files
        files_result = await db.execute(
            select(func.coalesce(func.sum(GeneratedFile.size_bytes), 0))
            .where(GeneratedFile.session_id == session_id)
        )
        files_size = files_result.scalar() or 0
        
        # Sum assets
        assets_result = await db.execute(
            select(func.coalesce(func.sum(Asset.size_bytes), 0))
            .where(Asset.session_id == session_id)
        )
        assets_size = assets_result.scalar() or 0
        
        return files_size + assets_size
    
    async def recalculate_user_storage(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> int:
        """
        Recalculate total storage for user from all files.
        Use this to fix any inconsistencies.
        """
        # Calculate from generated files
        files_result = await db.execute(
            select(func.coalesce(func.sum(GeneratedFile.size_bytes), 0))
            .select_from(GeneratedFile)
            .join(DBSession, GeneratedFile.session_id == DBSession.id)
            .where(DBSession.user_id == user_id)
        )
        files_total = files_result.scalar() or 0
        
        # Calculate from assets
        assets_result = await db.execute(
            select(func.coalesce(func.sum(Asset.size_bytes), 0))
            .where(Asset.user_id == user_id)
        )
        assets_total = assets_result.scalar() or 0
        
        total = files_total + assets_total
        
        # Update user
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(storage_used_bytes=total)
        )
        await db.commit()
        
        return total
    
    async def recalculate_session_size(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> int:
        """Recalculate and update session's total_size_bytes."""
        total = await self.calculate_session_size(db, session_id)
        
        await db.execute(
            update(DBSession)
            .where(DBSession.id == session_id)
            .values(total_size_bytes=total)
        )
        await db.commit()
        
        return total


# Global service instance
storage_quota_service = StorageQuotaService()
