# shared_architecture/auth/decorators.py
# TODO: RBAC Integration Phase 1 - Permission Decorators for All Services
# TODO: Add async support for all decorators
# TODO: Implement resource-level permission checking
# TODO: Add audit logging for all permission checks
# TODO: Create performance monitoring for permission checks
# TODO: Add organization context to all permission checks

from functools import wraps
from typing import List, Optional, Union, Callable, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .permission_manager import permission_manager
from .jwt_manager import JWTManager
from ..utils.enhanced_logging import get_logger

logger = get_logger(__name__)

# JWT token dependency
security = HTTPBearer()
jwt_manager = JWTManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to extract current user from JWT token.
    Used across all microservices for user context.
    """
    try:
        # TODO: Implement proper JWT validation with user_service
        token = credentials.credentials
        
        # Mock implementation - replace with real JWT validation
        if token.startswith('bypass_token_'):
            return {
                'user_id': '1',
                'email': 'admin@stocksblitz.com',
                'organization_id': 'ORG_REAL_001',
                'role': 'ADMIN'
            }
        
        # Real JWT validation would go here
        # user_data = await jwt_manager.validate_token(token)
        # return user_data
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
        
    except Exception as e:
        logger.exception(f"JWT validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

def require_permission(permission: str, resource_type: Optional[str] = None):
    """
    Decorator to require specific permission for endpoint access.
    
    Usage:
        @require_permission("view_positions")
        async def get_positions(user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user context (should be injected by FastAPI Depends)
            user_context = None
            for arg in args:
                if isinstance(arg, dict) and 'user_id' in arg:
                    user_context = arg
                    break
            
            if not user_context:
                # Look in kwargs for user context
                for key, value in kwargs.items():
                    if isinstance(value, dict) and 'user_id' in value:
                        user_context = value
                        break
            
            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User context not found"
                )
            
            # Check permission
            has_permission = await permission_manager.check_permission(
                user_id=user_context['user_id'],
                action=permission,
                organization_id=user_context.get('organization_id')
            )
            
            if not has_permission:
                logger.warning(f"Permission denied: {user_context['user_id']} -> {permission}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_permission(permissions: List[str]):
    """
    Decorator to require any of the specified permissions.
    
    Usage:
        @require_any_permission(["place_orders", "modify_orders"])
        async def trading_action(user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_context = _extract_user_context(args, kwargs)
            
            # Check if user has any of the required permissions
            for permission in permissions:
                has_permission = await permission_manager.check_permission(
                    user_id=user_context['user_id'],
                    action=permission,
                    organization_id=user_context.get('organization_id')
                )
                if has_permission:
                    return await func(*args, **kwargs)
            
            logger.warning(f"Permission denied: {user_context['user_id']} -> any of {permissions}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {', '.join(permissions)}"
            )
        return wrapper
    return decorator

def require_all_permissions(permissions: List[str]):
    """
    Decorator to require all specified permissions.
    
    Usage:
        @require_all_permissions(["view_positions", "modify_orders"])
        async def advanced_trading(user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_context = _extract_user_context(args, kwargs)
            
            # Check if user has all required permissions
            for permission in permissions:
                has_permission = await permission_manager.check_permission(
                    user_id=user_context['user_id'],
                    action=permission,
                    organization_id=user_context.get('organization_id')
                )
                if not has_permission:
                    logger.warning(f"Permission denied: {user_context['user_id']} -> {permission}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission '{permission}' required"
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_organization_access(organization_param: str = "organization_id"):
    """
    Decorator to ensure user has access to specified organization.
    
    Usage:
        @require_organization_access()
        async def get_org_data(organization_id: str, user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_context = _extract_user_context(args, kwargs)
            
            # Extract organization_id from parameters
            org_id = kwargs.get(organization_param)
            if not org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Organization ID parameter '{organization_param}' required"
                )
            
            # Check organization access
            has_access = await permission_manager.check_organization_access(
                user_id=user_context['user_id'],
                organization_id=org_id
            )
            
            if not has_access:
                logger.warning(f"Organization access denied: {user_context['user_id']} -> {org_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access to organization denied"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: str):
    """
    Decorator to require specific user role.
    
    Usage:
        @require_role("ADMIN")
        async def admin_function(user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_context = _extract_user_context(args, kwargs)
            
            user_role = user_context.get('role')
            if user_role != role:
                logger.warning(f"Role access denied: {user_context['user_id']} has {user_role}, requires {role}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{role}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_trading_permission(symbol: Optional[str] = None, action: str = "place_orders"):
    """
    Decorator for trading-specific permission checks with symbol restrictions.
    
    Usage:
        @require_trading_permission(action="place_orders")
        async def place_order(symbol: str, user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_context = _extract_user_context(args, kwargs)
            
            # Extract symbol from parameters if not provided
            trading_symbol = symbol or kwargs.get('symbol')
            if not trading_symbol:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Symbol parameter required for trading permission check"
                )
            
            # Check basic trading permission
            has_permission = await permission_manager.check_permission(
                user_id=user_context['user_id'],
                action=action,
                organization_id=user_context.get('organization_id')
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Trading permission '{action}' required"
                )
            
            # Check trading restrictions
            restriction_check = await permission_manager.check_trading_restrictions(
                user_id=user_context['user_id'],
                symbol=trading_symbol,
                action=action,
                organization_id=user_context.get('organization_id')
            )
            
            if not restriction_check['allowed']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=restriction_check['reason']
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Helper functions

def _extract_user_context(args: tuple, kwargs: dict) -> dict:
    """Extract user context from function arguments."""
    # Look in args first
    for arg in args:
        if isinstance(arg, dict) and 'user_id' in arg:
            return arg
    
    # Look in kwargs
    for key, value in kwargs.items():
        if isinstance(value, dict) and 'user_id' in value:
            return value
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User context not found in request"
    )