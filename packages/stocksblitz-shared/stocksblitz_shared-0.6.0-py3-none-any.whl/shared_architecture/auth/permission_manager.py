# shared_architecture/auth/permission_manager.py
# TODO: RBAC Integration Phase 1 - Centralized Permission System
# TODO: Implement real user_service integration instead of mock data
# TODO: Add Redis caching for permission data with TTL and invalidation
# TODO: Add permission audit logging for compliance and debugging
# TODO: Implement real-time permission updates via WebSocket/events
# TODO: Add organization-level permission inheritance and overrides
# TODO: Create comprehensive unit tests for all permission scenarios

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio
import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..utils.enhanced_logging import get_logger
from ..exceptions.trade_exceptions import AuthenticationException, AuthorizationException

logger = get_logger(__name__)

class PermissionManager:
    """
    Centralized permission checking system for all microservices.
    
    This class provides a unified interface for:
    - User permission validation
    - Role-based access control (RBAC)
    - Trading restrictions enforcement
    - Organization-level access control
    - Resource filtering based on permissions
    """
    
    def __init__(self, cache_ttl: int = 300):
        self.cache_ttl = cache_ttl
        self._permission_cache = {}  # TODO: Replace with Redis
        
    async def check_permission(
        self, 
        user_id: str, 
        action: str, 
        resource: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> bool:
        """
        Check if user has permission for specific action.
        
        Args:
            user_id: User identifier
            action: Permission action (e.g., 'view_positions', 'place_orders')
            resource: Optional resource identifier
            organization_id: Optional organization context
            
        Returns:
            bool: True if permission granted, False otherwise
        """
        try:
            # TODO: Replace with real user_service API call
            user_permissions = await self._get_user_permissions(user_id, organization_id)
            
            # Check basic permission
            if action not in user_permissions.get('permissions', {}):
                logger.warning(f"Permission check failed: {user_id} -> {action}")
                return False
                
            permission_granted = user_permissions['permissions'][action]
            
            # Apply additional restrictions if needed
            if resource and not await self._check_resource_access(user_id, resource, action):
                logger.warning(f"Resource access denied: {user_id} -> {resource} -> {action}")
                return False
                
            if permission_granted:
                logger.debug(f"Permission granted: {user_id} -> {action}")
            else:
                logger.warning(f"Permission denied: {user_id} -> {action}")
                
            return permission_granted
            
        except Exception as e:
            logger.exception(f"Permission check error for user {user_id}, action {action}: {e}")
            return False  # Fail-safe: deny on error
    
    async def get_user_permissions(
        self, 
        user_id: str, 
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Get all permissions for user in organization.
        
        Returns:
            Dict containing user permissions, restrictions, and metadata
        """
        try:
            return await self._get_user_permissions(user_id, organization_id)
        except Exception as e:
            logger.exception(f"Failed to get permissions for user {user_id}: {e}")
            return self._get_default_permissions()
    
    async def filter_accessible_resources(
        self, 
        user_id: str, 
        resources: List[Dict], 
        resource_type: str,
        organization_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter resources based on user permissions.
        
        Args:
            user_id: User identifier
            resources: List of resources to filter
            resource_type: Type of resource ('positions', 'orders', 'strategies', etc.)
            organization_id: Optional organization context
            
        Returns:
            List of accessible resources
        """
        try:
            # TODO: Implement resource-level filtering logic
            user_permissions = await self._get_user_permissions(user_id, organization_id)
            accessible_accounts = user_permissions.get('accessible_accounts', [])
            
            # Filter based on account access
            filtered_resources = []
            for resource in resources:
                account_id = resource.get('account_id') or resource.get('trading_account_id')
                if not account_id or account_id in accessible_accounts:
                    filtered_resources.append(resource)
                    
            logger.debug(f"Filtered {len(resources)} -> {len(filtered_resources)} {resource_type} for user {user_id}")
            return filtered_resources
            
        except Exception as e:
            logger.exception(f"Resource filtering error for user {user_id}: {e}")
            return []  # Fail-safe: return empty list on error
    
    async def check_trading_restrictions(
        self, 
        user_id: str, 
        symbol: str, 
        action: str,
        quantity: Optional[int] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check trading-specific restrictions.
        
        Returns:
            Dict with 'allowed' boolean and 'reason' if denied
        """
        try:
            user_permissions = await self._get_user_permissions(user_id, organization_id)
            restrictions = user_permissions.get('restrictions', {})
            
            # Check symbol restrictions
            blocked_symbols = restrictions.get('symbols_blocked', [])
            if symbol in blocked_symbols:
                return {'allowed': False, 'reason': f'Symbol {symbol} is blocked for user'}
                
            allowed_symbols = restrictions.get('symbols_allowed', [])
            if allowed_symbols and symbol not in allowed_symbols:
                return {'allowed': False, 'reason': f'Symbol {symbol} not in allowed list'}
            
            # Check instrument type restrictions
            # TODO: Implement instrument type detection from symbol
            
            # Check position size limits
            if quantity and quantity > restrictions.get('max_position_size', float('inf')):
                return {'allowed': False, 'reason': 'Position size exceeds user limit'}
            
            # Check trading hours
            if restrictions.get('trading_hours_enabled', False):
                # TODO: Implement trading hours checking
                pass
                
            return {'allowed': True}
            
        except Exception as e:
            logger.exception(f"Trading restriction check error for user {user_id}: {e}")
            return {'allowed': False, 'reason': 'Internal error during restriction check'}
    
    async def check_organization_access(
        self, 
        user_id: str, 
        organization_id: str
    ) -> bool:
        """Check if user has access to organization."""
        try:
            user_permissions = await self._get_user_permissions(user_id, organization_id)
            return user_permissions.get('organization_access', False)
        except Exception as e:
            logger.exception(f"Organization access check error: {e}")
            return False
    
    async def invalidate_user_cache(self, user_id: str):
        """Invalidate cached permissions for user."""
        # TODO: Implement Redis cache invalidation
        cache_keys = [key for key in self._permission_cache.keys() if user_id in key]
        for key in cache_keys:
            del self._permission_cache[key]
        logger.info(f"Invalidated permission cache for user {user_id}")
    
    async def invalidate_organization_cache(self, organization_id: str):
        """Invalidate cached permissions for entire organization."""
        # TODO: Implement Redis cache invalidation
        cache_keys = [key for key in self._permission_cache.keys() if organization_id in key]
        for key in cache_keys:
            del self._permission_cache[key]
        logger.info(f"Invalidated permission cache for organization {organization_id}")
    
    # Private methods
    
    async def _get_user_permissions(
        self, 
        user_id: str, 
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user permissions from cache or user_service."""
        from .permission_cache import permission_cache, cache_monitor
        
        # Initialize cache if needed
        await permission_cache.initialize()
        
        # Try cache first
        cached_permissions = await permission_cache.get_cached_permissions(user_id, organization_id)
        if cached_permissions:
            await cache_monitor.record_hit()
            logger.debug(f"Permission cache hit for user {user_id}")
            return cached_permissions
        
        # Cache miss - fetch from user_service
        await cache_monitor.record_miss()
        logger.debug(f"Permission cache miss for user {user_id}")
        
        try:
            permissions = await self._fetch_permissions_from_user_service(user_id, organization_id)
            
            # Cache the result
            await permission_cache.set_cached_permissions(
                user_id, 
                organization_id, 
                permissions, 
                ttl_minutes=self.cache_ttl // 60
            )
            
            return permissions
            
        except Exception as e:
            await cache_monitor.record_error()
            logger.exception(f"Error fetching permissions for user {user_id}: {e}")
            return self._get_default_permissions()
    
    async def _fetch_permissions_from_user_service(
        self, 
        user_id: str, 
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch permissions from user_service API."""
        import httpx
        from ..config.global_settings import get_settings
        
        try:
            settings = get_settings()
            user_service_url = settings.USER_SERVICE_URL or "http://localhost:8002"
            
            # Make API call to user_service
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get user permissions endpoint
                headers = {"Content-Type": "application/json"}
                
                # First get user basic info
                user_response = await client.get(
                    f"{user_service_url}/users/{user_id}",
                    headers=headers
                )
                
                if user_response.status_code != 200:
                    logger.warning(f"User not found in user_service: {user_id}")
                    return self._get_default_permissions()
                
                user_data = user_response.json()
                
                # Get user permissions for organization
                if organization_id:
                    perm_response = await client.get(
                        f"{user_service_url}/permissions/user/{user_id}/organization/{organization_id}",
                        headers=headers
                    )
                else:
                    perm_response = await client.get(
                        f"{user_service_url}/permissions/user/{user_id}",
                        headers=headers
                    )
                
                if perm_response.status_code == 200:
                    permission_data = perm_response.json()
                else:
                    # Fallback to role-based permissions
                    permission_data = self._get_role_based_permissions(user_data.get('role', 'VIEWER'))
                
                # Get trading accounts accessible to user
                accounts_response = await client.get(
                    f"{user_service_url}/trading-accounts/user/{user_id}",
                    headers=headers
                )
                
                accessible_accounts = []
                if accounts_response.status_code == 200:
                    accounts_data = accounts_response.json()
                    accessible_accounts = [acc['account_id'] for acc in accounts_data]
                
                # Get trading restrictions
                restrictions_response = await client.get(
                    f"{user_service_url}/restrictions/user/{user_id}",
                    headers=headers
                )
                
                restrictions = {}
                if restrictions_response.status_code == 200:
                    restrictions = restrictions_response.json()
                else:
                    restrictions = self._get_default_restrictions()
                
                return {
                    'permissions': permission_data.get('permissions', {}),
                    'restrictions': restrictions,
                    'accessible_accounts': accessible_accounts,
                    'organization_access': True,  # If we got this far, user has org access
                    'role': user_data.get('role', 'VIEWER'),
                    'organization_id': organization_id,
                    'user_id': user_id
                }
                
        except Exception as e:
            logger.exception(f"Failed to fetch permissions from user_service: {e}")
            # Fallback to mock data for development
            return self._get_mock_permissions(user_id)
    
    def _get_role_based_permissions(self, role: str) -> Dict[str, Any]:
        """Get permissions based on user role."""
        role_permissions = {
            'OWNER': {
                'permissions': {
                    'view_positions': True, 'view_orders': True, 'view_trades': True,
                    'view_balance': True, 'view_pnl': True, 'view_strategies': True,
                    'view_reports': True, 'place_orders': True, 'modify_orders': True,
                    'cancel_orders': True, 'square_off_positions': True,
                    'create_strategy': True, 'modify_strategy': True, 'adjust_strategy': True,
                    'square_off_strategy': True, 'share_strategy': True,
                    'admin_users': True, 'admin_api_keys': True, 'admin_settings': True,
                    'admin_reports': True
                }
            },
            'ADMIN': {
                'permissions': {
                    'view_positions': True, 'view_orders': True, 'view_trades': True,
                    'view_balance': True, 'view_pnl': True, 'view_strategies': True,
                    'view_reports': True, 'place_orders': True, 'modify_orders': True,
                    'cancel_orders': True, 'square_off_positions': True,
                    'create_strategy': True, 'modify_strategy': True, 'adjust_strategy': True,
                    'square_off_strategy': True, 'share_strategy': True,
                    'admin_users': True, 'admin_api_keys': True, 'admin_settings': False,
                    'admin_reports': True
                }
            },
            'TRADER': {
                'permissions': {
                    'view_positions': True, 'view_orders': True, 'view_trades': True,
                    'view_balance': True, 'view_pnl': True, 'view_strategies': True,
                    'view_reports': False, 'place_orders': True, 'modify_orders': True,
                    'cancel_orders': True, 'square_off_positions': True,
                    'create_strategy': True, 'modify_strategy': True, 'adjust_strategy': True,
                    'square_off_strategy': True, 'share_strategy': False,
                    'admin_users': False, 'admin_api_keys': False, 'admin_settings': False,
                    'admin_reports': False
                }
            },
            'VIEWER': {
                'permissions': {
                    'view_positions': True, 'view_orders': True, 'view_trades': True,
                    'view_balance': True, 'view_pnl': True, 'view_strategies': True,
                    'view_reports': False, 'place_orders': False, 'modify_orders': False,
                    'cancel_orders': False, 'square_off_positions': False,
                    'create_strategy': False, 'modify_strategy': False, 'adjust_strategy': False,
                    'square_off_strategy': False, 'share_strategy': False,
                    'admin_users': False, 'admin_api_keys': False, 'admin_settings': False,
                    'admin_reports': False
                }
            }
        }
        
        return role_permissions.get(role, role_permissions['VIEWER'])
    
    def _get_default_restrictions(self) -> Dict[str, Any]:
        """Get default trading restrictions."""
        return {
            'trading_hours_enabled': True,
            'trading_start_time': '09:15',
            'trading_end_time': '15:30',
            'instruments_allowed': ['equity'],
            'symbols_blocked': [],
            'symbols_allowed': [],
            'max_position_size': 100,
            'max_order_value': 50000,
            'max_daily_loss': 10000,
            'max_orders_per_minute': 10,
            'max_orders_per_day': 100
        }
    
    def _get_mock_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get mock permissions for development/fallback."""
        mock_permissions = {
            '1': {  # Admin user
                'permissions': self._get_role_based_permissions('ADMIN')['permissions'],
                'restrictions': {
                    'trading_hours_enabled': False,
                    'symbols_blocked': [],
                    'symbols_allowed': [],
                    'max_position_size': 10000,
                    'max_order_value': 1000000,
                },
                'accessible_accounts': ['DEMO123', 'LIVE456'],
                'organization_access': True,
                'role': 'ADMIN'
            },
            '2': {  # Trader user
                'permissions': self._get_role_based_permissions('TRADER')['permissions'],
                'restrictions': {
                    'trading_hours_enabled': True,
                    'trading_start_time': '09:15',
                    'trading_end_time': '15:30',
                    'symbols_blocked': ['RELIANCE'],
                    'symbols_allowed': [],
                    'max_position_size': 1000,
                    'max_order_value': 100000,
                },
                'accessible_accounts': ['DEMO123'],
                'organization_access': True,
                'role': 'TRADER'
            },
            '3': {  # Viewer user
                'permissions': self._get_role_based_permissions('VIEWER')['permissions'],
                'restrictions': self._get_default_restrictions(),
                'accessible_accounts': ['DEMO123'],
                'organization_access': True,
                'role': 'VIEWER'
            }
        }
        
        return mock_permissions.get(user_id, self._get_default_permissions())
    
    async def _check_resource_access(
        self, 
        user_id: str, 
        resource: str, 
        action: str
    ) -> bool:
        """Check if user has access to specific resource."""
        # TODO: Implement resource-specific access checks
        return True
    
    def _get_default_permissions(self) -> Dict[str, Any]:
        """Get default (minimal) permissions for users."""
        return {
            'permissions': {
                'view_positions': False,
                'view_orders': False,
                'view_trades': False,
                'view_balance': False,
                'view_pnl': False,
                'view_strategies': False,
                'view_reports': False,
                'place_orders': False,
                'modify_orders': False,
                'cancel_orders': False,
                'square_off_positions': False,
                'create_strategy': False,
                'modify_strategy': False,
                'admin_users': False,
                'admin_settings': False,
            },
            'restrictions': {
                'trading_hours_enabled': True,
                'symbols_blocked': [],
                'symbols_allowed': [],
                'max_position_size': 100,
                'max_order_value': 10000,
            },
            'accessible_accounts': [],
            'organization_access': False,
            'role': 'VIEWER'
        }

# Global instance for use across microservices
permission_manager = PermissionManager()