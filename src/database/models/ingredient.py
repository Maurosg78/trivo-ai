"""
Modelo para ingredientes
"""
from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from src.database.models.base import BaseModel

class Ingredient(BaseModel):
    """
    Modelo para ingredientes
    """
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)
    
    # Propiedades nutricionales
    protein = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)
    
    # Propiedades específicas
    allergens = Column(JSON, nullable=True)  # JSON array de alérgenos
    origin = Column(String(100), nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    recipes = relationship("RecipeIngredient", back_populates="ingredient")
    prices = relationship("IngredientPrice", back_populates="ingredient", cascade="all, delete-orphan")
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Ingredient a partir de un diccionario
        """
        ingredient = cls(
            name=data.get("name", "Sin nombre"),
            description=data.get("description", ""),
            category=data.get("category", "other"),
            protein=data.get("protein"),
            fat=data.get("fat"),
            carbohydrates=data.get("carbohydrates"),
            fiber=data.get("fiber"),
            calories=data.get("calories"),
            allergens=data.get("allergens", []),
            origin=data.get("origin"),
            is_active=data.get("is_active", True),
        )
        
        # Si hay un ID específico, usarlo
        if "id" in data:
            ingredient.id = data["id"]
            
        return ingredient
    
    def to_dict(self):
        """
        Convierte el ingrediente a un diccionario
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "protein": self.protein,
            "fat": self.fat,
            "carbohydrates": self.carbohydrates,
            "fiber": self.fiber,
            "calories": self.calories,
            "allergens": self.allergens,
            "origin": self.origin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class IngredientPrice(BaseModel):
    """
    Modelo para precios de ingredientes
    Permite mantener un historial de precios
    """
    ingredient_id = Column(String(36), ForeignKey("ingredient.id"), nullable=False)
    supplier_id = Column(String(36), ForeignKey("supplier.id"), nullable=True)
    
    price = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="kg")
    currency = Column(String(3), nullable=False, default="USD")
    
    # Metadatos
    is_current = Column(Boolean, default=True)  # Indica si es el precio actual
    notes = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)  # Fuente del precio (manual, API, etc.)
    
    # Relaciones
    ingredient = relationship("Ingredient", back_populates="prices")
    supplier = relationship("Supplier", back_populates="ingredient_prices") 