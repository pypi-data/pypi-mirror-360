"""
Topic model for research, learning, and knowledge organization
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, String, Text, JSON


class Topic(SQLModel, table=True):
    """Topic entity table for research and knowledge organization"""
    
    __tablename__ = "topics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(sa_column=Column(String(255)))
    aliases: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    category: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    research_score: float = Field(default=1.0, ge=0.0, le=10.0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Status flags
    is_deleted: bool = Field(default=False)
    
    class Config:
        """SQLModel configuration"""
        from_attributes = True