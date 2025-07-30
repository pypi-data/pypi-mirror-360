"""
Relationship models for many-to-many entity linking
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, String


# Task relationship models
class TaskPerson(SQLModel, table=True):
    """Many-to-many relationship between tasks and people"""
    
    __tablename__ = "task_people"
    
    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    person_id: int = Field(foreign_key="people.id", primary_key=True)
    relationship_type: str = Field(default="mentioned", sa_column=Column(String(20)))
    strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class TaskProject(SQLModel, table=True):
    """Many-to-many relationship between tasks and projects"""
    
    __tablename__ = "task_projects"
    
    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    project_id: int = Field(foreign_key="projects.id", primary_key=True)
    relationship_type: str = Field(default="part_of", sa_column=Column(String(20)))
    strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class TaskTopic(SQLModel, table=True):
    """Many-to-many relationship between tasks and topics"""
    
    __tablename__ = "task_topics"
    
    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    topic_id: int = Field(foreign_key="topics.id", primary_key=True)
    relationship_type: str = Field(default="researches", sa_column=Column(String(20)))
    strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# Note relationship models
class NotePerson(SQLModel, table=True):
    """Many-to-many relationship between notes and people"""
    
    __tablename__ = "note_people"
    
    note_id: int = Field(foreign_key="notes.id", primary_key=True)
    person_id: int = Field(foreign_key="people.id", primary_key=True)
    mention_type: str = Field(default="mentioned", sa_column=Column(String(20)))
    mention_count: int = Field(default=1, gt=0)
    strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NoteProject(SQLModel, table=True):
    """Many-to-many relationship between notes and projects"""
    
    __tablename__ = "note_projects"
    
    note_id: int = Field(foreign_key="notes.id", primary_key=True)
    project_id: int = Field(foreign_key="projects.id", primary_key=True)
    mention_type: str = Field(default="mentioned", sa_column=Column(String(20)))
    mention_count: int = Field(default=1, gt=0)
    strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NoteTopic(SQLModel, table=True):
    """Many-to-many relationship between notes and topics"""
    
    __tablename__ = "note_topics"
    
    note_id: int = Field(foreign_key="notes.id", primary_key=True)
    topic_id: int = Field(foreign_key="topics.id", primary_key=True)
    mention_type: str = Field(default="discusses", sa_column=Column(String(20)))
    mention_count: int = Field(default=1, gt=0)
    strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Topic relationship models
class TopicRelationship(SQLModel, table=True):
    """Two-way relationships between topics for knowledge graph"""
    
    __tablename__ = "topic_relationships"
    
    from_topic_id: int = Field(foreign_key="topics.id", primary_key=True)
    to_topic_id: int = Field(foreign_key="topics.id", primary_key=True)
    relationship_type: str = Field(sa_column=Column(String(30)))  # related_to, prerequisite_of, part_of, contradicts, extends
    strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TopicPerson(SQLModel, table=True):
    """Relationships between topics and people (experts, researchers)"""
    
    __tablename__ = "topic_people"
    
    topic_id: int = Field(foreign_key="topics.id", primary_key=True)
    person_id: int = Field(foreign_key="people.id", primary_key=True)
    relationship_type: str = Field(default="expert_in", sa_column=Column(String(20)))
    strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class TopicProject(SQLModel, table=True):
    """Relationships between topics and projects"""
    
    __tablename__ = "topic_projects"
    
    topic_id: int = Field(foreign_key="topics.id", primary_key=True)
    project_id: int = Field(foreign_key="projects.id", primary_key=True)
    relationship_type: str = Field(default="implements", sa_column=Column(String(20)))
    strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True