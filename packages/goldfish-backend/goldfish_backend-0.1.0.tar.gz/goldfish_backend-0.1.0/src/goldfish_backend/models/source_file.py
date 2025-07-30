"""
Source file model for tracking user's monitored files
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, String


class SourceFile(SQLModel, table=True):
    """Source file table for tracking user's monitored files"""
    
    __tablename__ = "source_files"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    file_path: str = Field(sa_column=Column(String(1000)))
    relative_path: str = Field(sa_column=Column(String(1000)))
    file_hash: str = Field(sa_column=Column(String(64), index=True))
    file_size: int
    last_modified: datetime
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Status flags
    is_watched: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    
    class Config:
        """SQLModel configuration"""
        from_attributes = True