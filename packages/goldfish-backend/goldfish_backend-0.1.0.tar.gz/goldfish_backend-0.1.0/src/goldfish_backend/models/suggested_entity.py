"""
Suggested entity model for human-in-the-loop verification
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, String, Text, JSON


class SuggestedEntity(SQLModel, table=True):
    """Suggested entity table for AI suggestions awaiting human verification"""
    
    __tablename__ = "suggested_entities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    note_id: int = Field(foreign_key="notes.id")
    entity_type: str = Field(sa_column=Column(String(20)))  # person, project, topic
    name: str = Field(sa_column=Column(String(255)))
    context: str = Field(sa_column=Column(Text))
    confidence: float = Field(ge=0.0, le=1.0)
    status: str = Field(default="pending", sa_column=Column(String(20)))  # pending, confirmed, rejected
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Additional AI processing metadata
    ai_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    class Config:
        """SQLModel configuration"""
        from_attributes = True