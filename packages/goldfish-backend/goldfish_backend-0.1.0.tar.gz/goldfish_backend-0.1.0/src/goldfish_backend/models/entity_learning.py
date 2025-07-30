"""
Entity learning model for improving AI accuracy from user feedback
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, String, Text, JSON


class EntityLearning(SQLModel, table=True):
    """Entity learning table for recording user confirmations to improve AI"""
    
    __tablename__ = "entity_learning"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    original_text: str = Field(sa_column=Column(String(500)))
    linked_entity_id: int
    entity_type: str = Field(sa_column=Column(String(20)))  # person, project, topic
    context: str = Field(sa_column=Column(Text))
    source_file_path: str = Field(sa_column=Column(String(1000)))
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional learning context
    learning_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    class Config:
        """SQLModel configuration"""
        from_attributes = True