"""User context model for authentication and authorization"""
from typing import List, Optional
from pydantic import BaseModel
from ..enums import UserRole


class UserContext(BaseModel):
    """User context extracted from JWT or authentication system"""
    user_id: str
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    local_user_role: Optional[UserRole] = None
    groups: List[str] = []
    organization_id: Optional[int] = None
    role: Optional[str] = None  # Single role for simplified access
    is_active: bool = True
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        return role in self.roles or role == self.role
    
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.local_user_role == UserRole.ADMIN or "admin" in self.roles
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return bool(self.user_id) and self.is_active