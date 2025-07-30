# shared_architecture/db/models/group.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared_architecture.db.base import Base

class Group(Base):
    """
    Group model for organizing users within a tenant/organization
    Groups help manage permissions for teams, departments, or projects
    """
    __tablename__ = "groups"
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='groups_organization_id_name_key'),
        {'schema': 'tradingdb'}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Group identification (matching database schema)
    organization_id = Column(Integer, nullable=False, index=True)  # Changed from tenant_id
    name = Column(String(255), nullable=False)
    description = Column(String)  # TEXT in DB
    
    # Group permissions (matching database schema)
    permissions = Column(JSON, default={})  # Changed from default_permissions
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    # owner = relationship("User", foreign_keys=[owner_id])
    group_memberships = relationship("UserGroup", back_populates="group")


class UserGroup(Base):
    """
    Many-to-many relationship between Users and Groups
    Tracks user membership in groups with additional role information
    """
    __tablename__ = "user_groups"
    __table_args__ = (
        UniqueConstraint('user_id', 'group_id', name='uq_user_group'),
        {'schema': 'tradingdb'}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("tradingdb.users.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("tradingdb.groups.id"), nullable=False, index=True)
    
    # Role within the group (matching database schema)
    role = Column(String(50), default='member')  # Changed from role_in_group
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User")
    group = relationship("Group", back_populates="group_memberships")


class GroupTradingAccount(Base):
    """
    Defines which trading accounts a group has access to and with what permissions
    """
    __tablename__ = "group_trading_accounts"
    __table_args__ = (
        UniqueConstraint('group_id', 'trading_account_id', name='uq_group_trading_account'),
        {'schema': 'tradingdb'}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("tradingdb.groups.id"), nullable=False, index=True)
    trading_account_id = Column(Integer, ForeignKey("tradingdb.trading_accounts.id"), nullable=False, index=True)
    
    # Permission level for this group on this trading account
    permission_level = Column(String, nullable=False, default='view_only')  # 'full_trade', 'limited_trade', 'view_only'
    
    # Additional restrictions (JSON format for flexibility)
    restrictions = Column(JSON, default={})  # Time limits, order size limits, etc.
    
    # Timestamps
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    granted_by = Column(Integer, ForeignKey("tradingdb.users.id"))
    
    # Relationships
    # group = relationship("Group", back_populates="trading_account_permissions")
    # trading_account = relationship("TradingAccount", back_populates="group_permissions")
    # granted_by_user = relationship("User", foreign_keys=[granted_by])