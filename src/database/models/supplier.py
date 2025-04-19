"""
Modelo para proveedores
"""
from sqlalchemy import Column, String, Boolean, Integer, Text, JSON
from sqlalchemy.orm import relationship
from src.database.models.base import BaseModel

class Supplier(BaseModel):
    """
    Modelo para proveedores de ingredientes
    """
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    contact_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    
    # Metadatos
    supplier_type = Column(String(50), nullable=True)  # Tipo de proveedor (local, nacional, internacional)
    payment_terms = Column(String(255), nullable=True)
    delivery_time = Column(Integer, nullable=True)  # Tiempo de entrega promedio en días
    minimum_order = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    rating = Column(Integer, nullable=True)  # Calificación 1-5
    tags = Column(JSON, nullable=True)  # JSON array de etiquetas
    
    # Relaciones
    ingredient_prices = relationship("IngredientPrice", back_populates="supplier")
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Supplier a partir de un diccionario
        """
        supplier = cls(
            name=data.get("name", "Sin nombre"),
            description=data.get("description", ""),
            contact_name=data.get("contact_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            supplier_type=data.get("supplier_type"),
            payment_terms=data.get("payment_terms"),
            delivery_time=data.get("delivery_time"),
            minimum_order=data.get("minimum_order"),
            notes=data.get("notes"),
            is_active=data.get("is_active", True),
            rating=data.get("rating"),
            tags=data.get("tags", []),
        )
        
        # Si hay un ID específico, usarlo
        if "id" in data:
            supplier.id = data["id"]
            
        return supplier
    
    def to_dict(self):
        """
        Convierte el proveedor a un diccionario
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "supplier_type": self.supplier_type,
            "payment_terms": self.payment_terms,
            "delivery_time": self.delivery_time,
            "minimum_order": self.minimum_order,
            "notes": self.notes,
            "is_active": self.is_active,
            "rating": self.rating,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 