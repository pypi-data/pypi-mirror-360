from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

class UserCreateSchema(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)  # Changed from phone_number to match DB

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.startswith('+'):
            # Auto-format phone if it doesn't start with +
            if v.startswith('1') and len(v) == 11:
                v = '+' + v
            elif len(v) == 10:
                v = '+1' + v
        return v


class UserUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)  # Changed from phone_number to match DB

class UserResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str]  # Changed from phone_number to match DB
    is_active: bool
    email_verified: bool
    phone_verified: bool

    class Config:
        from_attributes = True