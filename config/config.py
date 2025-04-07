from pydantic_settings import BaseSettings
from typing import Dict, List

class Settings(BaseSettings):
    # Configuración de la base de datos
    DATABASE_URL: str = "sqlite:///./vegan_dough.db"
    
    # Configuración de la API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Vegan Dough AI"
    
    # Configuración de ingredientes
    INGREDIENT_CATEGORIES: List[str] = [
        "vegetables",
        "legumes",
        "grains",
        "nuts",
        "seeds"
    ]
    
    # Propiedades nutricionales objetivo
    TARGET_NUTRITIONAL_PROPERTIES: Dict[str, float] = {
        "protein": 15.0,  # gramos por 100g
        "fiber": 8.0,     # gramos por 100g
        "fat": 5.0,       # gramos por 100g
        "carbohydrates": 30.0  # gramos por 100g
    }
    
    # Propiedades de textura objetivo
    TARGET_TEXTURE_PROPERTIES: Dict[str, float] = {
        "elasticity": 0.7,
        "firmness": 0.6,
        "moisture": 0.5
    }
    
    # Configuración de producción
    PRODUCTION_SCALE: str = "small"  # small, medium, large
    EQUIPMENT_REQUIREMENTS: List[str] = [
        "mixer",
        "kneader",
        "proofer",
        "baker"
    ]
    
    # Configuración de logística
    STORAGE_TEMPERATURE: float = -18.0  # Celsius
    SHELF_LIFE_DAYS: int = 30
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 