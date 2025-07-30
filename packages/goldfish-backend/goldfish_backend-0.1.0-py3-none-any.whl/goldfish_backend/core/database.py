"""
Database connection and session management
"""
import os
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

# Import all models to ensure they're registered with SQLModel
from ..models import *  # noqa


class DatabaseConfig:
    """Database configuration"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./goldfish.db")
        self.test_database_url = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_goldfish.db")
        self.echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"


# Global database configuration
db_config = DatabaseConfig()

# Create engine
engine = create_engine(
    db_config.database_url,
    echo=db_config.echo,
    connect_args={"check_same_thread": False} if "sqlite" in db_config.database_url else {},
    poolclass=StaticPool if "sqlite" in db_config.database_url else None,
)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection"""
    with Session(engine) as session:
        yield session


# For testing
def create_test_engine():
    """Create test database engine"""
    return create_engine(
        db_config.test_database_url,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_test_session():
    """Create test database session"""
    test_engine = create_test_engine()
    SQLModel.metadata.create_all(test_engine)
    return Session(test_engine)