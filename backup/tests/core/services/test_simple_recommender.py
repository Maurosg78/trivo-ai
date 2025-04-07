import unittest
from unittest.mock import patch, MagicMock

from src.core.services.simple_recommender import SimpleRecommender


class TestSimpleRecommender(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.recommender = SimpleRecommender(self.api_key)

    @patch('src.core.services.simple_recommender.requests.get')
    def test_search_foods(self, mock_get):
        """Prueba la búsqueda de alimentos."""
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "foods": [
                {"description": "Tomato", "fdcId": "123"},
                {"description": "Tomato sauce", "fdcId": "456"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Llamar al método
        foods = self.recommender.search_foods("tomato")
        
        # Verificar resultados
        self.assertIsInstance(foods, list)
        self.assertEqual(len(foods), 2)
        self.assertEqual(foods[0]["description"], "Tomato")
        self.assertEqual(foods[1]["fdcId"], "456")

    @patch('src.core.services.simple_recommender.requests.get')
    def test_get_food_details(self, mock_get):
        """Prueba la obtención de detalles de un alimento."""
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "fdcId": "123",
            "description": "Tomato",
            "foodNutrients": [
                {"nutrientName": "Protein", "value": 0.9},
                {"nutrientName": "Carbohydrate, by difference", "value": 3.9}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Llamar al método
        details = self.recommender.get_food_details("123")
        
        # Verificar resultados
        self.assertIsInstance(details, dict)
        self.assertEqual(details["description"], "Tomato")
        self.assertEqual(len(details["foodNutrients"]), 2)

    @patch('src.core.services.simple_recommender.SimpleRecommender.search_foods')
    @patch('src.core.services.simple_recommender.SimpleRecommender.get_food_details')
    def test_get_recommendations(self, mock_details, mock_search):
        """Prueba la generación de recomendaciones."""
        # Configurar mocks
        mock_search.return_value = [
            {"description": "Tomato", "fdcId": "123"},  # Base ingredient
            {"description": "Tomato sauce", "fdcId": "456"}  # Similar ingredient
        ]
        mock_details.return_value = {
            "fdcId": "456",
            "description": "Tomato sauce",
            "foodNutrients": [{"nutrientName": "Protein", "value": 1.2}]
        }
        
        # Llamar al método
        recommendations = self.recommender.get_recommendations("tomato")
        
        # Verificar resultados
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]["description"], "Tomato sauce")
        self.assertIn("score", recommendations[0])
        self.assertIn("nutrients", recommendations[0])


if __name__ == "__main__":
    unittest.main()
