"""
User service layer for business logic
"""
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models.user import User
from ..models.schemas import UserCreate, UserUpdate
from ..core.auth import get_password_hash, validate_password_strength


class UserService:
    """User service for CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        statement = select(User).where(User.id == user_id, User.is_deleted == False)
        return self.db.exec(statement).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        statement = select(User).where(User.email == email, User.is_deleted == False)
        return self.db.exec(statement).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Validate password strength
        if not validate_password_strength(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be at least 8 characters and contain uppercase, lowercase, digit, and special character"
            )
        
        # Check if email already exists
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            bio=user_data.bio,
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update fields if provided
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.bio is not None:
            user.bio = user_data.bio
        
        user.updated_at = datetime.utcnow()
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Soft delete user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_deleted = True
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        self.db.add(user)
        self.db.commit()
        return True