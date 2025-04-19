"""
Modelo para fichas técnicas de recetas
"""
from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey, Text, JSON, Date
from sqlalchemy.orm import relationship
from src.database.models.base import BaseModel

class RecipeSheet(BaseModel):
    """
    Modelo para fichas técnicas industriales de recetas
    """
    recipe_id = Column(String(36), ForeignKey("recipe.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(10), default="1.0")
    revision_number = Column(Integer, default=1)
    status = Column(String(50), nullable=False, default="draft")  # draft, review, approved, archived
    
    # Información básica
    description = Column(Text, nullable=True)
    target_market = Column(String(255), nullable=True)
    certification = Column(JSON, nullable=True)  # Certificaciones (kosher, halal, etc.)
    serving_size = Column(String(100), nullable=True)
    yield_amount = Column(Float, nullable=True)
    yield_unit = Column(String(20), nullable=True, default="g")
    
    # Datos de vida útil
    shelf_life_ambient = Column(String(50), nullable=True)
    shelf_life_refrigerated = Column(String(50), nullable=True)
    shelf_life_frozen = Column(String(50), nullable=True)
    
    # Información industrial
    quality_parameters = Column(JSON, nullable=True)  # Parámetros de calidad en formato JSON
    critical_control_points = Column(JSON, nullable=True)  # Puntos críticos de control HACCP
    packaging_info = Column(JSON, nullable=True)  # Información de empaque
    storage_info = Column(JSON, nullable=True)  # Información de almacenamiento
    
    # Información nutricional
    nutrition = Column(JSON, nullable=True)  # Información nutricional
    allergens = Column(JSON, nullable=True)  # Información de alérgenos
    
    # Metadatos
    approved_by = Column(String(255), nullable=True)
    approval_date = Column(Date, nullable=True)
    author = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relaciones
    recipe = relationship("Recipe", back_populates="sheets")
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de RecipeSheet a partir de un diccionario
        """
        sheet = cls(
            recipe_id=data.get("recipe_id"),
            name=data.get("name", "Sin nombre"),
            version=data.get("version", "1.0"),
            revision_number=data.get("revision_number", 1),
            status=data.get("status", "draft"),
            description=data.get("description"),
            target_market=data.get("target_market"),
            certification=data.get("certification"),
            serving_size=data.get("serving_size"),
            yield_amount=data.get("yield_amount"),
            yield_unit=data.get("yield_unit", "g"),
            shelf_life_ambient=data.get("shelf_life_ambient"),
            shelf_life_refrigerated=data.get("shelf_life_refrigerated"),
            shelf_life_frozen=data.get("shelf_life_frozen"),
            quality_parameters=data.get("quality_parameters"),
            critical_control_points=data.get("critical_control_points"),
            packaging_info=data.get("packaging_info"),
            storage_info=data.get("storage_info"),
            nutrition=data.get("nutrition"),
            allergens=data.get("allergens"),
            approved_by=data.get("approved_by"),
            approval_date=data.get("approval_date"),
            author=data.get("author"),
            notes=data.get("notes"),
        )
        
        # Si hay un ID específico, usarlo
        if "id" in data:
            sheet.id = data["id"]
            
        return sheet
    
    def to_dict(self):
        """
        Convierte la ficha técnica a un diccionario
        """
        return {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "name": self.name,
            "version": self.version,
            "revision_number": self.revision_number,
            "status": self.status,
            "description": self.description,
            "target_market": self.target_market,
            "certification": self.certification,
            "serving_size": self.serving_size,
            "yield_amount": self.yield_amount,
            "yield_unit": self.yield_unit,
            "shelf_life_ambient": self.shelf_life_ambient,
            "shelf_life_refrigerated": self.shelf_life_refrigerated,
            "shelf_life_frozen": self.shelf_life_frozen,
            "quality_parameters": self.quality_parameters,
            "critical_control_points": self.critical_control_points,
            "packaging_info": self.packaging_info,
            "storage_info": self.storage_info,
            "nutrition": self.nutrition,
            "allergens": self.allergens,
            "approved_by": self.approved_by,
            "approval_date": self.approval_date.isoformat() if self.approval_date else None,
            "author": self.author,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 