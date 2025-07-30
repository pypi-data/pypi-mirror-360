"""
Database models for Goldfish backend
"""

# Import all models for SQLModel table creation
from .user import User
from .source_file import SourceFile
from .note import Note
from .person import Person
from .project import Project
from .topic import Topic
from .task import Task
from .suggested_entity import SuggestedEntity
from .entity_learning import EntityLearning
from .relationships import (
    TaskPerson,
    TaskProject,
    TaskTopic,
    NotePerson,
    NoteProject,
    NoteTopic,
    TopicRelationship,
    TopicPerson,
    TopicProject,
)

__all__ = [
    "User",
    "SourceFile",
    "Note",
    "Person",
    "Project",
    "Topic",
    "Task",
    "SuggestedEntity",
    "EntityLearning",
    "TaskPerson",
    "TaskProject",
    "TaskTopic",
    "NotePerson",
    "NoteProject",
    "NoteTopic",
    "TopicRelationship",
    "TopicPerson",
    "TopicProject",
]