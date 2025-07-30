"""
Project model for organizing work and goals
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, String, Text, JSON


class Project(SQLModel, table=True):
    """Project entity table for work and goal organization"""
    
    __tablename__ = "projects"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(sa_column=Column(String(255)))
    aliases: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    deadline: Optional[datetime] = None
    status: str = Field(default="active", sa_column=Column(String(20)))  # active, completed, archived, on_hold
    priority_score: float = Field(default=1.0, ge=0.0, le=10.0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Status flags
    is_deleted: bool = Field(default=False)
    
    class Config:
        """SQLModel configuration"""
        from_attributes = True