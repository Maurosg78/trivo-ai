"""
Modelo para usuarios
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from src.database.models.base import BaseModel

class User(BaseModel):
    """
    Modelo para usuarios del sistema
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)  # Almacena hash, no la contraseña
    
    # Información de perfil
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="user")  # user, admin, chef, etc.
    
    # Estado
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Preferencias y configuración
    preferences = Column(JSON, nullable=True)  # Preferencias del usuario en formato JSON
    settings = Column(JSON, nullable=True)  # Configuración del usuario en formato JSON
    
    # Relaciones con proyectos
    projects = relationship("Project", secondary="project_users", back_populates="users")
    created_projects = relationship("Project", back_populates="creator", foreign_keys="[Project.creator_id]")
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de User a partir de un diccionario
        """
        user = cls(
            username=data.get("username"),
            email=data.get("email"),
            password_hash=data.get("password_hash"),
            full_name=data.get("full_name"),
            role=data.get("role", "user"),
            is_active=data.get("is_active", True),
            is_verified=data.get("is_verified", False),
            preferences=data.get("preferences", {}),
            settings=data.get("settings", {}),
        )
        
        # Si hay un ID específico, usarlo
        if "id" in data:
            user.id = data["id"]
            
        return user
    
    def to_dict(self):
        """
        Convierte el usuario a un diccionario (sin datos sensibles)
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "project_count": len(self.projects) if self.projects else 0,
            "created_project_count": len(self.created_projects) if self.created_projects else 0
        } 