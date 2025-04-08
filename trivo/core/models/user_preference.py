from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.core.models.base import Base

class UserPreference(Base):
    """Modelo de preferencias de usuario para el sistema."""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    dietary_restrictions = Column(JSON, default=list)  # lista de restricciones dietéticas
    favorite_cuisines = Column(JSON, default=list)  # lista de cocinas favoritas
    disliked_ingredients = Column(JSON, default=list)  # lista de ingredientes que no le gustan
    allergies = Column(JSON, default=list)  # lista de alergias
    preferred_cooking_time = Column(Integer)  # tiempo máximo de cocción en minutos
    skill_level = Column(String)  # principiante, intermedio, avanzado
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreference for user {self.user_id}>"
    
    @property
    def has_dietary_restrictions(self) -> bool:
        """Verifica si el usuario tiene restricciones dietéticas."""
        return bool(self.dietary_restrictions)
    
    @property
    def has_allergies(self) -> bool:
        """Verifica si el usuario tiene alergias."""
        return bool(self.allergies)
    
    def can_eat_ingredient(self, ingredient_name: str) -> bool:
        """Verifica si el usuario puede comer un ingrediente específico."""
        return (
            ingredient_name not in self.disliked_ingredients and
            not any(allergy in ingredient_name.lower() for allergy in self.allergies)
        ) 