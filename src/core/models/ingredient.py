from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.core.models.base import Base

class Ingredient(Base):
    """Modelo de ingrediente para el sistema."""
    
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    category = Column(String, index=True)
    usda_id = Column(String, unique=True, index=True)  # ID de la base de datos USDA
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)
    carbs_per_100g = Column(Float)
    fat_per_100g = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient")
    
    def __repr__(self):
        return f"<Ingredient {self.name}>"
    
    @property
    def nutritional_info(self) -> dict:
        """Retorna la información nutricional del ingrediente."""
        return {
            "calories": self.calories_per_100g,
            "protein": self.protein_per_100g,
            "carbs": self.carbs_per_100g,
            "fat": self.fat_per_100g
        }
