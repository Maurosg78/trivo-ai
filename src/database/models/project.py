"""
Modelo de proyectos para TRIVO-AI.

Este módulo define el modelo de datos para los proyectos,
permitiendo agrupar recetas, usuarios y recursos.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, String, Integer, ForeignKey, Table, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.database.models.base import BaseModel

# Tabla de asociación para la relación muchos a muchos entre proyectos y usuarios
project_users = Table(
    'project_users',
    BaseModel.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

# Tabla de asociación para la relación muchos a muchos entre proyectos y recetas
project_recipes = Table(
    'project_recipes',
    BaseModel.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True)
)

class Project(BaseModel):
    """
    Modelo para representar un proyecto en el sistema.
    
    Un proyecto permite a los usuarios colaborar en un conjunto de recetas
    y compartir recursos comunes.
    """
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default='active')  # active, archived, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con el usuario creador
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    creator = relationship("User", back_populates="created_projects", foreign_keys=[creator_id])
    
    # Relaciones muchos a muchos
    users = relationship("User", secondary=project_users, back_populates="projects")
    recipes = relationship("Recipe", secondary=project_recipes, back_populates="projects")
    
    # Configuración y metadatos del proyecto
    config = Column(JSONB, default={})
    tags = Column(JSONB, default=[])
    
    # Para seguimiento de actividad
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el proyecto a un diccionario.
        
        Returns:
            Dict[str, Any]: Representación del proyecto como diccionario
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "creator_id": self.creator_id,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "is_public": self.is_public,
            "config": self.config,
            "tags": self.tags,
            "user_count": len(self.users) if self.users else 0,
            "recipe_count": len(self.recipes) if self.recipes else 0
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """
        Crea una instancia de proyecto a partir de un diccionario.
        
        Args:
            data: Datos del proyecto
            
        Returns:
            Project: Nueva instancia de proyecto
        """
        return cls(
            name=data.get('name'),
            description=data.get('description'),
            status=data.get('status', 'active'),
            creator_id=data.get('creator_id'),
            is_public=data.get('is_public', False),
            config=data.get('config', {}),
            tags=data.get('tags', [])
        ) 