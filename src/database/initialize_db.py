"""
Script para inicializar la base de datos
"""
import sys
import os
import inspect

# Añadir el directorio raíz al path de Python
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = "sqlite:///./trivo_ai.db"  # Usar SQLite por defecto
print(f"Usando URL de base de datos: {DATABASE_URL}")

# Crear motor de base de datos
engine = create_engine(
    DATABASE_URL, 
    echo=True,  # Mostrar SQL generado
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Importar la base desde el modelo base
print("Importando modelos...")
from src.database.models.base import Base

# Importar modelos individualmente para que se registren con la Base
from src.database.models.user import User
from src.database.models.supplier import Supplier
from src.database.models.ingredient import Ingredient, IngredientPrice
from src.database.models.recipe import Recipe, RecipeIngredient, RecipeStep
from src.database.models.recipe_sheet import RecipeSheet

def init_db():
    """
    Inicializar la base de datos creando todas las tablas
    """
    print("Creando tablas en la base de datos...")
    
    # Verificar clases registradas en Base
    print(f"Clases registradas: {Base.metadata.tables.keys()}")
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente!")

if __name__ == "__main__":
    init_db() 