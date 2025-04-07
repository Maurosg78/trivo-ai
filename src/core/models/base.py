from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_optimized = Column(Boolean, default=False)
    optimization_score = Column(Float)
    
    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    validations = relationship("RecipeValidation", back_populates="recipe")

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    ingredient_name = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    
    recipe = relationship("Recipe", back_populates="ingredients")

class RecipeValidation(Base):
    __tablename__ = 'recipe_validations'
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    validation_type = Column(String(50), nullable=False)
    passed = Column(Boolean, default=False)
    message = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recipe = relationship("Recipe", back_populates="validations")
