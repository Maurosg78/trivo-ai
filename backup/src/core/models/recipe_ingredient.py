from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.core.models.base import Base


class RecipeIngredient(Base):
    """Modelo de relación entre recetas e ingredientes."""

    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    amount = Column(Float, nullable=False)  # cantidad en gramos
    unit = Column(String, nullable=False)  # unidad de medida
    notes = Column(String)  # notas adicionales (opcional)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

    def __repr__(self):
        return f"<RecipeIngredient {self.ingredient.name} in {self.recipe.name}>"
