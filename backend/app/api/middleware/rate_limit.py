"""
NCD INAI - Rate Limiting Middleware
Prevent abuse and ensure fair usage
"""

import logging
import time
from typing import Dict, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        
        # Store: {client_id: [(timestamp, request_count)]}
        self.requests: Dict[str, list] = defaultdict(list)
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier from request."""
        # Try to get user ID from headers first
        user_id = request.headers.get("X-Clerk-User-Id")
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get first IP from chain
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"ip:{client_ip}"
    
    def _clean_old_requests(self, client_id: str, current_time: float) -> None:
        """Remove requests older than the window."""
        cutoff_time = current_time - self.window_seconds
        self.requests[client_id] = [
            (ts, count) for ts, count in self.requests[client_id]
            if ts > cutoff_time
        ]
    
    def _is_rate_limited(self, client_id: str) -> Tuple[bool, int, int]:
        """
        Check if client has exceeded rate limit.
        
        Returns:
            (is_limited, current_count, limit)
        """
        current_time = time.time()
        
        # Clean old requests
        self._clean_old_requests(client_id, current_time)
        
        # Count requests in current window
        total_requests = sum(count for _, count in self.requests[client_id])
        
        # Check if limit exceeded
        is_limited = total_requests >= self.requests_per_minute
        
        return is_limited, total_requests, self.requests_per_minute
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Check rate limit
        is_limited, current_count, limit = self._is_rate_limited(client_id)
        
        if is_limited:
            logger.warning(
                f"Rate limit exceeded for {client_id}",
                extra={
                    "client_id": client_id,
                    "current_count": current_count,
                    "limit": limit,
                    "path": request.url.path
                }
            )
            
            return Response(
                content='{"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests. Please try again later."}}',
                status_code=429,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + self.window_seconds))
                }
            )
        
        # Record this request
        self.requests[client_id].append((current_time, 1))
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, limit - (current_count + 1))
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response


def setup_rate_limiting(app, requests_per_minute: int = 60):
    """
    Setup rate limiting middleware.
    
    Args:
        app: FastAPI application
        requests_per_minute: Maximum requests per minute per client
    """
    app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute)
    logger.info(f"✅ Rate limiting configured: {requests_per_minute} requests/minute")


# TODO: For production, use Redis-based rate limiting
# from redis import asyncio as aioredis
# 
# class RedisRateLimiter:
#     def __init__(self, redis_url: str, requests_per_minute: int = 60):
#         self.redis = aioredis.from_url(redis_url)
#         self.requests_per_minute = requests_per_minute
#     
#     async def is_allowed(self, client_id: str) -> bool:
#         key = f"rate_limit:{client_id}"
#         count = await self.redis.incr(key)
#         if count == 1:
#             await self.redis.expire(key, 60)
#         return count <= self.requests_per_minute
