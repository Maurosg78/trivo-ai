"""
Módulo para interactuar con APIs externas de recetas y nutrición.
"""

from typing import Optional
import logging
import os
from .spoonacular_api import SpoonacularClient
from .recipe_cache import RecipeCache

# Configurar logger
logger = logging.getLogger(__name__)

# Variables globales para los clientes
_spoonacular_client = None
_recipe_cache = None

def get_spoonacular_client() -> SpoonacularClient:
    """
    Retorna una instancia del cliente Spoonacular, utilizando caché inteligente.
    
    Returns:
        Instancia inicializada de SpoonacularClient
    """
    global _spoonacular_client, _recipe_cache
    
    if _spoonacular_client is None:
        # Inicializar el caché primero
        cache = get_recipe_cache()
        
        # Obtener API key
        api_key = os.environ.get('SPOONACULAR_API_KEY', '')
        
        if not api_key:
            logger.warning(
                "No se encontró la variable de entorno SPOONACULAR_API_KEY. "
                "Se utilizará el modo sin API."
            )
        
        # Crear cliente con caché
        _spoonacular_client = SpoonacularClient(api_key=api_key, recipe_cache=cache)
        logger.info("Cliente Spoonacular inicializado con caché inteligente")
    
    return _spoonacular_client

def get_recipe_cache() -> RecipeCache:
    """
    Retorna una instancia del caché de recetas.
    
    Returns:
        Instancia inicializada de RecipeCache
    """
    global _recipe_cache
    
    if _recipe_cache is None:
        # Directorio personalizado para caché
        cache_dir = os.environ.get('RECIPE_CACHE_DIR', 'cache/recipes')
        
        # Crear directorio si no existe
        os.makedirs(cache_dir, exist_ok=True)
        
        # Inicializar caché
        _recipe_cache = RecipeCache(cache_dir=cache_dir)
        
        # Mostrar estadísticas del caché existente
        stats = _recipe_cache.get_stats()
        logger.info(f"Caché de recetas inicializado en {cache_dir}")
        logger.info(f"Recetas en caché: {stats['total_recipes']}")
        
        if stats['total_recipes'] > 0:
            tipo_msg = ', '.join([f"{tipo}: {cantidad}" for tipo, cantidad in stats['recipe_types'].items()])
            logger.info(f"Tipos de recetas: {tipo_msg}")
    
    return _recipe_cache

__all__ = ['SpoonacularClient', 'RecipeCache', 'get_spoonacular_client', 'get_recipe_cache'] 