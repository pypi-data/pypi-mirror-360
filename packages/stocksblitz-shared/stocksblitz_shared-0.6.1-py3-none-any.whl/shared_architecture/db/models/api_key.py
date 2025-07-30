# shared_architecture/db/models/api_key.py
"""
API Key Model - Core model for trade_service integration
Each API key belongs to a tenant and has specific permissions for trading accounts
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared_architecture.db.base import Base

class ApiKey(Base):
    """
    API Key for accessing the trading system
    - Owned by a tenant (organization)
    - Has specific permissions and restrictions
    - Used by trade_service for AutoTrader connections
    - Maps to specific trading accounts and their pseudo_accounts
    """
    __tablename__ = "api_keys"
    __table_args__ = {'schema': 'tradingdb'}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Key identification (the key_name is what trade_service uses)
    api_key_name = Column(String, nullable=False, unique=True, index=True)  # Used by trade_service
    display_name = Column(String, nullable=False)  # Human-readable name
    description = Column(Text)
    
    # Actual key credentials (for API authentication)
    api_key_hash = Column(String, nullable=False)  # Hashed key
    api_secret_hash = Column(String, nullable=False)  # Hashed secret
    
    # Ownership and management
    tenant_id = Column(Integer, ForeignKey("tradingdb.tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("tradingdb.users.id"), nullable=False)
    
    # Core permissions for this API key
    permissions = Column(JSON, default={
        "orders": {
            "view": True,
            "create": False,
            "modify": False,
            "cancel": False
        },
        "positions": {"view": True},
        "holdings": {"view": True},
        "margins": {"view": True},
        "strategies": {
            "view": False,
            "create": False,
            "modify": False
        }
    })
    
    # Trading account restrictions
    allowed_trading_accounts = Column(JSON, default=[])  # Empty = all tenant accounts
    blocked_trading_accounts = Column(JSON, default=[])  # Explicitly blocked accounts
    
    # Security restrictions
    allowed_ips = Column(JSON, default=[])  # Empty = all IPs allowed
    rate_limit_per_minute = Column(Integer, default=60)
    trading_hours_only = Column(Boolean, default=False)
    
    # Status and lifecycle
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True))
    last_used_ip = Column(String)
    usage_count = Column(Integer, default=0)
    
    # Expiry and rotation
    expires_at = Column(DateTime(timezone=True))  # Null = never expires
    should_rotate = Column(Boolean, default=False)  # Flag for key rotation
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    # tenant = relationship("Organization", back_populates="api_keys")
    # created_by = relationship("User", foreign_keys=[created_by_user_id])
    # usage_logs = relationship("ApiKeyUsageLog", back_populates="api_key")
    
    def __repr__(self):
        return f"<ApiKey(name='{self.api_key_name}', tenant_id={self.tenant_id})>"
    
    @property
    def can_access_trading_account(self, trading_account_id: int) -> bool:
        """Check if this API key can access a specific trading account"""
        if trading_account_id in self.blocked_trading_accounts:
            return False
        if not self.allowed_trading_accounts:  # Empty = all allowed
            return True
        return trading_account_id in self.allowed_trading_accounts