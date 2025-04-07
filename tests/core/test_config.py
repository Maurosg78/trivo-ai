import os
from unittest.mock import patch

import pytest
from pydantic import PostgresDsn

from src.core.config import Settings, get_settings


def test_get_settings_singleton():
    """Prueba que get_settings devuelva siempre la misma instancia."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


@patch.dict(os.environ, {
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_HOST": "test_host",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "test_db"
})
def test_database_url_validation():
    """Prueba la validación y construcción del DATABASE_URL."""
    settings = Settings()
    
    assert isinstance(settings.DATABASE_URL, str)
    assert "postgresql://" in settings.DATABASE_URL
    assert "test_user" in settings.DATABASE_URL
    assert "test_password" in settings.DATABASE_URL
    assert "test_host" in settings.DATABASE_URL
    assert "5432" in settings.DATABASE_URL
    assert "test_db" in settings.DATABASE_URL


@patch.dict(os.environ, {
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_DB": "0"
})
def test_redis_configuration():
    """Prueba la configuración de Redis."""
    settings = Settings()
    
    assert settings.REDIS_HOST == "localhost"
    assert settings.REDIS_PORT == 6379
    assert settings.REDIS_DB == 0


@patch.dict(os.environ, {"USDA_API_KEY": "test_api_key"})
def test_usda_api_configuration():
    """Prueba la configuración de la API USDA."""
    settings = Settings()
    
    assert settings.USDA_API_KEY == "test_api_key"
    assert "api.nal.usda.gov" in settings.USDA_API_BASE_URL 