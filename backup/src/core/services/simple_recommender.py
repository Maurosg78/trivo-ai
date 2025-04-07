import logging
import time
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class SimpleRecommender:
    """Servicio simple de recomendaciones que usa directamente la API de USDA."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        self.session = requests.Session()
        self.session.headers.update({"X-Api-Key": self.api_key, "Content-Type": "application/json"})
        self._cache = {}  # Cache simple en memoria

    def search_foods(self, query: str, page_size: int = 5) -> List[Dict]:
        """Busca alimentos en la base de datos de USDA."""
        cache_key = f"search:{query}:{page_size}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        try:
            logger.info(f"Buscando alimentos para: {query}")
            
            response = requests.get(
                f"{self.base_url}/foods/search",
                params={
                    "query": query,
                    "pageSize": page_size,
                    "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"],
                },
                headers={"X-Api-Key": self.api_key}
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("foods", [])
                self._cache[cache_key] = result
                return result
                
        except Exception as e:
            logger.error(f"Error al buscar alimentos: {str(e)}")
            
        return []

    def get_food_details(self, fdc_id: str) -> Optional[Dict]:
        """Obtiene detalles de un alimento específico."""
        cache_key = f"food:{fdc_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        try:
            logger.info(f"Obteniendo detalles para alimento ID: {fdc_id}")
            
            response = requests.get(
                f"{self.base_url}/food/{fdc_id}",
                headers={"X-Api-Key": self.api_key}
            )
            
            if response.status_code == 200:
                data = response.json()
                self._cache[cache_key] = data
                return data
                
        except Exception as e:
            logger.error(f"Error al obtener detalles del alimento {fdc_id}: {str(e)}")
            
        return None

    def get_recommendations(self, base_ingredient: str, limit: int = 3) -> List[Dict]:
        """Genera recomendaciones de ingredientes similares."""
        try:
            logger.info(f"Generando recomendaciones para: {base_ingredient}")
            
            # Buscar ingredientes similares
            foods = self.search_foods(base_ingredient, page_size=limit + 2)
            
            if len(foods) <= 1:
                return []
                
            # El primer elemento es el ingrediente base, lo omitimos
            recommendations = []
            
            for food in foods[1:limit+1]:
                details = self.get_food_details(food["fdcId"])
                if details:
                    recommendations.append({
                        "description": food["description"],
                        "fdcId": food["fdcId"],
                        "score": self._calculate_score(details),
                        "nutrients": self._extract_nutrients(details)
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error al generar recomendaciones: {str(e)}")
            return []
            
    def _calculate_score(self, food_details: Dict) -> float:
        """Calcula un puntaje para el alimento basado en sus nutrientes."""
        score = 5.0  # Puntaje base
        nutrients = food_details.get("foodNutrients", [])
        
        # Por simplicidad, solo sumamos 0.1 por cada nutriente presente
        return score + (len(nutrients) * 0.1)
        
    def _extract_nutrients(self, food_details: Dict) -> Dict:
        """Extrae los nutrientes principales de los detalles del alimento."""
        nutrients = {}
        
        for nutrient in food_details.get("foodNutrients", []):
            name = nutrient.get("nutrientName", "")
            if name:
                nutrients[name] = nutrient.get("value", 0)
                
        return nutrients
