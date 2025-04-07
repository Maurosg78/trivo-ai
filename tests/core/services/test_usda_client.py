import json
import unittest
from unittest.mock import patch, Mock

import pytest
import requests

from src.core.services.usda_client import USDAClient


class TestUSDAClient(unittest.TestCase):
    """Pruebas para el cliente de la API USDA."""

    def setUp(self):
        """Configurar recursos para las pruebas."""
        self.api_key = "test_api_key"
        self.base_url = "https://api.example.com"
        
        # Crear el cliente con un patch para usar un base_url de prueba
        with patch("src.core.config.get_settings") as mock_settings:
            mock_settings.return_value.USDA_API_KEY = self.api_key
            mock_settings.return_value.USDA_API_BASE_URL = self.base_url
            self.client = USDAClient()
        
        # Asegurar que el cliente use la URL base de prueba
        self.client.base_url = self.base_url
        
    @patch("requests.Session.get")
    def test_search_foods_success(self, mock_get):
        """Prueba la búsqueda de alimentos con respuesta exitosa."""
        # Configurar mock para respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "foods": [
                {"fdcId": "123", "description": "Tomato"},
                {"fdcId": "456", "description": "Tomato sauce"}
            ],
            "totalHits": 2,
            "currentPage": 1,
            "totalPages": 1
        }
        mock_get.return_value = mock_response
        
        # Llamar al método
        result = self.client.search_foods("tomato", page_size=2)
        
        # Verificar llamada a la API
        mock_get.assert_called_once_with(
            f"{self.base_url}/foods/search",
            params={
                "query": "tomato",
                "pageSize": 2,
                "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"]
            }
        )
        
        # Verificar resultado
        self.assertEqual(result["foods"][0]["fdcId"], "123")
        self.assertEqual(result["foods"][1]["description"], "Tomato sauce")
        self.assertEqual(result["totalHits"], 2)

    @patch("requests.Session.get")
    def test_search_foods_from_cache(self, mock_get):
        """Prueba la búsqueda de alimentos con caché."""
        # Configurar datos de caché
        cache_key = "search:tomato:2"
        cached_result = {
            "foods": [
                {"fdcId": "123", "description": "Tomato"},
                {"fdcId": "456", "description": "Tomato sauce"}
            ]
        }
        self.client._cache[cache_key] = cached_result
        
        # Llamar al método
        result = self.client.search_foods("tomato", page_size=2)
        
        # Verificar que no se llamó a la API
        mock_get.assert_not_called()
        
        # Verificar resultado
        self.assertEqual(result, cached_result)

    @patch("requests.Session.get")
    def test_search_foods_error(self, mock_get):
        """Prueba la búsqueda de alimentos con error de conexión."""
        # Configurar mock para simular error
        mock_get.side_effect = requests.exceptions.RequestException("Error de conexión")
        
        # Llamar al método
        result = self.client.search_foods("tomato")
        
        # Verificar resultado
        self.assertEqual(result["foods"], [])
        self.assertEqual(result["totalHits"], 0)

    @patch("requests.Session.get")
    def test_get_food_details_success(self, mock_get):
        """Prueba la obtención de detalles de alimento con respuesta exitosa."""
        # Configurar mock para respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "fdcId": "123",
            "description": "Tomato",
            "foodNutrients": [
                {"nutrientName": "Protein", "value": 0.9},
                {"nutrientName": "Carbohydrate, by difference", "value": 3.9}
            ]
        }
        mock_get.return_value = mock_response
        
        # Llamar al método
        result = self.client.get_food_details("123")
        
        # Verificar llamada a la API
        mock_get.assert_called_once_with(f"{self.base_url}/food/123")
        
        # Verificar resultado
        self.assertEqual(result["fdcId"], "123")
        self.assertEqual(result["description"], "Tomato")
        self.assertEqual(len(result["foodNutrients"]), 2)

    @patch("requests.Session.get")
    def test_get_food_details_from_cache(self, mock_get):
        """Prueba la obtención de detalles de alimento con caché."""
        # Configurar datos de caché
        cache_key = "food:123"
        cached_result = {
            "fdcId": "123",
            "description": "Tomato",
            "foodNutrients": [
                {"nutrientName": "Protein", "value": 0.9}
            ]
        }
        self.client._cache[cache_key] = cached_result
        
        # Llamar al método
        result = self.client.get_food_details("123")
        
        # Verificar que no se llamó a la API
        mock_get.assert_not_called()
        
        # Verificar resultado
        self.assertEqual(result, cached_result)

    @patch("requests.Session.get")
    def test_get_food_details_error(self, mock_get):
        """Prueba la obtención de detalles de alimento con error de conexión."""
        # Configurar mock para simular error
        mock_get.side_effect = requests.exceptions.RequestException("Error de conexión")
        
        # Llamar al método
        result = self.client.get_food_details("123")
        
        # Verificar resultado
        self.assertEqual(result, {})

    def test_parse_nutrition_data(self):
        """Prueba el parseo de datos nutricionales."""
        # Datos de prueba
        food_data = {
            "fdcId": "123",
            "description": "Tomato",
            "foodNutrients": [
                {"nutrientName": "Energy", "value": 18},
                {"nutrientName": "Protein", "value": 0.9},
                {"nutrientName": "Carbohydrate, by difference", "value": 3.9},
                {"nutrientName": "Total lipid (fat)", "value": 0.2},
                {"nutrientName": "Fiber, total dietary", "value": 1.2},
                {"nutrientName": "Sugars, total including NLEA", "value": 2.6},
                {"nutrientName": "Sodium, Na", "value": 5},
                {"nutrientName": "Vitamin C", "value": 13.7}  # Nutriente no mapeado
            ]
        }
        
        # Llamar al método
        result = self.client.parse_nutrition_data(food_data)
        
        # Verificar resultado
        self.assertEqual(result["name"], "Tomato")
        self.assertEqual(result["fdc_id"], "123")
        self.assertEqual(result["nutrients"]["calories"], 18)
        self.assertEqual(result["nutrients"]["protein"], 0.9)
        self.assertEqual(result["nutrients"]["carbs"], 3.9)
        self.assertEqual(result["nutrients"]["fat"], 0.2)
        self.assertEqual(result["nutrients"]["fiber"], 1.2)
        self.assertEqual(result["nutrients"]["sugar"], 2.6)
        self.assertEqual(result["nutrients"]["sodium"], 5)
        self.assertNotIn("Vitamin C", result["nutrients"])

    @patch.object(USDAClient, "search_foods")
    @patch.object(USDAClient, "get_food_details")
    def test_get_food_by_name_success(self, mock_details, mock_search):
        """Prueba la obtención de alimento por nombre con éxito."""
        # Configurar mocks
        mock_search.return_value = {
            "foods": [{"fdcId": "123", "description": "Tomato"}]
        }
        mock_details.return_value = {
            "fdcId": "123",
            "description": "Tomato",
            "foodNutrients": [
                {"nutrientName": "Energy", "value": 18},
                {"nutrientName": "Protein", "value": 0.9}
            ]
        }
        
        # Llamar al método
        result = self.client.get_food_by_name("tomato")
        
        # Verificar llamadas a los métodos
        mock_search.assert_called_once_with("tomato", page_size=1)
        mock_details.assert_called_once_with("123")
        
        # Verificar resultado
        self.assertEqual(result["name"], "Tomato")
        self.assertEqual(result["fdc_id"], "123")
        self.assertIn("nutrients", result)
        self.assertIn("calories", result["nutrients"])

    @patch.object(USDAClient, "search_foods")
    def test_get_food_by_name_no_results(self, mock_search):
        """Prueba la obtención de alimento por nombre sin resultados."""
        # Configurar mock
        mock_search.return_value = {"foods": []}
        
        # Llamar al método
        result = self.client.get_food_by_name("no_existe")
        
        # Verificar resultado
        self.assertIsNone(result)

    @patch.object(USDAClient, "search_foods")
    def test_get_food_by_name_error(self, mock_search):
        """Prueba la obtención de alimento por nombre con error."""
        # Configurar mock para simular error
        mock_search.side_effect = Exception("Error inesperado")
        
        # Llamar al método
        result = self.client.get_food_by_name("tomato")
        
        # Verificar resultado
        self.assertIsNone(result) 