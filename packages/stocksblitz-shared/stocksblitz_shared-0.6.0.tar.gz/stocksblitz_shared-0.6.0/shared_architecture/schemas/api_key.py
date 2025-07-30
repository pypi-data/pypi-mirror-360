# shared_architecture/schemas/api_key.py
"""
Pydantic schemas for API Key management
Used by user_service and trade_service for API key operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ApiKeyPermissions(BaseModel):
    """Structured permissions for an API key"""
    orders: Dict[str, bool] = {
        "view": True,
        "create": False,
        "modify": False,
        "cancel": False
    }
    positions: Dict[str, bool] = {"view": True}
    holdings: Dict[str, bool] = {"view": True}
    margins: Dict[str, bool] = {"view": True}
    strategies: Dict[str, bool] = {
        "view": False,
        "create": False,
        "modify": False
    }


class ApiKeyCreateRequest(BaseModel):
    """Request schema for creating a new API key"""
    api_key_name: str = Field(..., min_length=3, max_length=100, description="Unique name for the API key")
    display_name: str = Field(..., min_length=1, max_length=200, description="Human-readable name")
    description: Optional[str] = Field(None, max_length=1000)
    
    # Optional AutoTrader credentials (if provided, triggers validation and workflow)
    api_key: Optional[str] = Field(None, description="AutoTrader API key (optional)")
    api_secret: Optional[str] = Field(None, description="AutoTrader API secret (optional)")
    
    # Permissions
    permissions: Optional[ApiKeyPermissions] = None
    
    # Restrictions
    allowed_trading_accounts: Optional[List[int]] = Field(default=[], description="Trading account IDs allowed (empty = all)")
    blocked_trading_accounts: Optional[List[int]] = Field(default=[], description="Trading account IDs blocked")
    allowed_ips: Optional[List[str]] = Field(default=[], description="Allowed IP addresses (empty = all)")
    rate_limit_per_minute: Optional[int] = Field(default=60, ge=1, le=1000)
    trading_hours_only: Optional[bool] = Field(default=False)
    
    # Expiry
    expires_at: Optional[datetime] = None
    
    @validator('api_key_name')
    def validate_api_key_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('API key name must contain only letters, numbers, hyphens, and underscores')
        return v
    
    @validator('api_secret')
    def validate_api_credentials(cls, v, values):
        # If api_key is provided, api_secret must also be provided
        api_key = values.get('api_key')
        if api_key and not v:
            raise ValueError('API secret is required when API key is provided')
        if v and not api_key:
            raise ValueError('API key is required when API secret is provided')
        return v


class ApiKeyUpdateRequest(BaseModel):
    """Request schema for updating an API key"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    
    # Permissions
    permissions: Optional[ApiKeyPermissions] = None
    
    # Restrictions
    allowed_trading_accounts: Optional[List[int]] = None
    blocked_trading_accounts: Optional[List[int]] = None
    allowed_ips: Optional[List[str]] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000)
    trading_hours_only: Optional[bool] = None
    
    # Status
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class ApiKeyResponse(BaseModel):
    """Response schema for API key data"""
    id: int
    api_key_name: str
    display_name: str
    description: Optional[str]
    
    # Ownership
    tenant_id: int
    created_by_user_id: int
    
    # Permissions and restrictions
    permissions: Dict[str, Any]
    allowed_trading_accounts: List[int]
    blocked_trading_accounts: List[int]
    allowed_ips: List[str]
    rate_limit_per_minute: int
    trading_hours_only: bool
    
    # Status
    is_active: bool
    last_used_at: Optional[datetime]
    last_used_ip: Optional[str]
    usage_count: int
    expires_at: Optional[datetime]
    should_rotate: bool
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ApiKeyWithSecrets(ApiKeyResponse):
    """API key response that includes the actual key and secret (only for creation)"""
    api_key: str = Field(..., description="The actual API key (only shown once)")
    api_secret: str = Field(..., description="The API secret (only shown once)")


class ApiKeyListResponse(BaseModel):
    """Response for listing API keys"""
    api_keys: List[ApiKeyResponse]
    total: int
    page: int
    per_page: int


class ApiKeyUsageLogEntry(BaseModel):
    """Schema for API key usage logging"""
    api_key_name: str
    endpoint: str
    method: str
    ip_address: str
    user_agent: Optional[str]
    status_code: int
    response_time_ms: int
    timestamp: datetime
    
    # Trading context
    trading_account_id: Optional[int] = None
    order_id: Optional[str] = None
    
    # Errors
    error_message: Optional[str] = None


class ApiKeyAuthRequest(BaseModel):
    """Schema for API key authentication (used by trade_service)"""
    api_key_name: str = Field(..., description="The API key name to authenticate")
    api_key: str = Field(..., description="The API key")
    api_secret: str = Field(..., description="The API secret")


class ApiKeyAuthResponse(BaseModel):
    """Response for API key authentication"""
    is_valid: bool
    tenant_id: Optional[int] = None
    permissions: Optional[Dict[str, Any]] = None
    allowed_trading_accounts: Optional[List[int]] = None
    rate_limit_per_minute: Optional[int] = None
    
    # Error details
    error_code: Optional[str] = None  # 'invalid_key', 'expired', 'rate_limited', 'ip_blocked'
    error_message: Optional[str] = None


class TradingAccountPermissionCheck(BaseModel):
    """Schema for checking if API key can access a trading account"""
    api_key_name: str
    trading_account_id: int
    operation: str = Field(..., description="Operation to check: 'view', 'trade', 'modify'")


class TradingAccountPermissionResponse(BaseModel):
    """Response for trading account permission check"""
    allowed: bool
    reason: Optional[str] = None  # Explanation if not allowed