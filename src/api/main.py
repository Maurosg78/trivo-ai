#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicación principal de la API REST para TRIVO-AI.

Este módulo configura y ejecuta la aplicación FastAPI principal,
incorporando todos los diferentes endpoints y routers de la API.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar routers
from src.api.help_endpoints import router as help_router
from src.api.project_endpoints import router as project_router

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("trivo_api")

def create_app() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI.
    
    Returns:
        FastAPI: Aplicación FastAPI configurada
    """
    # Crear la aplicación FastAPI
    app = FastAPI(
        title="TRIVO-AI API",
        description="API para el sistema inteligente de apoyo a la creación de recetas de masas",
        version="1.0.0"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, esto debería ser más restrictivo
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Agregar routers
    app.include_router(help_router)
    app.include_router(project_router)
    
    # Ruta de salud
    @app.get("/health")
    async def health_check():
        """
        Endpoint para verificar el estado de la API.
        
        Returns:
            dict: Estado de la API
        """
        return {"status": "ok", "service": "TRIVO-AI API"}
    
    return app

# Aplicación para ejecución directa
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    # Obtener puerto de variables de entorno o usar valor por defecto
    port = int(os.getenv("API_PORT", "8000"))
    
    # Ejecutar servidor
    uvicorn.run(app, host="0.0.0.0", port=port) 