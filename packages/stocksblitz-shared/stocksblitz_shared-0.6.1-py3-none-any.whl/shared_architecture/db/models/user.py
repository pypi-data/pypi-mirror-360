# shared_architecture/db/models/user.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared_architecture.db.base import Base


class User(Base):
    """
    User model - represents actual people who log into the system
    Users belong to tenants through groups and inherit permissions
    """
    __tablename__ = "users"
    __table_args__ = {'schema': 'tradingdb'}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal information (matching database schema)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)  # Changed from phone_number
    
    # Profile picture
    avatar = Column(String(500), nullable=True)  # Changed from avatar_url
    
    # User preferences and settings
    preferences = Column(JSON, default={})
    
    # Status (matching database schema)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)  # Changed from last_login_at
    email_verified = Column(Boolean, default=False)  # Changed from is_email_verified
    phone_verified = Column(Boolean, default=False)  # Changed from is_phone_verified
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships (multi-tenant support)
    tenant_roles = relationship("UserTenantRole", foreign_keys="UserTenantRole.user_id", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    @property
    def display_name(self):
        """Name to display in UI"""
        return self.full_name
    
    @property
    def accessible_trading_accounts(self):
        """Get all trading accounts this user can access (legacy)"""
        return []  # Will be implemented with new permission system
    
    @property
    def is_organization_owner(self):
        """Check if user owns any organizations (legacy)"""
        return False  # Will be implemented with new permission system
    
    @property
    def is_organization_backup_owner(self):
        """Check if user is backup owner of any organizations (legacy)"""
        return False  # Will be implemented with new permission system
    
    def get_tenant_role(self, tenant_id: int):
        """Get user's role in a specific tenant"""
        # This will be implemented when relationships are active
        pass
    
    def has_permission_in_tenant(self, tenant_id: int, permission: str) -> bool:
        """Check if user has a specific permission in a tenant"""
        # This will be implemented when relationships are active
        pass