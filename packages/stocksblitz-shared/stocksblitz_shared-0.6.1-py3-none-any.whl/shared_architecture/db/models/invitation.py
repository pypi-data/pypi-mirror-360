from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from shared_architecture.db.base import Base

class UserInvitation(Base):
    __tablename__ = "user_invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    role = Column(String(50), nullable=False)
    department = Column(String(100))
    
    # Organization
    organization_id = Column(String(50), ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="invitations")
    
    # Invitation details
    invitation_code = Column(String(100), unique=True, nullable=False, index=True)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    inviter = relationship("User", foreign_keys=[invited_by])
    
    # Status tracking
    status = Column(String(20), default="pending")  # pending, accepted, expired, cancelled
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    cancelled_by = Column(Integer, ForeignKey("users.id"))
    
    # Permissions to grant
    permissions = Column(JSON, default={})
    personal_message = Column(Text)
    
    # Link to created user
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", foreign_keys=[user_id])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserInvitation(email='{self.email}', status='{self.status}')>"