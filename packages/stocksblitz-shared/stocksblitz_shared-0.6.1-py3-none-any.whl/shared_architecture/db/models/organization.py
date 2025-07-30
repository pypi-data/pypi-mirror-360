# shared_architecture/db/models/organization.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared_architecture.db.base import Base

class Organization(Base):
    """
    Organization/Group model with API key management
    An organization represents a trading group with shared API access
    """
    __tablename__ = "organizations"
    __table_args__ = {'schema': 'tradingdb'}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Ownership structure
    owner_id = Column(Integer, ForeignKey("tradingdb.users.id"), nullable=True, index=True)
    backup_owner_id = Column(Integer, ForeignKey("tradingdb.users.id"), nullable=True, index=True)
    
    # Tenant specific fields (aligned with database schema)
    tenant_code = Column(String(50), unique=True, nullable=True)
    tenant_type = Column(String(50), default='individual')
    subscription_tier = Column(String(50), default='basic')
    max_users = Column(Integer, default=5)
    max_trading_accounts = Column(Integer, default=10)
    max_api_keys = Column(Integer, default=3)
    settings = Column(JSON, default={})
    feature_flags = Column(JSON, default={})
    is_verified = Column(Boolean, default=False)
    
    # Status and timestamps
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    backup_owner = relationship("User", foreign_keys=[backup_owner_id])
    
    trading_accounts = relationship("TradingAccount", cascade="all, delete-orphan")
    account_permissions = relationship("TradingAccountPermission", cascade="all, delete-orphan")
    
    # Multi-tenant relationships - DISABLED since we're using Tenant model now
    # user_roles = relationship("UserTenantRole", back_populates="tenant")
    # groups = relationship("Group", back_populates="tenant")
    
    @property
    def total_accounts(self):
        """Get total number of trading accounts"""
        return len(self.trading_accounts)
    
    @property
    def active_accounts(self):
        """Get active trading accounts"""
        return [acc for acc in self.trading_accounts if acc.is_active]
    
    @property
    def display_name(self):
        """Return display name for the organization"""
        return f"{self.name} ({self.tenant_code})" if self.tenant_code else self.name