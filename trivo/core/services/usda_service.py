from typing import Dict, List, Optional

from pydantic import BaseModel
from src.core.cache.redis_cache import RedisCache
from src.core.services.usda_client import USDAClient


class NutrientInfo(BaseModel):
    """Información sobre un nutriente."""
    name: str
    amount: float
    unit: str


class FoodItem(BaseModel):
    """Modelo para un alimento de la API de USDA."""
    fdcId: str
    description: str
    nutrients: List[NutrientInfo] = []


class USDAService:
    """Servicio para interactuar con la API de USDA."""

    def __init__(self, api_key: str = None, cache: RedisCache = None):
        """Inicializa el servicio USDA."""
        self.client = USDAClient(api_key)
        self.cache = cache

    def search_foods(self, query: str, page_size: int = 5) -> List[Dict]:
        """Busca alimentos en la base de datos USDA."""
        if self.cache:
            cache_key = f"search:{query}:{page_size}"
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result

        result = self.client.search_foods(query, page_size)
        if "foods" in result:
            result = result["foods"]

        if self.cache:
            self.cache.set(cache_key, result, expire=3600)  # Cache por 1 hora

        return result

    def get_food_details(self, food_id: str) -> Dict:
        """Obtiene detalles de un alimento específico."""
        if self.cache:
            cache_key = f"food:{food_id}"
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result

        result = self.client.get_food_details(food_id)

        if self.cache:
            self.cache.set(cache_key, result, expire=86400)  # Cache por 24 horas

        return result

    def get_food_nutrition(self, food_name: str) -> Dict:
        """Obtiene información nutricional de un alimento por nombre."""
        foods = self.search_foods(food_name, page_size=1)
        if not foods:
            return {}

        food_id = foods[0]["fdcId"]
        return self.get_food_details(food_id)
