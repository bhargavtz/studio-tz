"""
NCD INAI - Custom Exception Classes
Production-grade exception hierarchy for better error handling
"""

from typing import Optional, Dict, Any


class NCDException(Exception):
    """
    Base exception for all NCD INAI errors.
    All custom exceptions should inherit from this.
    """
    def __init__(
        self, 
        message: str, 
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


# ==================== Session Errors ====================

class SessionNotFoundError(NCDException):
    """Raised when a session is not found."""
    def __init__(self, session_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Session not found: {session_id}",
            status_code=404,
            error_code="SESSION_NOT_FOUND",
            details=details or {"session_id": session_id}
        )


class SessionCreationError(NCDException):
    """Raised when session creation fails."""
    def __init__(self, message: str = "Failed to create session", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="SESSION_CREATION_FAILED",
            details=details
        )


class SessionUpdateError(NCDException):
    """Raised when session update fails."""
    def __init__(self, session_id: str, message: str = "Failed to update session", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="SESSION_UPDATE_FAILED",
            details=details or {"session_id": session_id}
        )


# ==================== Blueprint Errors ====================

class BlueprintError(NCDException):
    """Base exception for blueprint-related errors."""
    pass


class BlueprintNotFoundError(BlueprintError):
    """Raised when blueprint is not found for a session."""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Blueprint not found for session: {session_id}",
            status_code=404,
            error_code="BLUEPRINT_NOT_FOUND",
            details={"session_id": session_id}
        )


class BlueprintGenerationError(BlueprintError):
    """Raised when blueprint generation fails."""
    def __init__(self, message: str = "Blueprint generation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="BLUEPRINT_GENERATION_FAILED",
            details=details
        )


class BlueprintAlreadyConfirmedError(BlueprintError):
    """Raised when trying to modify a confirmed blueprint."""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Blueprint already confirmed for session: {session_id}",
            status_code=400,
            error_code="BLUEPRINT_ALREADY_CONFIRMED",
            details={"session_id": session_id}
        )


# ==================== Generation Errors ====================

class GenerationError(NCDException):
    """Base exception for website generation errors."""
    pass


class WebsiteGenerationError(GenerationError):
    """Raised when website generation fails."""
    def __init__(self, message: str = "Website generation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="WEBSITE_GENERATION_FAILED",
            details=details
        )


class CodeValidationError(GenerationError):
    """Raised when generated code validation fails."""
    def __init__(self, validation_errors: Dict[str, Any]):
        super().__init__(
            message="Generated code validation failed",
            status_code=422,
            error_code="CODE_VALIDATION_FAILED",
            details={"validation_errors": validation_errors}
        )


# ==================== Storage Errors ====================

class StorageError(NCDException):
    """Base exception for storage-related errors."""
    pass


class FileUploadError(StorageError):
    """Raised when file upload to R2 fails."""
    def __init__(self, filename: str, message: str = "File upload failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to upload file: {filename}. {message}",
            status_code=500,
            error_code="FILE_UPLOAD_FAILED",
            details=details or {"filename": filename}
        )


class FileDownloadError(StorageError):
    """Raised when file download from R2 fails."""
    def __init__(self, filename: str, message: str = "File download failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to download file: {filename}. {message}",
            status_code=500,
            error_code="FILE_DOWNLOAD_FAILED",
            details=details or {"filename": filename}
        )


class FileNotFoundError(StorageError):
    """Raised when a file is not found in storage."""
    def __init__(self, filename: str):
        super().__init__(
            message=f"File not found: {filename}",
            status_code=404,
            error_code="FILE_NOT_FOUND",
            details={"filename": filename}
        )


class StorageQuotaExceededError(StorageError):
    """Raised when storage quota is exceeded."""
    def __init__(self, user_id: str, usage: int, limit: int):
        super().__init__(
            message=f"Storage quota exceeded. Usage: {usage} bytes, Limit: {limit} bytes",
            status_code=413,
            error_code="STORAGE_QUOTA_EXCEEDED",
            details={
                "user_id": user_id,
                "usage_bytes": usage,
                "limit_bytes": limit
            }
        )


# ==================== Validation Errors ====================

class ValidationError(NCDException):
    """Raised when input validation fails."""
    def __init__(self, field: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Validation failed for '{field}': {message}",
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details or {"field": field, "error": message}
        )


# ==================== Authentication Errors ====================

class AuthenticationError(NCDException):
    """Base exception for authentication errors."""
    pass


class InvalidTokenError(AuthenticationError):
    """Raised when authentication token is invalid."""
    def __init__(self, message: str = "Invalid authentication token"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="INVALID_TOKEN"
        )


class UnauthorizedError(AuthenticationError):
    """Raised when user is not authorized to perform an action."""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="UNAUTHORIZED"
        )


# ==================== AI/LLM Errors ====================

class AIError(NCDException):
    """Base exception for AI/LLM related errors."""
    pass


class LLMRequestError(AIError):
    """Raised when LLM request fails."""
    def __init__(self, provider: str, message: str = "LLM request failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{provider} request failed: {message}",
            status_code=502,
            error_code="LLM_REQUEST_FAILED",
            details=details or {"provider": provider}
        )


class LLMTimeoutError(AIError):
    """Raised when LLM request times out."""
    def __init__(self, provider: str, timeout: int):
        super().__init__(
            message=f"{provider} request timed out after {timeout} seconds",
            status_code=504,
            error_code="LLM_TIMEOUT",
            details={"provider": provider, "timeout_seconds": timeout}
        )
