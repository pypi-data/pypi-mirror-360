"""
Shared JWT Authentication Middleware for all microservices
Provides standardized authentication patterns and user context
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, Dict, Any, List
import httpx
import os
from datetime import datetime
import logging
from dataclasses import dataclass

from shared_architecture.utils.logging_utils import log_info, log_warning, log_exception

@dataclass
class UserContext:
    """Standardized user context across all services"""
    user_id: int
    email: str
    first_name: str
    last_name: str
    role: str
    organization_id: Optional[int] = None
    is_active: bool = True
    permissions: List[str] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []

class BaseAuthMiddleware:
    """Base authentication middleware for all microservices"""
    
    def __init__(self, 
                 service_name: str,
                 user_service_url: Optional[str] = None,
                 jwt_secret_key: Optional[str] = None,
                 jwt_algorithm: str = "HS256",
                 skip_paths: Optional[List[str]] = None):
        self.service_name = service_name
        self.user_service_url = user_service_url or os.getenv("USER_SERVICE_URL", "http://user_service:8002")
        self.jwt_secret_key = jwt_secret_key or os.getenv("JWT_SECRET_KEY")
        self.jwt_algorithm = jwt_algorithm
        self.security = HTTPBearer()
        
        # Default paths to skip authentication
        default_skip_paths = [
            "/health", "/docs", "/openapi.json", "/redoc",
            "/api/v1/health", "/api/v1/docs", "/api/v1/openapi.json"
        ]
        self.skip_paths = set(default_skip_paths + (skip_paths or []))
        
        if not self.jwt_secret_key:
            log_warning(f"JWT_SECRET_KEY not set for {service_name} authentication middleware")
    
    def should_skip_auth(self, path: str) -> bool:
        """Check if authentication should be skipped for this path"""
        return any(path.startswith(skip_path) for skip_path in self.skip_paths)
    
    async def extract_token(self, request: Request) -> str:
        """Extract JWT token from request headers"""
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing"
            )
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        return authorization.split(" ")[1]
    
    async def validate_token_locally(self, token: str) -> Dict[str, Any]:
        """Validate JWT token locally using secret key"""
        try:
            payload = jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])
            return payload
        except JWTError as e:
            log_exception(f"JWT validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def validate_token_with_user_service(self, token: str) -> UserContext:
        """Validate token with user service and get user context"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.user_service_url}/api/v1/auth/validate",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return UserContext(
                        user_id=user_data.get("user_id"),
                        email=user_data.get("email"),
                        first_name=user_data.get("first_name"),
                        last_name=user_data.get("last_name"),
                        role=user_data.get("role"),
                        organization_id=user_data.get("organization_id"),
                        is_active=user_data.get("is_active", True),
                        permissions=user_data.get("permissions", [])
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token validation failed"
                    )
        except httpx.TimeoutException:
            log_warning("User service timeout during token validation")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
        except Exception as e:
            log_exception(f"Error validating token with user service: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    async def get_user_context(self, token: str) -> UserContext:
        """Get user context from token - try local validation first, then user service"""
        if self.jwt_secret_key:
            try:
                payload = await self.validate_token_locally(token)
                # Convert JWT payload to UserContext
                return UserContext(
                    user_id=payload.get("user_id"),
                    email=payload.get("email"),
                    first_name=payload.get("first_name", ""),
                    last_name=payload.get("last_name", ""),
                    role=payload.get("role", "user"),
                    organization_id=payload.get("organization_id"),
                    is_active=payload.get("is_active", True),
                    permissions=payload.get("permissions", [])
                )
            except HTTPException:
                # Fall back to user service validation
                return await self.validate_token_with_user_service(token)
        else:
            # No local secret, use user service
            return await self.validate_token_with_user_service(token)
    
    async def __call__(self, request: Request, call_next):
        """Process request with JWT authentication"""
        
        # Skip authentication for specified paths
        if self.should_skip_auth(request.url.path):
            return await call_next(request)
        
        try:
            # Extract and validate token
            token = await self.extract_token(request)
            user_context = await self.get_user_context(token)
            
            # Add user context to request state
            request.state.user = user_context
            request.state.token = token
            
            log_info(f"Authenticated user {user_context.email} for {self.service_name}")
            
        except HTTPException:
            raise
        except Exception as e:
            log_exception(f"Unexpected error in auth middleware: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication processing error"
            )
        
        return await call_next(request)

class MockAuthMiddleware(BaseAuthMiddleware):
    """Mock authentication middleware for development/testing"""
    
    def __init__(self, service_name: str, mock_user_id: int = 1, **kwargs):
        super().__init__(service_name, **kwargs)
        self.mock_user_id = mock_user_id
        log_info(f"Using mock authentication for {service_name}")
    
    async def __call__(self, request: Request, call_next):
        """Process request with mock authentication"""
        
        # Skip authentication for specified paths
        if self.should_skip_auth(request.url.path):
            return await call_next(request)
        
        # Add mock user context
        mock_user = UserContext(
            user_id=self.mock_user_id,
            email=f"mock-user-{self.mock_user_id}@example.com",
            first_name="Mock",
            last_name="User",
            role="admin",
            organization_id=1,
            is_active=True,
            permissions=["all"]
        )
        
        request.state.user = mock_user
        request.state.token = "mock-token"
        
        return await call_next(request)

def create_auth_middleware(service_name: str, 
                          use_mock: bool = None,
                          **kwargs) -> BaseAuthMiddleware:
    """Factory function to create appropriate auth middleware"""
    
    if use_mock is None:
        use_mock = os.getenv("USE_MOCK_AUTH", "false").lower() == "true"
    
    if use_mock:
        return MockAuthMiddleware(service_name, **kwargs)
    else:
        return BaseAuthMiddleware(service_name, **kwargs)

# Dependency functions for FastAPI
def get_current_user(request: Request) -> UserContext:
    """FastAPI dependency to get current authenticated user"""
    if hasattr(request.state, 'user'):
        return request.state.user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not authenticated"
    )

def get_current_token(request: Request) -> str:
    """FastAPI dependency to get current JWT token"""
    if hasattr(request.state, 'token'):
        return request.state.token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token not available"
    )

def require_permission(required_permission: str):
    """FastAPI dependency factory to require specific permission"""
    def permission_checker(user: UserContext = get_current_user):
        if "all" in user.permissions or required_permission in user.permissions:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{required_permission}' required"
        )
    return permission_checker

def require_role(required_role: str):
    """FastAPI dependency factory to require specific role"""
    def role_checker(user: UserContext = get_current_user):
        if user.role == required_role or user.role == "admin":
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{required_role}' required"
        )
    return role_checker