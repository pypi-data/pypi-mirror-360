"""
Pydantic schemas for API request/response models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str
    bio: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserResponse(UserBase):
    """User response schema"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    bio: Optional[str] = None


# Authentication schemas
class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None