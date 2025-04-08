from typing import List, Optional, Union, Dict, Any
import os
from dotenv import load_dotenv

from pydantic import Field, SecretStr, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Configuración de la base de datos
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    
    # URL de conexión a la base de datos
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/trivoai",
        env="DATABASE_URL"
    )
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, any]) -> any:
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_HOST')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
    
    # Configuración de la aplicación
    APP_NAME: str = "TRIVO-AI"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Configuración de seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configuración de CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["*"])

    # Configuración de logging
    LOG_LEVEL: str = "INFO"

    # Configuración de la API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Configuración de caché
    CACHE_TTL: int = 3600  # 1 hora en segundos

    # Configuración de límites de API
    API_RATE_LIMIT: int = 100  # peticiones por minuto

    # Configuración de archivos
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    # Configuración de email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None

    # Configuración de monitoreo
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # Configuración de APIs externas
    USDA_API_KEY: Optional[str] = Field(default=None, env="USDA_API_KEY")
    USDA_API_URL: str = "https://api.nal.usda.gov/fdc/v1"

    # Configuración de GitHub
    GITHUB_TOKEN: Optional[str] = Field(default=None, env="GITHUB_TOKEN")

    # Configuración de Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_default=True,
        extra="allow",  # Permitir campos adicionales
    )

    @classmethod
    def parse_env_var(
        cls, field_name: str, raw_val: str
    ) -> Optional[Union[str, int, bool, SecretStr]]:
        """Parsea variables de entorno personalizadas"""
        if raw_val.lower() in ("null", "", "none"):
            return None
        return raw_val


# Crear una instancia global de la configuración
@lru_cache()
def get_settings() -> Settings:
    return Settings()


class Config:
    def __init__(self):
        load_dotenv()
        self._config = {
            "database": {
                "url": os.getenv("DATABASE_URL", "sqlite:///pizzaai.db")
            },
            "api": {
                "spoonacular_key": os.getenv("SPOONACULAR_API_KEY", ""),
                "openai_key": os.getenv("OPENAI_API_KEY", "")
            },
            "validation": {
                "strict_mode": os.getenv("VALIDATION_STRICT_MODE", "true").lower() == "true"
            },
            "optimization": {
                "max_iterations": int(os.getenv("OPTIMIZATION_MAX_ITERATIONS", "100")),
                "population_size": int(os.getenv("OPTIMIZATION_POPULATION_SIZE", "50"))
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración por su clave."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Establece un valor de configuración."""
        keys = key.split(".")
        current = self._config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    def to_dict(self) -> Dict[str, Any]:
        """Devuelve la configuración como un diccionario."""
        return self._config.copy()

config = Config()
