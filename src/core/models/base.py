from datetime import datetime
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, Integer, DateTime

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # Generar __tablename__ automáticamente
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class BaseModelMixin:
    """Mixin con campos comunes para todos los modelos."""

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
