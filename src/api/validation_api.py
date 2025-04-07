#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API REST para el sistema de validación de recetas.

Este módulo proporciona endpoints para validar recetas y acceder a las
reglas de validación disponibles.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, APIRouter, HTTPException, Body, Query, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Importar el motor de validación
from src.features.validation.validation_engine import ValidationEngine, check_system_integrity
from src.features.validation.validation_rules import get_validation_rules, get_rule_by_code

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("validation_api")

# Modelos de datos para la API
class Ingredient(BaseModel):
    """Modelo para representar un ingrediente y su cantidad."""
    name: str = Field(..., description="Nombre del ingrediente")
    amount: float = Field(..., description="Cantidad del ingrediente en gramos")

class Recipe(BaseModel):
    """Modelo para representar una receta."""
    recipe_type: str = Field(..., description="Tipo de receta (pizza, pan, etc.)")
    ingredients: Dict[str, float] = Field(..., description="Diccionario de ingredientes y cantidades")
    fermentation_time: Optional[float] = Field(None, description="Tiempo de fermentación en horas")
    fermentation_temp: Optional[float] = Field(None, description="Temperatura de fermentación en °C")
    sub_type: Optional[str] = Field(None, description="Subtipo de receta (napolitana, etc.)")

class ValidationResponse(BaseModel):
    """Modelo para respuestas de validación."""
    is_viable: bool = Field(..., description="Indica si la receta es viable")
    validation_time: str = Field(..., description="Fecha y hora de la validación")
    total_rules_checked: int = Field(..., description="Número total de reglas verificadas")
    total_issues: int = Field(..., description="Número total de problemas encontrados")
    issues_by_severity: Dict[str, int] = Field(..., description="Problemas agrupados por severidad")
    recommendations: List[str] = Field(..., description="Recomendaciones para mejorar la receta")
    details: List[Dict[str, Any]] = Field(..., description="Detalles de la validación por regla")

class RuleInfo(BaseModel):
    """Modelo para información de reglas de validación."""
    code: str = Field(..., description="Código único de la regla")
    description: str = Field(..., description="Descripción de la regla")
    severity: str = Field(..., description="Nivel de severidad (critical, medium, low)")

class SystemStatusResponse(BaseModel):
    """Modelo para respuestas de estado del sistema."""
    status: str = Field(..., description="Estado del sistema (OK, ERROR)")
    rules_count: int = Field(..., description="Número total de reglas disponibles")
    rules_by_severity: Dict[str, int] = Field(..., description="Reglas agrupadas por severidad")
    version: str = Field(..., description="Versión del sistema de validación")
    last_check: str = Field(..., description="Fecha y hora de la última verificación")

# Crear router para la API de validación
validation_router = APIRouter(
    prefix="/api/v1/validation",
    tags=["validación"],
    responses={
        404: {"description": "No encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)

# Inicializar motor de validación
engine = ValidationEngine()

@validation_router.post("/validate", response_model=ValidationResponse)
async def validate_recipe(
    recipe: Recipe = Body(..., description="Receta a validar"),
    production_scale: str = Query("individual", description="Escala de producción")
):
    """
    Valida una receta según reglas predefinidas.
    
    Args:
        recipe: Receta a validar
        production_scale: Escala de producción (individual, small_business, industrial)
        
    Returns:
        Resultados de la validación
    """
    try:
        # Preparar datos de la receta
        recipe_data = {**recipe.ingredients}
        
        # Añadir parámetros adicionales
        if recipe.fermentation_time is not None:
            recipe_data["tiempo_fermentacion"] = recipe.fermentation_time
        if recipe.fermentation_temp is not None:
            recipe_data["temperatura_fermentacion"] = recipe.fermentation_temp
        if recipe.sub_type:
            recipe_data[f"tipo_{recipe.sub_type}"] = True
        
        # Validar receta
        results = engine.validate_recipe(recipe_data, recipe.recipe_type, production_scale)
        
        # Generar resumen
        summary = engine.summarize_results(results)
        
        # Preparar respuesta
        response = {
            "is_viable": summary["is_viable"],
            "validation_time": datetime.now().isoformat(),
            "total_rules_checked": summary["total_rules_checked"],
            "total_issues": summary["total_issues"],
            "issues_by_severity": summary["issues_by_severity"],
            "recommendations": summary["recommendations"],
            "details": [r.to_dict() for r in results]
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Error al validar receta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al validar receta: {str(e)}"
        )

@validation_router.post("/validate/file", response_model=ValidationResponse)
async def validate_recipe_file(
    file: UploadFile = File(..., description="Archivo JSON con la receta"),
    recipe_type: Optional[str] = Query(None, description="Tipo de receta"),
    production_scale: str = Query("individual", description="Escala de producción")
):
    """
    Valida una receta desde un archivo JSON.
    
    Args:
        file: Archivo JSON con la receta
        recipe_type: Tipo de receta (opcional, se intentará leer del archivo)
        production_scale: Escala de producción
        
    Returns:
        Resultados de la validación
    """
    try:
        # Leer contenido del archivo
        contents = await file.read()
        recipe_data = json.loads(contents)
        
        # Determinar tipo de receta
        if recipe_type is None:
            recipe_type = recipe_data.get("recipe_type", "pizza")
        
        # Validar receta
        engine = ValidationEngine()
        
        # Extraer ingredientes si están en formato anidado
        if "ingredients" in recipe_data:
            ingredients = recipe_data["ingredients"]
        else:
            ingredients = recipe_data
        
        results = engine.validate_recipe(ingredients, recipe_type, production_scale)
        
        # Generar resumen
        summary = engine.summarize_results(results)
        
        # Preparar respuesta
        response = {
            "is_viable": summary["is_viable"],
            "validation_time": datetime.now().isoformat(),
            "total_rules_checked": summary["total_rules_checked"],
            "total_issues": summary["total_issues"],
            "issues_by_severity": summary["issues_by_severity"],
            "recommendations": summary["recommendations"],
            "details": [r.to_dict() for r in results]
        }
        
        return response
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="El archivo no contiene un JSON válido"
        )
    except Exception as e:
        logger.error(f"Error al validar receta desde archivo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al validar receta desde archivo: {str(e)}"
        )

@validation_router.get("/rules", response_model=List[RuleInfo])
async def get_rules():
    """
    Obtiene la lista de reglas de validación disponibles.
    
    Returns:
        Lista de reglas de validación
    """
    try:
        rules = get_validation_rules()
        
        # Preparar respuesta
        response = [
            {
                "code": rule.code,
                "description": rule.description,
                "severity": rule.severity
            }
            for rule in rules
        ]
        
        return response
    
    except Exception as e:
        logger.error(f"Error al obtener reglas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener reglas: {str(e)}"
        )

@validation_router.get("/rules/{rule_code}", response_model=RuleInfo)
async def get_rule(rule_code: str):
    """
    Obtiene información sobre una regla específica.
    
    Args:
        rule_code: Código de la regla
        
    Returns:
        Información de la regla
    """
    try:
        rule = get_rule_by_code(rule_code)
        
        if rule is None:
            raise HTTPException(
                status_code=404,
                detail=f"Regla no encontrada: {rule_code}"
            )
        
        # Preparar respuesta
        response = {
            "code": rule.code,
            "description": rule.description,
            "severity": rule.severity
        }
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener regla {rule_code}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener regla {rule_code}: {str(e)}"
        )

@validation_router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """
    Verifica el estado del sistema de validación.
    
    Returns:
        Estado del sistema
    """
    try:
        result = check_system_integrity()
        
        if result["status"] != "OK":
            return JSONResponse(
                status_code=503,
                content={
                    "status": "ERROR",
                    "error_message": result.get("error_message", "Error desconocido"),
                    "last_check": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            )
        
        # Preparar respuesta
        response = {
            "status": "OK",
            "rules_count": result["rules_count"],
            "rules_by_severity": result["rules_by_severity"],
            "version": "1.0.0",
            "last_check": datetime.now().isoformat()
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Error al verificar estado del sistema: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al verificar estado del sistema: {str(e)}"
        )

# Función para integrar el router en una aplicación FastAPI
def register_validation_api(app: FastAPI):
    """
    Registra la API de validación en una aplicación FastAPI.
    
    Args:
        app: Aplicación FastAPI
    """
    app.include_router(validation_router)

# Aplicación standalone para pruebas
if __name__ == "__main__":
    import uvicorn
    
    # Crear aplicación FastAPI
    app = FastAPI(
        title="TRIVO-AI Validation API",
        description="API para validación de recetas de masas",
        version="1.0.0"
    )
    
    # Registrar API de validación
    register_validation_api(app)
    
    # Ejecutar servidor
    uvicorn.run(app, host="0.0.0.0", port=8080) 