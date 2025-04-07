from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.core.models.base import Base

class Recipe(Base):
    """Modelo de receta para el sistema."""
    
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    instructions = Column(Text, nullable=False)
    preparation_time = Column(Integer)  # en minutos
    cooking_time = Column(Integer)  # en minutos
    servings = Column(Integer)
    difficulty = Column(String)  # fácil, medio, difícil
    image_url = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    author = relationship("User", back_populates="recipes")
    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    ratings = relationship("RecipeRating", back_populates="recipe")
    
    def __repr__(self):
        return f"<Recipe {self.name}>"
    
    @property
    def total_time(self) -> int:
        """Retorna el tiempo total de preparación en minutos."""
        return (self.preparation_time or 0) + (self.cooking_time or 0)
    
    @property
    def average_rating(self) -> Optional[float]:
        """Calcula el rating promedio de la receta."""
        if not self.ratings:
            return None
        return sum(rating.score for rating in self.ratings) / len(self.ratings)
    
    @property
    def nutritional_info(self) -> dict:
        """Calcula la información nutricional total de la receta."""
        total = {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0
        }
        
        for recipe_ingredient in self.ingredients:
            ingredient = recipe_ingredient.ingredient
            amount = recipe_ingredient.amount / 100  # Convertir a gramos
            
            total["calories"] += ingredient.calories_per_100g * amount
            total["protein"] += ingredient.protein_per_100g * amount
            total["carbs"] += ingredient.carbs_per_100g * amount
            total["fat"] += ingredient.fat_per_100g * amount
            
        return total
