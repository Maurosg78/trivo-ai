"""
Modelo para registrar las ayudas proporcionadas por TRIVO-AI
"""
from sqlalchemy import Column, String, Text, ForeignKey, JSON, Enum, Integer
from sqlalchemy.orm import relationship
import enum
from src.database.models.base import BaseModel

class HelpType(enum.Enum):
    """Tipos de ayuda proporcionados por el sistema"""
    RECIPE_SUGGESTION = "recipe_suggestion"  # Sugerencias de recetas
    INVENTORY_MANAGEMENT = "inventory_management"  # Gestión de inventario
    COST_OPTIMIZATION = "cost_optimization"  # Optimización de costos
    SUPPLIER_RECOMMENDATION = "supplier_recommendation"  # Recomendación de proveedores
    PRODUCTION_PLANNING = "production_planning"  # Planificación de producción
    QUALITY_CONTROL = "quality_control"  # Control de calidad
    OTHER = "other"  # Otros tipos de ayuda

class HelpLog(BaseModel):
    """
    Modelo para registrar las ayudas proporcionadas por TRIVO-AI a los usuarios
    """
    # Relación con el usuario que recibió la ayuda
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    user = relationship("User", backref="help_logs")
    
    # Tipo de ayuda proporcionada
    help_type = Column(Enum(HelpType), nullable=False)
    
    # Detalles de la consulta y la respuesta
    query = Column(Text, nullable=False)  # Consulta realizada por el usuario
    response = Column(Text, nullable=False)  # Respuesta proporcionada por TRIVO-AI
    
    # Metadata adicional
    context_data = Column(JSON, nullable=True)  # Datos de contexto en formato JSON (ej. recetas relacionadas, ingredientes)
    feedback = Column(Text, nullable=True)  # Retroalimentación opcional del usuario
    usefulness_rating = Column(Integer, nullable=True)  # Calificación opcional de utilidad (1-5)
    
    # Si la ayuda está relacionada con una receta específica
    recipe_id = Column(String(36), ForeignKey('recipe.id'), nullable=True)
    recipe = relationship("Recipe", backref="help_logs")
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de HelpLog a partir de un diccionario
        """
        help_log = cls(
            user_id=data.get("user_id"),
            help_type=data.get("help_type"),
            query=data.get("query"),
            response=data.get("response"),
            context_data=data.get("context_data"),
            feedback=data.get("feedback"),
            usefulness_rating=data.get("usefulness_rating"),
            recipe_id=data.get("recipe_id")
        )
        
        # Si hay un ID específico, usarlo
        if "id" in data:
            help_log.id = data["id"]
            
        return help_log
    
    def to_dict(self):
        """
        Convierte el registro de ayuda a un diccionario
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "help_type": self.help_type.value if self.help_type else None,
            "query": self.query,
            "response": self.response,
            "context_data": self.context_data,
            "feedback": self.feedback,
            "usefulness_rating": self.usefulness_rating,
            "recipe_id": self.recipe_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 