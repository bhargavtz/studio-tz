"""
NCD INAI - Error Handler Middleware
Centralized exception handling for consistent API responses
"""

import logging
from typing import Union
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import NCDException

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup all exception handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(NCDException)
    async def ncd_exception_handler(request: Request, exc: NCDException) -> JSONResponse:
        """
        Handle all custom NCD exceptions.
        Returns consistent error response format.
        """
        logger.error(
            f"NCDException: {exc.error_code} - {exc.message}",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "details": exc.details,
                "path": request.url.path
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                },
                "path": request.url.path
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle FastAPI request validation errors.
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Validation error: {len(errors)} field(s)",
            extra={
                "errors": errors,
                "path": request.url.path
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {
                        "errors": errors
                    }
                },
                "path": request.url.path
            }
        )
    
    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: PydanticValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors.
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Pydantic validation error: {len(errors)} field(s)",
            extra={
                "errors": errors,
                "path": request.url.path
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Data validation failed",
                    "details": {
                        "errors": errors
                    }
                },
                "path": request.url.path
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Catch-all handler for unhandled exceptions.
        Logs the error and returns a generic error response.
        """
        logger.exception(
            f"Unhandled exception: {type(exc).__name__}",
            extra={
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "path": request.url.path
            },
            exc_info=exc
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": {
                        "type": type(exc).__name__
                    }
                },
                "path": request.url.path
            }
        )
    
    logger.info("✅ Exception handlers configured")


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    details: dict = None
) -> JSONResponse:
    """
    Helper function to create standardized error responses.
    
    Args:
        error_code: Error code identifier
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details
    
    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {}
            }
        }
    )
