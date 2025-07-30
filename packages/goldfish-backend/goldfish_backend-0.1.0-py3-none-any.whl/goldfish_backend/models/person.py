"""
Person model for entity linking and human verification
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, String, Text, JSON


class Person(SQLModel, table=True):
    """Person entity table for people recognition and linking"""
    
    __tablename__ = "people"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(sa_column=Column(String(255)))
    aliases: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    importance_score: float = Field(default=1.0, ge=0.0, le=10.0)
    
    # Contact information
    bio: Optional[str] = Field(default=None, sa_column=Column(Text))
    email: Optional[str] = Field(default=None, sa_column=Column(String(255)))
    phone: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Status flags
    is_deleted: bool = Field(default=False)
    
    class Config:
        """SQLModel configuration"""
        from_attributes = True