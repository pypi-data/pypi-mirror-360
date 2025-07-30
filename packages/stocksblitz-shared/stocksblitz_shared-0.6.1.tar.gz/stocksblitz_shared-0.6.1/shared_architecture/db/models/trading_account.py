# shared_architecture/db/models/trading_account.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared_architecture.db.base import Base

class TradingAccount(Base):
    """
    Trading Account model - represents a broker account connected to the system
    This is NOT a user account, but an actual trading account at a broker (ICICI, Zerodha, etc.)
    Multiple users can have access to trade or view this account based on permissions
    """
    __tablename__ = "trading_accounts"
    __table_args__ = {'schema': 'tradingdb'}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core trading account identifiers
    login_id = Column(String, nullable=False, index=True)  # Broker login ID (e.g., "DSINHA")
    account_name = Column(String, nullable=False)          # Friendly name (e.g., "Main ICICI Account")
    broker = Column(String, nullable=False, index=True)    # Broker name (e.g., "ICICI Direct")
    platform = Column(String, nullable=False)              # Platform/System (e.g., "Breeze")
    
    # Broker-specific identifiers
    system_id = Column(BigInteger, nullable=False, index=True)              # From broker API
    system_id_of_pseudo_acc = Column(BigInteger, nullable=False, index=True) # From broker API
    
    # License and status information
    license_expiry_date = Column(String, nullable=True)    # Broker license expiry
    license_days_left = Column(Integer, nullable=True)     # Days until expiry
    is_live = Column(Boolean, default=False, nullable=False) # Live vs Paper trading
    
    # Organization/Tenant relationship (which organization/workspace owns this account)
    # TODO: Rename to tenant_id once we migrate from organizations to tenants table
    organization_id = Column(Integer, ForeignKey("tradingdb.organizations.id"), nullable=False, index=True)
    
    # Legacy user assignment - will be replaced by permission system
    assigned_user_id = Column(Integer, ForeignKey("tradingdb.users.id"), nullable=True, index=True)
    
    # Note: In future, users will get access through tenant permissions, not direct assignment
    
    # Status and timestamps
    is_active = Column(Boolean, default=True, nullable=False)
    imported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_synced_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional fields for user login (may be populated later)
    trading_password_hash = Column(String, nullable=True)  # For direct broker login if needed
    additional_credentials = Column(String, nullable=True)  # JSON field for extra broker-specific data
    
    # Relationships (commented out to avoid import issues)
    # organization = relationship("Organization", back_populates="trading_accounts")
    # assigned_user = relationship("User", back_populates="assigned_trading_accounts")
    # permissions = relationship("TradingAccountPermission", back_populates="trading_account", cascade="all, delete-orphan")
    # strategies = relationship("Strategy", back_populates="trading_account", cascade="all, delete-orphan")
    
    @property
    def account_identifier(self):
        """Unique identifier for this trading account"""
        return f"{self.broker}:{self.login_id}"
    
    @property
    def is_license_expired(self):
        """Check if license is expired"""
        return self.license_days_left is not None and self.license_days_left <= 0
    
    @property
    def users_with_access(self):
        """Get list of users who have access to this account"""
        # users = []
        # if self.assigned_user:
        #     users.append(self.assigned_user)
        # 
        # # Add users with explicit permissions
        # for permission in self.permissions:
        #     if permission.user not in users:
        #         users.append(permission.user)
        # 
        # return users
        return []  # Temporarily disabled
    
    @property
    def active_strategies(self):
        """Get list of active strategies in this account"""
        # return [strategy for strategy in self.strategies if strategy.is_active and strategy.is_running]
        return []  # Temporarily disabled
    
    @property
    def total_strategies(self):
        """Get total number of strategies"""
        # return len(self.strategies)
        return 0  # Temporarily disabled
    
    @property
    def strategies_pnl(self):
        """Get total P&L across all strategies"""
        # return sum(strategy.total_pnl for strategy in self.strategies if strategy.total_pnl)
        return 0  # Temporarily disabled