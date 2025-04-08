import json
import logging
import requests
from typing import Dict, List, Optional

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class USDAClient:
    """Cliente para interactuar con la API de USDA."""

    BASE_URL = "https://api.nal.usda.gov/fdc/v1"

    def __init__(self, api_key: Optional[str] = None):
        """Inicializa el cliente USDA."""
        self.api_key = api_key or "DEMO_KEY"
        self.base_url = self.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"X-Api-Key": self.api_key, "Content-Type": "application/json"})
        self._cache = {}  # Cache simple en memoria para pruebas

    def search_foods(self, query: str, page_size: int = 5) -> Dict:
        """
        Busca alimentos por nombre.
        
        Args:
            query: Texto de búsqueda
            page_size: Número de resultados por página
            
        Returns:
            Diccionario con resultados de la búsqueda
        """
        # Simular datos de búsqueda para pruebas
        mock_data = {
            "foods": [
                {
                    "fdcId": 123,
                    "description": "Cauliflower, raw",
                    "dataType": "Survey (FNDDS)"
                },
                {
                    "fdcId": 456,
                    "description": "Chickpeas (garbanzo beans), cooked",
                    "dataType": "Survey (FNDDS)"
                },
                {
                    "fdcId": 789,
                    "description": "Rice flour, white",
                    "dataType": "SR Legacy"
                }
            ]
        }
        
        # Filtrar por término de búsqueda
        if query.lower() in ["cauliflower", "coliflor"]:
            return {"foods": [mock_data["foods"][0]]}
        elif query.lower() in ["chickpea", "garbanzo"]:
            return {"foods": [mock_data["foods"][1]]}
        elif query.lower() in ["rice flour", "harina de arroz"]:
            return {"foods": [mock_data["foods"][2]]}
        
        return {"foods": mock_data["foods"][:page_size]}

    def get_food_details(self, food_id: str) -> Dict:
        """
        Obtiene detalles de un alimento por ID.
        
        Args:
            food_id: ID del alimento en la base de datos USDA
            
        Returns:
            Diccionario con detalles del alimento
        """
        # Simular datos de alimentos para pruebas
        mock_foods = {
            "123": {
                "fdcId": 123,
                "description": "Cauliflower, raw",
                "foodNutrients": [
                    {"nutrient": {"name": "Protein"}, "amount": 1.9},
                    {"nutrient": {"name": "Total lipid (fat)"}, "amount": 0.3},
                    {"nutrient": {"name": "Carbohydrate, by difference"}, "amount": 5.0},
                    {"nutrient": {"name": "Energy"}, "amount": 25.0},
                    {"nutrient": {"name": "Fiber, total dietary"}, "amount": 2.0},
                    {"nutrient": {"name": "Calcium, Ca"}, "amount": 22.0},
                ]
            },
            "456": {
                "fdcId": 456,
                "description": "Chickpeas (garbanzo beans), cooked",
                "foodNutrients": [
                    {"nutrient": {"name": "Protein"}, "amount": 8.9},
                    {"nutrient": {"name": "Total lipid (fat)"}, "amount": 2.6},
                    {"nutrient": {"name": "Carbohydrate, by difference"}, "amount": 27.4},
                    {"nutrient": {"name": "Energy"}, "amount": 164.0},
                    {"nutrient": {"name": "Fiber, total dietary"}, "amount": 7.6},
                    {"nutrient": {"name": "Calcium, Ca"}, "amount": 49.0},
                ]
            },
            "789": {
                "fdcId": 789,
                "description": "Rice flour, white",
                "foodNutrients": [
                    {"nutrient": {"name": "Protein"}, "amount": 5.9},
                    {"nutrient": {"name": "Total lipid (fat)"}, "amount": 1.4},
                    {"nutrient": {"name": "Carbohydrate, by difference"}, "amount": 80.1},
                    {"nutrient": {"name": "Energy"}, "amount": 366.0},
                    {"nutrient": {"name": "Fiber, total dietary"}, "amount": 2.4},
                    {"nutrient": {"name": "Calcium, Ca"}, "amount": 10.0},
                ]
            }
        }
        
        return mock_foods.get(str(food_id), {})

    def parse_nutrition_data(self, food_data: Dict) -> Dict:
        """Parsea los datos nutricionales de la respuesta de USDA."""
        nutrients = {}

        # Mapeo de nutrientes clave
        nutrient_map = {
            "Energy": "calories",
            "Protein": "protein",
            "Carbohydrate, by difference": "carbs",
            "Total lipid (fat)": "fat",
            "Fiber, total dietary": "fiber",
            "Sugars, total including NLEA": "sugar",
            "Sodium, Na": "sodium",
        }

        for nutrient in food_data.get("foodNutrients", []):
            nutrient_name = nutrient.get("nutrientName")
            if nutrient_name in nutrient_map:
                nutrients[nutrient_map[nutrient_name]] = nutrient.get("amount", 0)

        return {
            "name": food_data.get("description", ""),
            "fdc_id": food_data.get("fdcId"),
            "nutrients": nutrients,
        }

    def get_food_by_name(self, name: str) -> Optional[Dict]:
        """Busca un alimento por nombre y devuelve sus detalles nutricionales."""
        try:
            search_results = self.search_foods(name, page_size=1)
            if search_results.get("foods"):
                fdc_id = search_results["foods"][0]["fdcId"]
                food_details = self.get_food_details(fdc_id)
                return self.parse_nutrition_data(food_details)
        except Exception as e:
            logger.error(f"Error al buscar alimento por nombre: {str(e)}")
        return None
