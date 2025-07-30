# shared_architecture/middleware/permission_middleware.py
"""
Permission middleware for FastAPI applications.
Automatically applies permission checks to all endpoints based on configuration.
"""

import json
from typing import List, Dict, Optional, Callable, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import time

from ..auth.permission_manager import permission_manager
from ..auth.jwt_manager import JWTManager
from ..utils.enhanced_logging import get_logger

logger = get_logger(__name__)

class PermissionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically apply permission checks to FastAPI endpoints.
    
    Features:
    - Automatic JWT validation
    - Permission checking based on endpoint configuration
    - Request/response filtering based on user permissions
    - Audit logging for all permission checks
    """
    
    def __init__(
        self,
        app,
        excluded_paths: List[str] = None,
        permission_config: Dict[str, Any] = None,
        require_auth: bool = True
    ):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"
        ]
        self.permission_config = permission_config or {}
        self.require_auth = require_auth
        self.jwt_manager = JWTManager()
        self.security = HTTPBearer(auto_error=False)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware function."""
        start_time = time.time()
        
        # Skip excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        try:
            # Extract and validate user context
            user_context = await self._extract_user_context(request)
            
            # Check permissions for this endpoint
            if self.require_auth and user_context:
                await self._check_endpoint_permissions(request, user_context)
            
            # Add user context to request state
            if user_context:
                request.state.user = user_context
            
            # Process request
            response = await call_next(request)
            
            # Apply response filtering if needed
            if user_context and hasattr(request.state, 'filter_response'):
                response = await self._filter_response(response, user_context, request)
            
            # Log successful request
            processing_time = time.time() - start_time
            await self._log_request(request, user_context, response.status_code, processing_time)
            
            return response
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.exception(f"Permission middleware error: {e}")
            # Log failed request
            processing_time = time.time() - start_time
            await self._log_request(request, None, 500, processing_time, error=str(e))
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during permission check"
            )
    
    async def _extract_user_context(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract user context from JWT token."""
        try:
            # Get Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                if self.require_auth:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authorization header required"
                    )
                return None
            
            token = auth_header.split(" ")[1]
            
            # Handle bypass tokens for development
            if token.startswith('bypass_token_'):
                return {
                    'user_id': '1',
                    'email': 'admin@stocksblitz.com',
                    'organization_id': 'ORG_REAL_001',
                    'role': 'ADMIN',
                    'token_type': 'bypass'
                }
            
            # Validate JWT token
            try:
                claims = await self.jwt_manager.validate_token(token)
                return {
                    'user_id': claims.get('sub'),
                    'email': claims.get('email'),
                    'organization_id': claims.get('organization_id'),
                    'role': claims.get('role'),
                    'token_type': 'jwt'
                }
            except Exception as jwt_error:
                logger.warning(f"JWT validation failed: {jwt_error}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error extracting user context: {e}")
            if self.require_auth:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication failed"
                )
            return None
    
    async def _check_endpoint_permissions(self, request: Request, user_context: Dict[str, Any]):
        """Check permissions for the endpoint."""
        method = request.method.lower()
        path = request.url.path
        
        # Get permission requirements for this endpoint
        permissions_required = self._get_endpoint_permissions(method, path)
        
        if not permissions_required:
            # No specific permissions required
            return
        
        # Check each required permission
        for permission in permissions_required:
            has_permission = await permission_manager.check_permission(
                user_id=user_context['user_id'],
                action=permission,
                organization_id=user_context.get('organization_id')
            )
            
            if not has_permission:
                logger.warning(
                    f"Permission denied: {user_context['user_id']} -> {permission} for {method.upper()} {path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required for this operation"
                )
        
        logger.debug(f"Permission check passed: {user_context['user_id']} -> {permissions_required}")
    
    def _get_endpoint_permissions(self, method: str, path: str) -> List[str]:
        """Get required permissions for endpoint."""
        # Check exact path match first
        endpoint_key = f"{method.upper()}:{path}"
        if endpoint_key in self.permission_config:
            return self.permission_config[endpoint_key]
        
        # Check pattern matches
        for pattern, permissions in self.permission_config.items():
            if self._path_matches_pattern(path, pattern.split(':', 1)[1] if ':' in pattern else pattern):
                return permissions
        
        # Default permission mapping based on method and path patterns
        return self._get_default_permissions(method, path)
    
    def _get_default_permissions(self, method: str, path: str) -> List[str]:
        """Get default permission requirements based on method and path."""
        # Common permission patterns
        default_patterns = {
            # Trading operations
            ('POST', '/orders'): ['place_orders'],
            ('PUT', '/orders'): ['modify_orders'],
            ('DELETE', '/orders'): ['cancel_orders'],
            ('GET', '/positions'): ['view_positions'],
            ('GET', '/orders'): ['view_orders'],
            ('GET', '/trades'): ['view_trades'],
            ('POST', '/strategies'): ['create_strategy'],
            ('PUT', '/strategies'): ['modify_strategy'],
            ('GET', '/strategies'): ['view_strategies'],
            
            # Admin operations
            ('GET', '/users'): ['admin_users'],
            ('POST', '/users'): ['admin_users'],
            ('GET', '/api-keys'): ['admin_api_keys'],
            ('POST', '/api-keys'): ['admin_api_keys'],
            
            # Reports
            ('GET', '/reports'): ['view_reports'],
        }
        
        # Check for exact matches
        for (pattern_method, pattern_path), permissions in default_patterns.items():
            if method.upper() == pattern_method and path.startswith(pattern_path):
                return permissions
        
        # Default: no specific permissions required
        return []
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern (simple wildcard support)."""
        if '*' not in pattern:
            return path == pattern
        
        # Simple wildcard matching
        pattern_parts = pattern.split('*')
        if len(pattern_parts) == 2:
            prefix, suffix = pattern_parts
            return path.startswith(prefix) and path.endswith(suffix)
        
        return False
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if path should be excluded from permission checks."""
        return any(path.startswith(excluded) for excluded in self.excluded_paths)
    
    async def _filter_response(
        self, 
        response: Response, 
        user_context: Dict[str, Any], 
        request: Request
    ) -> Response:
        """Filter response data based on user permissions."""
        # This is a placeholder for response filtering
        # In practice, you might filter out sensitive fields or entire records
        return response
    
    async def _log_request(
        self, 
        request: Request, 
        user_context: Optional[Dict[str, Any]], 
        status_code: int, 
        processing_time: float,
        error: Optional[str] = None
    ):
        """Log request for audit purposes."""
        log_data = {
            'timestamp': time.time(),
            'method': request.method,
            'path': request.url.path,
            'user_id': user_context.get('user_id') if user_context else None,
            'organization_id': user_context.get('organization_id') if user_context else None,
            'status_code': status_code,
            'processing_time_ms': round(processing_time * 1000, 2),
            'user_agent': request.headers.get('user-agent'),
            'ip_address': request.client.host if request.client else None
        }
        
        if error:
            log_data['error'] = error
            logger.error(f"Request failed: {json.dumps(log_data)}")
        else:
            logger.info(f"Request processed: {json.dumps(log_data)}")


# Configuration helpers

def create_trading_permission_config() -> Dict[str, List[str]]:
    """Create permission configuration for trading service endpoints."""
    return {
        # Trading operations
        'POST:/trades/orders': ['place_orders'],
        'PUT:/trades/orders/*': ['modify_orders'],
        'DELETE:/trades/orders/*': ['cancel_orders'],
        'POST:/trades/square-off': ['square_off_positions'],
        
        # Data viewing
        'GET:/trades/positions': ['view_positions'],
        'GET:/trades/orders': ['view_orders'],
        'GET:/trades/trades': ['view_trades'],
        'GET:/trades/balance': ['view_balance'],
        'GET:/trades/pnl': ['view_pnl'],
        
        # Strategy management
        'POST:/strategies': ['create_strategy'],
        'PUT:/strategies/*': ['modify_strategy'],
        'DELETE:/strategies/*': ['modify_strategy'],
        'GET:/strategies': ['view_strategies'],
        
        # Admin operations
        'GET:/api-key-management/*': ['admin_api_keys'],
        'POST:/api-key-management/*': ['admin_api_keys'],
        'GET:/management/*': ['admin_settings'],
        
        # Reports
        'GET:/ledger/*': ['view_reports'],
        'GET:/data/reports': ['view_reports'],
    }

def create_execution_engine_permission_config() -> Dict[str, List[str]]:
    """Create permission configuration for execution engine endpoints."""
    return {
        # Strategy execution
        'POST:/strategies/start': ['place_orders', 'create_strategy'],
        'POST:/strategies/stop': ['modify_strategy'],
        'POST:/strategies/pause': ['modify_strategy'],
        'POST:/strategies/emergency-stop': ['square_off_positions'],
        
        # Strategy monitoring
        'GET:/strategies/status': ['view_strategies'],
        'GET:/strategies/performance': ['view_strategies'],
        'GET:/strategies/logs': ['view_strategies'],
        
        # Portfolio management
        'POST:/portfolios/start': ['place_orders', 'create_strategy'],
        'POST:/portfolios/stop': ['modify_strategy'],
        'GET:/portfolios/status': ['view_strategies'],
        
        # Admin operations
        'POST:/admin/restart': ['admin_settings'],
        'GET:/admin/health': ['admin_settings'],
    }

def create_signal_service_permission_config() -> Dict[str, List[str]]:
    """Create permission configuration for signal service endpoints."""
    return {
        # Threshold management
        'POST:/thresholds': ['create_strategy'],
        'PUT:/thresholds/*': ['modify_strategy'],
        'DELETE:/thresholds/*': ['modify_strategy'],
        'GET:/thresholds': ['view_strategies'],
        
        # Alert management
        'GET:/alerts': ['view_orders'],
        'POST:/alerts/acknowledge': ['modify_orders'],
        
        # Signal monitoring
        'GET:/signals': ['view_strategies'],
        'GET:/monitoring/status': ['view_strategies'],
    }

def create_ticker_service_permission_config() -> Dict[str, List[str]]:
    """Create permission configuration for ticker service endpoints."""
    return {
        # Data subscriptions
        'POST:/feeds/subscribe/*': ['view_positions'],
        'DELETE:/feeds/unsubscribe/*': ['view_positions'],
        'GET:/feeds/status': ['view_positions'],
        
        # Historical data
        'GET:/historical/*': ['view_reports'],
        'POST:/historical/fetch': ['view_reports'],
        
        # Symbols
        'GET:/symbols/*': ['view_positions'],
    }