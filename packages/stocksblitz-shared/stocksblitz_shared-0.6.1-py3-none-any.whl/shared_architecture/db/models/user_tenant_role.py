# shared_architecture/db/models/user_tenant_role.py
"""
User-Tenant Role Model - Junction table for user-tenant relationships
Handles roles, permissions, and access control in multi-tenant system
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared_architecture.db.base import Base


class UserTenantRole(Base):
    """
    User-Tenant Role mapping with permissions
    - Links users to tenants with specific roles
    - Handles granular permissions and restrictions
    - Supports invitation workflow
    - Allows users to belong to multiple tenants
    """
    __tablename__ = "user_tenant_roles"
    __table_args__ = (
        UniqueConstraint('user_id', 'tenant_id', name='uix_user_tenant'),
        {'schema': 'tradingdb'}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core relationship
    user_id = Column(Integer, ForeignKey("tradingdb.users.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tradingdb.tenants.id"), nullable=False, index=True)
    
    # Role within the tenant
    role = Column(String, nullable=False, default='viewer')  # owner, admin, trader, viewer, compliance
    
    # Granular permissions (JSON structure)
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
        },
        "reports": {"view": False},
        "admin": {
            "users": False,
            "api_keys": False,
            "settings": False
        }
    })
    
    # Restrictions (JSON structure)
    restrictions = Column(JSON, default={
        "trading_hours_only": False,
        "max_order_value": None,
        "allowed_instruments": [],  # Empty = all allowed
        "blocked_instruments": [],
        "rate_limits": {
            "orders_per_minute": None,
            "api_calls_per_minute": None
        }
    })
    
    # Trading account access
    allowed_trading_accounts = Column(JSON, default=[])  # Empty = all tenant accounts allowed
    
    # Status flags
    is_active = Column(Boolean, default=True)
    
    # Invitation tracking (matching database schema)
    invitation_status = Column(String(50), default='active')  # 'pending', 'active', 'expired', 'revoked'
    invited_by = Column(Integer, ForeignKey("tradingdb.users.id"), nullable=True)
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    activated_at = Column(DateTime(timezone=True))
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="tenant_roles")
    tenant = relationship("Tenant", foreign_keys=[tenant_id])  # Removed back_populates for now
    invited_by_user = relationship("User", foreign_keys=[invited_by])
    
    def __repr__(self):
        return f"<UserTenantRole(user_id={self.user_id}, tenant_id={self.tenant_id}, role='{self.role}')>"
    
    @property
    def role_display_name(self):
        """Human-readable role name"""
        role_names = {
            'owner': 'Owner',
            'admin': 'Administrator',
            'trader': 'Trader',
            'viewer': 'Viewer',
            'compliance': 'Compliance Officer'
        }
        return role_names.get(self.role, self.role.title())
    
    def has_permission(self, category: str, action: str) -> bool:
        """Check if user has a specific permission"""
        if not self.is_active:
            return False
        
        # Owner has all permissions
        if self.role == 'owner':
            return True
        
        # Check specific permission
        if category in self.permissions:
            return self.permissions[category].get(action, False)
        
        return False
    
    def can_access_trading_account(self, trading_account_id: int) -> bool:
        """Check if user can access a specific trading account"""
        if not self.is_active:
            return False
        
        # Owner and admin have access to all tenant accounts
        if self.role in ['owner', 'admin']:
            return True
        
        # Check allowed list (empty = all allowed)
        if not self.allowed_trading_accounts:
            return True
        
        return trading_account_id in self.allowed_trading_accounts
    
    def get_effective_permissions(self) -> dict:
        """Get effective permissions considering role hierarchy"""
        base_permissions = self.permissions.copy()
        
        # Owner gets all permissions
        if self.role == 'owner':
            return {
                "orders": {"view": True, "create": True, "modify": True, "cancel": True},
                "positions": {"view": True},
                "holdings": {"view": True},
                "margins": {"view": True},
                "strategies": {"view": True, "create": True, "modify": True},
                "reports": {"view": True},
                "admin": {"users": True, "api_keys": True, "settings": True}
            }
        
        # Admin gets enhanced permissions
        elif self.role == 'admin':
            base_permissions["admin"]["users"] = True
            base_permissions["admin"]["api_keys"] = True
            base_permissions["reports"]["view"] = True
        
        # Trader gets trading permissions
        elif self.role == 'trader':
            base_permissions["orders"]["create"] = True
            base_permissions["orders"]["modify"] = True
            base_permissions["orders"]["cancel"] = True
        
        return base_permissions