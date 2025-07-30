"""
Task model for actionable items extracted from notes
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, String, Text


class Task(SQLModel, table=True):
    """Task table for actionable items with AI-calculated priorities"""
    
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    note_id: int = Field(foreign_key="notes.id")
    content: str = Field(sa_column=Column(Text))
    status: str = Field(default="pending", sa_column=Column(String(20)))  # pending, in_progress, completed, cancelled
    priority_score: float = Field(default=0.0, ge=0.0, le=10.0)
    position: int = Field(default=0)  # Position in kanban column
    due_date: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Status flags
    is_deleted: bool = Field(default=False)
    
    class Config:
        """SQLModel configuration"""
        from_attributes = True