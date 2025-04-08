#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para la API de validación.
"""

import json
import sys
import os
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Añadir el directorio raíz al path para poder importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importar la API
from src.api.validation_api import register_validation_api

# Crear aplicación de prueba
app = FastAPI()
register_validation_api(app)
client = TestClient(app)

# Fixtures para las pruebas
@pytest.fixture
def sample_recipe():
    """Fixture que devuelve una receta de ejemplo."""
    return {
        "recipe_type": "pizza",
        "ingredients": {
            "harina": 500.0,
            "agua": 325.0,
            "sal": 10.0,
            "levadura": 5.0,
            "aceite_oliva": 15.0
        },
        "fermentation_time": 24.0,
        "fermentation_temp": 4.0,
        "sub_type": "napolitana"
    }

@pytest.fixture
def recipe_json_path(tmp_path):
    """Fixture que crea un archivo JSON temporal con una receta."""
    recipe = {
        "recipe_type": "pizza",
        "ingredients": {
            "harina": 500.0,
            "agua": 325.0,
            "sal": 10.0,
            "levadura": 5.0,
            "aceite_oliva": 15.0
        }
    }
    
    file_path = tmp_path / "recipe.json"
    with open(file_path, "w") as f:
        json.dump(recipe, f)
    
    return file_path

# Pruebas para los endpoints
def test_get_system_status():
    """Prueba para verificar el estado del sistema."""
    response = client.get("/api/v1/validation/status")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "OK"
    assert "rules_count" in data
    assert "rules_by_severity" in data
    assert "version" in data
    assert "last_check" in data

def test_get_rules():
    """Prueba para obtener la lista de reglas."""
    response = client.get("/api/v1/validation/rules")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verificar estructura de la primera regla
    rule = data[0]
    assert "code" in rule
    assert "description" in rule
    assert "severity" in rule

def test_get_rule_by_code():
    """Prueba para obtener información de una regla específica."""
    # Primero obtenemos todas las reglas para encontrar un código válido
    response = client.get("/api/v1/validation/rules")
    rules = response.json()
    rule_code = rules[0]["code"]
    
    # Ahora probamos obtener esa regla específica
    response = client.get(f"/api/v1/validation/rules/{rule_code}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == rule_code
    assert "description" in data
    assert "severity" in data

def test_get_rule_nonexistent():
    """Prueba para intentar obtener una regla que no existe."""
    response = client.get("/api/v1/validation/rules/NONEXISTENT_RULE")
    assert response.status_code == 404

def test_validate_recipe(sample_recipe):
    """Prueba para validar una receta."""
    response = client.post(
        "/api/v1/validation/validate",
        json=sample_recipe,
        params={"production_scale": "individual"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "is_viable" in data
    assert "validation_time" in data
    assert "total_rules_checked" in data
    assert "total_issues" in data
    assert "issues_by_severity" in data
    assert "recommendations" in data
    assert "details" in data
    
    # Verificar si hay detalles de validación
    assert isinstance(data["details"], list)

def test_validate_recipe_with_invalid_data():
    """Prueba para validar una receta con datos incorrectos."""
    # Receta sin los campos requeridos
    invalid_recipe = {
        "recipe_type": "pizza",
        # Falta el campo ingredients
    }
    
    response = client.post(
        "/api/v1/validation/validate",
        json=invalid_recipe,
        params={"production_scale": "individual"}
    )
    assert response.status_code == 422  # Error de validación Pydantic

def test_validate_recipe_file(recipe_json_path):
    """Prueba para validar una receta desde un archivo."""
    with open(recipe_json_path, "rb") as f:
        response = client.post(
            "/api/v1/validation/validate/file",
            files={"file": ("recipe.json", f, "application/json")},
            params={
                "recipe_type": "pizza",
                "production_scale": "individual"
            }
        )
    
    assert response.status_code == 200
    
    data = response.json()
    assert "is_viable" in data
    assert "validation_time" in data
    assert "total_rules_checked" in data
    assert "total_issues" in data
    assert "issues_by_severity" in data
    assert "recommendations" in data
    assert "details" in data

def test_validate_recipe_file_invalid_json(tmp_path):
    """Prueba para validar un archivo que no contiene JSON válido."""
    file_path = tmp_path / "invalid.json"
    with open(file_path, "w") as f:
        f.write("esto no es un JSON válido")
    
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/v1/validation/validate/file",
            files={"file": ("invalid.json", f, "application/json")},
            params={
                "recipe_type": "pizza",
                "production_scale": "individual"
            }
        )
    
    assert response.status_code == 400
    assert "JSON" in response.json()["detail"]

def test_production_scale_parameter(sample_recipe):
    """Prueba para verificar el funcionamiento del parámetro production_scale."""
    # Probar diferentes escalas de producción
    scales = ["individual", "small_business", "industrial"]
    
    for scale in scales:
        response = client.post(
            "/api/v1/validation/validate",
            json=sample_recipe,
            params={"production_scale": scale}
        )
        assert response.status_code == 200

def test_recipe_type_parameter(sample_recipe):
    """Prueba para verificar el funcionamiento del parámetro recipe_type."""
    # Modificar el tipo de receta
    recipe_types = ["pizza", "pan", "focaccia"]
    
    for recipe_type in recipe_types:
        recipe = sample_recipe.copy()
        recipe["recipe_type"] = recipe_type
        
        response = client.post(
            "/api/v1/validation/validate",
            json=recipe,
            params={"production_scale": "individual"}
        )
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 