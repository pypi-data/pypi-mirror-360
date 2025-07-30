# shared_architecture/db/models/tenant.py
"""
Tenant Model - Represents the top-level account holder (formerly called organization)
This is the entity that owns API keys and manages sub-users
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared_architecture.db.base import Base

class Tenant(Base):
    """
    Tenant represents the main account holder who:
    - Logs into the trading dashboard
    - Owns one or more API keys
    - Can create sub-users (pseudo accounts)
    - Manages trading accounts
    """
    __tablename__ = "tenants"
    __table_args__ = {'schema': 'tradingdb'}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant identification
    name = Column(String, nullable=False, unique=True)
    display_name = Column(String)
    tenant_code = Column(String, unique=True, nullable=False)  # Unique identifier like "TENANT001"
    
    # Primary owner of this tenant account
    owner_user_id = Column(Integer, ForeignKey("tradingdb.users.id"), nullable=False)
    
    # Tenant details
    description = Column(String)
    tenant_type = Column(String, default='individual')  # individual, firm, institutional
    
    # Configuration
    settings = Column(JSON, default={})
    feature_flags = Column(JSON, default={})
    
    # Subscription and limits
    subscription_tier = Column(String, default='basic')  # basic, premium, enterprise
    max_users = Column(Integer, default=5)
    max_trading_accounts = Column(Integer, default=10)
    max_api_keys = Column(Integer, default=3)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships will be added after all models are defined
    # owner = relationship("User", foreign_keys=[owner_user_id])
    # api_keys = relationship("ApiKey", back_populates="tenant")
    # users = relationship("UserTenantRole", back_populates="tenant")
    # trading_accounts = relationship("TradingAccount", back_populates="tenant")