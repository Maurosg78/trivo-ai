from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from src.core.models.base import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    CHEF = "chef"

class User(Base):
    """Modelo de usuario para el sistema."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    recipes = relationship("Recipe", back_populates="author")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    @property
    def is_chef(self) -> bool:
        return self.role == UserRole.CHEF 