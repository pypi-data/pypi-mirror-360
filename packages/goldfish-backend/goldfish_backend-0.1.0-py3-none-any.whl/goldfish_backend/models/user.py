"""
User model for authentication and user management
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, String


class User(SQLModel, table=True):
    """User table for authentication and profile information"""
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True))
    hashed_password: str
    full_name: str
    bio: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Status flags
    is_active: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    
    class Config:
        """SQLModel configuration"""
        from_attributes = True