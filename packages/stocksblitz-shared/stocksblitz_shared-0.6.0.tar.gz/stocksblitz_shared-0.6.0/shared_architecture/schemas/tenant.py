# shared_architecture/schemas/tenant.py
"""
Pydantic schemas for Tenant/Organization management
Used by user_service for multi-tenant operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class TenantCreateRequest(BaseModel):
    """Request schema for creating a new tenant/organization"""
    name: str = Field(..., min_length=2, max_length=255, description="Tenant name")
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    tenant_type: str = Field(default='individual', description="Type: individual, firm, institutional")
    
    # Initial settings
    max_users: Optional[int] = Field(default=5, ge=1, le=1000)
    max_trading_accounts: Optional[int] = Field(default=10, ge=1, le=100)
    max_api_keys: Optional[int] = Field(default=3, ge=1, le=50)
    
    @validator('tenant_type')
    def validate_tenant_type(cls, v):
        allowed_types = ['individual', 'firm', 'institutional', 'hedge_fund', 'bank']
        if v not in allowed_types:
            raise ValueError(f'Tenant type must be one of: {", ".join(allowed_types)}')
        return v


class TenantUpdateRequest(BaseModel):
    """Request schema for updating a tenant"""
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    # Settings updates
    max_users: Optional[int] = Field(None, ge=1, le=1000)
    max_trading_accounts: Optional[int] = Field(None, ge=1, le=100)
    max_api_keys: Optional[int] = Field(None, ge=1, le=50)
    
    # Status
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class TenantResponse(BaseModel):
    """Response schema for tenant data"""
    id: int
    name: str
    display_name: Optional[str]
    description: Optional[str]
    tenant_code: str
    tenant_type: str
    
    # Owner
    owner_user_id: int
    
    # Settings and limits
    max_users: int
    max_trading_accounts: int
    max_api_keys: int
    
    # Current usage
    current_users: Optional[int] = 0
    current_trading_accounts: Optional[int] = 0
    current_api_keys: Optional[int] = 0
    
    # Status
    is_active: bool
    is_verified: bool
    subscription_tier: str
    
    # Configuration
    settings: Dict[str, Any] = {}
    feature_flags: Dict[str, Any] = {}
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """Response for listing tenants"""
    tenants: List[TenantResponse]
    total: int
    page: int
    per_page: int


class UserTenantRoleRequest(BaseModel):
    """Request for adding/updating user role in tenant"""
    user_id: int
    role: str = Field(..., description="Role: owner, admin, trader, viewer")
    
    # Permissions
    permissions: Optional[Dict[str, Any]] = {}
    restrictions: Optional[Dict[str, Any]] = {}
    allowed_trading_accounts: Optional[List[int]] = []
    
    # Status
    is_active: bool = True
    invitation_status: str = 'active'
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['owner', 'admin', 'trader', 'viewer', 'compliance']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v


class UserTenantRoleResponse(BaseModel):
    """Response for user tenant role"""
    id: int
    user_id: int
    tenant_id: int
    role: str
    
    # User details
    user_email: Optional[str]
    user_name: Optional[str]
    
    # Permissions
    permissions: Dict[str, Any]
    restrictions: Dict[str, Any]
    allowed_trading_accounts: List[int]
    
    # Status
    is_active: bool
    
    # Invitation tracking (matching database schema)
    invitation_status: str
    invited_by: Optional[int]
    invited_at: Optional[datetime]
    activated_at: Optional[datetime]
    notes: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TenantInviteUserRequest(BaseModel):
    """Request for inviting a user to a tenant"""
    email: str = Field(..., description="Email of user to invite")
    role: str = Field(..., description="Role to assign")
    
    # Optional user details (if creating new user)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Permissions
    permissions: Optional[Dict[str, Any]] = {}
    allowed_trading_accounts: Optional[List[int]] = []
    
    # Invitation settings
    send_email: bool = True
    custom_message: Optional[str] = None


class TenantInviteResponse(BaseModel):
    """Response for tenant invitation"""
    invitation_id: str
    tenant_id: int
    user_email: str
    role: str
    status: str  # 'sent', 'accepted', 'expired', 'cancelled'
    
    # Links
    invitation_link: Optional[str] = None
    expires_at: datetime
    
    class Config:
        from_attributes = True


class TenantStatsResponse(BaseModel):
    """Response for tenant statistics"""
    tenant_id: int
    tenant_name: str
    
    # Usage stats
    total_users: int
    active_users: int
    total_api_keys: int
    active_api_keys: int
    total_trading_accounts: int
    active_trading_accounts: int
    
    # Activity stats
    api_calls_today: int
    api_calls_this_month: int
    orders_today: int
    orders_this_month: int
    
    # Limits
    max_users: int
    max_api_keys: int
    max_trading_accounts: int
    
    # Calculated fields
    users_usage_percent: float
    api_keys_usage_percent: float
    trading_accounts_usage_percent: float