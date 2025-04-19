"""
Modelo para recetas de masas
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from src.database.models.base import BaseModel

class Recipe(BaseModel):
    """
    Modelo para recetas de masas
    """
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)
    version = Column(String(10), default="1.0")
    is_public = Column(Boolean, default=False)
    
    # Propiedades específicas
    dough_hydration = Column(Float, nullable=True)
    dough_weight = Column(Integer, nullable=True)  # en gramos
    dough_temp = Column(Float, nullable=True)
    cooking_temp = Column(Integer, nullable=True)
    
    # Tiempos de proceso (en minutos)
    preparation_time = Column(Integer, nullable=True)
    fermentation_time = Column(Integer, nullable=True)
    cooking_time = Column(Integer, nullable=True)
    
    # Metadatos
    tags = Column(JSON, nullable=True)  # JSON array de etiquetas
    notes = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)  # Fuente o autor original
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones con otros modelos
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    steps = relationship("RecipeStep", back_populates="recipe", order_by="RecipeStep.order", cascade="all, delete-orphan")
    sheets = relationship("RecipeSheet", back_populates="recipe", cascade="all, delete-orphan")
    
    # Relación con proyectos
    projects = relationship("Project", secondary="project_recipes", back_populates="recipes")
    
    # Constructor para facilitar la creación desde diccionarios
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Recipe a partir de un diccionario
        """
        recipe = cls(
            name=data.get("nombre", "Sin nombre"),
            description=data.get("descripcion", ""),
            category=data.get("category", "pizza"),
            version=data.get("version", "1.0"),
            dough_hydration=data.get("dough_hydration"),
            dough_weight=data.get("dough_weight"),
            dough_temp=data.get("dough_temp"),
            cooking_temp=data.get("cooking_temp"),
            preparation_time=data.get("preparation_time"),
            fermentation_time=data.get("fermentation_time"),
            cooking_time=data.get("cooking_time"),
            tags=data.get("tags", []),
            notes=data.get("notes", ""),
            source=data.get("source", ""),
            is_public=data.get("is_public", False)
        )
        
        # Si hay un ID específico, usarlo
        if "id" in data:
            recipe.id = data["id"]
            
        return recipe
    
    def to_dict(self):
        """
        Convierte la receta a un diccionario
        """
        return {
            "id": self.id,
            "nombre": self.name,
            "descripcion": self.description,
            "category": self.category,
            "version": self.version,
            "is_public": self.is_public,
            "dough_hydration": self.dough_hydration,
            "dough_weight": self.dough_weight,
            "dough_temp": self.dough_temp,
            "cooking_temp": self.cooking_temp,
            "preparation_time": self.preparation_time,
            "fermentation_time": self.fermentation_time,
            "cooking_time": self.cooking_time,
            "tags": self.tags,
            "notes": self.notes,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "project_count": len(self.projects) if self.projects else 0
        }

class RecipeIngredient(BaseModel):
    """
    Modelo para ingredientes en una receta
    Tabla de relación entre recetas e ingredientes
    """
    __tablename__ = 'recipe_ingredients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    order = Column(Integer, default=0)  # Orden en la lista de ingredientes
    
    # Opcional: campos específicos para esta relación
    notes = Column(Text, nullable=True)
    is_optional = Column(Boolean, default=False)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipes")

class RecipeStep(BaseModel):
    """
    Pasos de preparación para una receta
    """
    __tablename__ = 'recipe_steps'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    order = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    time = Column(Integer, nullable=True)  # tiempo en minutos para este paso
    temperature = Column(Float, nullable=True)  # temperatura para este paso, si aplica
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    recipe = relationship("Recipe", back_populates="steps") 