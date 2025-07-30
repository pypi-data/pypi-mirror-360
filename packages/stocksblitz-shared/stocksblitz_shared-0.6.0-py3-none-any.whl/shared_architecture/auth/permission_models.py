# shared_architecture/auth/permission_models.py
"""
Three-tier permission system for strategy execution
1. User Service: Defines permissions (roles, organization membership)
2. Subscription Service: Authorizes based on subscriptions & tiers
3. Execution Engine: Validates before execution
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class PermissionLevel(str, Enum):
    """Permission levels from most to least restrictive"""
    NONE = "none"
    VIEW_ONLY = "view_only"
    EXECUTE_ONLY = "execute_only"
    EXECUTE_AND_MODIFY = "execute_and_modify"
    FULL_ACCESS = "full_access"


class SubscriptionTier(str, Enum):
    """Subscription tiers with different capabilities"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ExecutionContext(BaseModel):
    """Context for permission validation"""
    user_id: str
    strategy_id: str
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    requested_action: str = Field(default="execute")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserPermission(BaseModel):
    """User-level permissions from user_service"""
    user_id: str
    roles: List[str] = Field(default_factory=list)
    organizations: Dict[str, str] = Field(default_factory=dict)  # org_id -> role
    global_permissions: List[str] = Field(default_factory=list)
    resource_permissions: Dict[str, List[str]] = Field(default_factory=dict)  # resource_id -> actions
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class SubscriptionAuthorization(BaseModel):
    """Subscription-based authorization from subscription_service"""
    subscription_id: str
    user_id: str
    tier: SubscriptionTier
    strategy_access: Dict[str, PermissionLevel] = Field(default_factory=dict)  # strategy_id -> level
    rate_limits: Dict[str, int] = Field(default_factory=dict)
    usage_quota: Dict[str, int] = Field(default_factory=dict)
    features_enabled: List[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
    is_valid: bool = True


class ValidationResult(BaseModel):
    """Final validation result from execution_engine"""
    allowed: bool
    permission_level: PermissionLevel
    reasons: List[str] = Field(default_factory=list)
    
    # User permission check
    user_check_passed: bool = False
    user_check_reason: Optional[str] = None
    
    # Subscription authorization check
    subscription_check_passed: bool = False
    subscription_check_reason: Optional[str] = None
    
    # Additional validation checks
    rate_limit_check_passed: bool = True
    quota_check_passed: bool = True
    feature_check_passed: bool = True
    
    # Metadata for logging
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    validation_duration_ms: Optional[float] = None
    cache_hit: bool = False


class PermissionRequest(BaseModel):
    """Request for permission check across services"""
    context: ExecutionContext
    required_level: PermissionLevel = PermissionLevel.EXECUTE_ONLY
    check_rate_limits: bool = True
    check_quotas: bool = True
    bypass_cache: bool = False


class PermissionResponse(BaseModel):
    """Response from permission services"""
    request_id: str
    result: ValidationResult
    user_permission: Optional[UserPermission] = None
    subscription_auth: Optional[SubscriptionAuthorization] = None
    ttl_seconds: int = 300  # Cache TTL