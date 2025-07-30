"""User Service Client for inter-service communication"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import os
from shared_architecture.clients.service_client import InterServiceClient
from shared_architecture.auth.user_context import UserContext
from shared_architecture.utils.enhanced_logging import get_logger

logger = get_logger(__name__)


class UserServiceClient(InterServiceClient):
    """Client for communicating with user service"""
    
    def __init__(self, base_url: Optional[str] = None, service_secret: Optional[str] = None):
        """Initialize user service client"""
        if base_url is None:
            base_url = os.getenv("USER_SERVICE_URL", "http://user-service:8002")
        
        if service_secret is None:
            service_secret = os.getenv("SERVICE_SECRET", "default_secret_for_testing")
        
        super().__init__(
            service_name="user_service",
            base_url=base_url,
            service_secret=service_secret,
            timeout=30.0
        )
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token and return user context
        
        Used by other services to validate incoming requests
        """
        try:
            response = await self._make_request(
                method="POST",
                endpoint="/api/v1/trade-integration/auth/validate-token",
                json={"token": token}
            )
            
            if response and response.get("valid"):
                return response
            else:
                raise ValueError("Invalid token")
                
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise
    
    async def check_permission(
        self, 
        user_id: int, 
        permission: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None
    ) -> bool:
        """
        Check if user has specific permission
        
        Args:
            user_id: User ID to check
            permission: Permission string (e.g., 'TRADING_EXECUTE')
            resource_type: Optional resource type for context
            resource_id: Optional resource ID for context
        """
        try:
            response = await self._make_request(
                method="POST",
                endpoint="/api/v1/trade-integration/auth/check-permission",
                json={
                    "user_id": user_id,
                    "permission": permission,
                    "resource_type": resource_type,
                    "resource_id": resource_id
                }
            )
            
            return response.get("has_permission", False)
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    async def get_users_by_api_key(self, api_key: str) -> List[Dict[str, Any]]:
        """
        Get users who have access to a specific API key
        
        Used for broker API key management
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/trade-integration/users/by-api-key/{api_key}"
            )
            
            return response.get("users", [])
            
        except Exception as e:
            logger.error(f"Failed to get users by API key: {e}")
            return []
    
    async def validate_access(
        self, 
        user_id: int, 
        organization_id: int,
        pseudo_account_id: Optional[int] = None
    ) -> bool:
        """
        Validate user access to organization and optionally pseudo account
        """
        try:
            response = await self._make_request(
                method="POST",
                endpoint="/api/v1/trade-integration/auth/validate-access",
                json={
                    "user_id": user_id,
                    "organization_id": organization_id,
                    "pseudo_account_id": pseudo_account_id
                }
            )
            
            return response.get("has_access", False)
            
        except Exception as e:
            logger.error(f"Access validation failed: {e}")
            return False
    
    async def get_trading_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get trading accounts accessible by user
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/trade-integration/users/{user_id}/trading-accounts"
            )
            
            return response.get("trading_accounts", [])
            
        except Exception as e:
            logger.error(f"Failed to get trading accounts: {e}")
            return []
    
    async def log_audit_action(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Log audit action for compliance
        """
        try:
            response = await self._make_request(
                method="POST",
                endpoint="/api/v1/trade-integration/audit/log-action",
                json={
                    "user_id": user_id,
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "details": details,
                    "ip_address": ip_address,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return response.get("success", False)
            
        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")
            return False
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user details by ID
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/users/{user_id}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user details by email
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint="/api/v1/users/by-email",
                params={"email": email}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    async def get_user_permissions(self, user_id: int, organization_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get all permissions for a user
        """
        try:
            params = {}
            if organization_id:
                params["organization_id"] = organization_id
                
            response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/permissions/user/{user_id}",
                params=params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return {}
    
    async def get_user_trading_limits(self, user_id: int) -> Dict[str, Any]:
        """
        Get trading limits for a user
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/trading-limits/user/{user_id}"
            )
            
            return response.get("limits", {})
            
        except Exception as e:
            logger.error(f"Failed to get user trading limits: {e}")
            return {}
    
    async def validate_trading_limit(
        self,
        user_id: int,
        instrument_key: str,
        quantity: int,
        value: float,
        action: str = "BUY"
    ) -> Dict[str, Any]:
        """
        Validate if a trade is within user's limits
        """
        try:
            response = await self._make_request(
                method="POST",
                endpoint="/api/v1/trading-limits/validate",
                json={
                    "user_id": user_id,
                    "instrument_key": instrument_key,
                    "quantity": quantity,
                    "value": value,
                    "action": action
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to validate trading limit: {e}")
            return {"allowed": False, "reason": str(e)}
    
    async def get_tenant_api_keys(self, tenant_id: int) -> List[Dict[str, Any]]:
        """
        Get API keys for a tenant
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/tenants/{tenant_id}/api-keys"
            )
            
            return response.get("api_keys", [])
            
        except Exception as e:
            logger.error(f"Failed to get tenant API keys: {e}")
            return []
    
    async def create_user_context(self, token: str) -> Optional[UserContext]:
        """
        Create UserContext from JWT token
        
        This is a convenience method that validates the token
        and creates a UserContext object
        """
        try:
            # Validate token and get user info
            validation_result = await self.validate_token(token)
            
            if not validation_result.get("valid"):
                return None
            
            user_data = validation_result.get("user", {})
            
            # Create UserContext
            return UserContext(
                user_id=user_data.get("id"),
                email=user_data.get("email"),
                organization_id=user_data.get("organization_id"),
                role=user_data.get("role"),
                permissions=user_data.get("permissions", []),
                is_active=user_data.get("is_active", True)
            )
            
        except Exception as e:
            logger.error(f"Failed to create user context: {e}")
            return None
    
    # New permission methods for Sprint 3
    
    async def check_user_permission(
        self,
        user_id: int,
        permission: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None
    ) -> bool:
        """
        Check if user has a specific permission
        """
        try:
            response = await self._make_request(
                method="POST",
                endpoint="/api/v1/permissions/check",
                json={
                    "user_id": user_id,
                    "permission_name": permission,
                    "resource_type": resource_type,
                    "resource_id": resource_id
                }
            )
            
            return response.get("allowed", False)
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    async def sync_subscription_permissions(
        self,
        user_id: int,
        subscription_id: int,
        tier_name: str
    ) -> bool:
        """
        Sync user permissions based on subscription tier
        """
        try:
            response = await self._make_request(
                method="POST",
                endpoint="/api/v1/permissions/sync-subscription",
                json={
                    "user_id": user_id,
                    "subscription_id": subscription_id,
                    "tier_name": tier_name
                }
            )
            
            return response.get("success", False)
            
        except Exception as e:
            logger.error(f"Permission sync failed: {e}")
            return False
    
    async def get_tier_permissions(self, tier_name: str) -> Dict[str, Any]:
        """
        Get permissions for a subscription tier
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/permissions/subscription-tiers/{tier_name}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get tier permissions: {e}")
            return {}
    
    async def batch_check_permissions(
        self,
        user_id: int,
        permission_checks: List[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """
        Check multiple permissions at once
        """
        try:
            response = await self._make_request(
                method="POST",
                endpoint="/api/v1/permissions/batch/check",
                json={
                    "user_id": user_id,
                    "checks": permission_checks
                }
            )
            
            # Convert response to simple dict
            results = {}
            for key, result in response.get("results", {}).items():
                results[key] = result.get("allowed", False)
                
            return results
            
        except Exception as e:
            logger.error(f"Batch permission check failed: {e}")
            return {}
    
    async def validate_execution_context(
        self,
        user_id: int,
        strategy_id: str,
        requested_action: str = "execute"
    ) -> Dict[str, Any]:
        """
        Validate execution context for strategy execution
        """
        try:
            response = await self._make_request(
                method="POST",
                endpoint="/api/v1/permissions/validate-execution-context",
                json={
                    "user_id": user_id,
                    "strategy_id": strategy_id,
                    "requested_action": requested_action
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Execution context validation failed: {e}")
            return {"allowed": False}


# Global singleton instance
_user_service_client: Optional[UserServiceClient] = None


def get_user_service_client() -> UserServiceClient:
    """Get singleton instance of UserServiceClient"""
    global _user_service_client
    if _user_service_client is None:
        _user_service_client = UserServiceClient()
    return _user_service_client


async def initialize_user_service_client(base_url: Optional[str] = None):
    """Initialize the global UserServiceClient instance"""
    global _user_service_client
    _user_service_client = UserServiceClient(base_url=base_url)
    logger.info(f"UserServiceClient initialized with base_url: {base_url or 'default'}")
    return _user_service_client