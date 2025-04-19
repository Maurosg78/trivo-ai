"""
Módulo de base de datos para TRIVO-AI
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trivo_ai.db")

# Crear motor de base de datos
engine = create_engine(
    DATABASE_URL, 
    echo=False,  # Cambiar a True para debugging
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

# Base para los modelos declarativos
Base = declarative_base()
Base.query = db_session.query_property()

def get_db():
    """
    Función para obtener una sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Inicializar la base de datos creando todas las tablas
    """
    # Importar todos los modelos para que Base los conozca
    print("Creando tablas en la base de datos...")
    
    # Importamos aquí para evitar problemas de importación circular
    import src.database.models.recipe
    import src.database.models.ingredient
    import src.database.models.supplier
    import src.database.models.user
    import src.database.models.recipe_sheet
    
    print(f"Motor de base de datos: {engine}")
    print(f"URL de la base de datos: {DATABASE_URL}")
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente!") 