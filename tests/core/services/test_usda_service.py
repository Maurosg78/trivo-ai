import unittest
from unittest.mock import patch, MagicMock

from src.core.services.usda_service import USDAService


class TestUSDAService(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.service = USDAService(self.api_key)
        
    @patch('src.core.services.usda_client.USDAClient.search_foods')
    def test_search_foods(self, mock_search):
        """Prueba la búsqueda de alimentos en USDA."""
        mock_search.return_value = [{"description": "Tomato", "fdcId": "123"}]
        
        foods = self.service.search_foods("tomato")
        
        mock_search.assert_called_once_with("tomato", 5)
        self.assertIsInstance(foods, list)
        self.assertEqual(len(foods), 1)
        self.assertIn("description", foods[0])
        self.assertIn("fdcId", foods[0])

    @patch('src.core.services.usda_client.USDAClient.get_food_details')
    def test_get_food_details(self, mock_details):
        """Prueba la obtención de detalles de un alimento."""
        mock_details.return_value = {
            "fdcId": "123",
            "description": "Tomato",
            "foodNutrients": [{"nutrientId": "1", "value": 10}]
        }
        
        details = self.service.get_food_details("123")
        
        mock_details.assert_called_once_with("123")
        self.assertIsNotNone(details)
        self.assertIn("foodNutrients", details)

    @patch('src.core.services.usda_service.USDAService.search_foods')
    @patch('src.core.services.usda_service.USDAService.get_food_details')
    def test_get_food_nutrition(self, mock_details, mock_search):
        """Prueba la obtención de la información nutricional de un alimento."""
        mock_search.return_value = [{"fdcId": "123"}]
        mock_details.return_value = {"nutrients": {"protein": 10}}
        
        nutrition = self.service.get_food_nutrition("tomato")
        
        mock_search.assert_called_once_with("tomato", page_size=1)
        mock_details.assert_called_once_with("123")
        self.assertEqual(nutrition, {"nutrients": {"protein": 10}})


if __name__ == "__main__":
    unittest.main()
