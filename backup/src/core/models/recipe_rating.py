from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.core.models.base import Base

class RecipeRating(Base):
    """Modelo de calificaciones de recetas."""
    
    __tablename__ = "recipe_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Float, nullable=False)  # puntuación de 1 a 5
    comment = Column(String)  # comentario opcional
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    recipe = relationship("Recipe", back_populates="ratings")
    user = relationship("User")
    
    def __repr__(self):
        return f"<RecipeRating {self.score} for recipe {self.recipe_id}>"
    
    @property
    def is_positive(self) -> bool:
        """Determina si la calificación es positiva (4 o 5 estrellas)."""
        return self.score >= 4.0 