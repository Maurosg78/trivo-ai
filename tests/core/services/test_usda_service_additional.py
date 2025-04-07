import pytest
from unittest.mock import Mock, patch

from src.core.services.usda_service import USDAService


class TestUSDAServiceErrorCases:
    """Pruebas para escenarios de error y caché en USDAService."""

    @pytest.fixture
    def mock_usda_client(self):
        """Mock para USDAClient."""
        with patch("src.core.services.usda_service.USDAClient") as mock:
            client = Mock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def mock_cache(self):
        """Mock para RedisCache."""
        cache = Mock()
        return cache

    def test_search_foods_with_cache_hit(self, mock_usda_client, mock_cache):
        """Prueba la búsqueda de alimentos con un hit en la caché."""
        # Configurar mock de caché
        mock_cache.get.return_value = [{"fdcId": "123", "description": "Tomate"}]
        
        # Crear servicio
        service = USDAService(cache=mock_cache)
        
        # Realizar búsqueda
        result = service.search_foods("tomate", page_size=5)
        
        # Verificar que se usó la caché
        mock_cache.get.assert_called_once_with("search:tomate:5")
        assert result == [{"fdcId": "123", "description": "Tomate"}]
        
        # Verificar que no se llamó al cliente
        mock_usda_client.search_foods.assert_not_called()

    def test_search_foods_with_cache_miss(self, mock_usda_client, mock_cache):
        """Prueba la búsqueda de alimentos con un fallo en la caché."""
        # Configurar mocks
        mock_cache.get.return_value = None
        mock_usda_client.search_foods.return_value = {
            "foods": [{"fdcId": "123", "description": "Tomate"}]
        }
        
        # Crear servicio
        service = USDAService(cache=mock_cache)
        
        # Realizar búsqueda
        result = service.search_foods("tomate", page_size=5)
        
        # Verificar que se usó la caché
        mock_cache.get.assert_called_once_with("search:tomate:5")
        
        # Verificar que se llamó al cliente
        mock_usda_client.search_foods.assert_called_once_with("tomate", 5)
        
        # Verificar que se guardó en caché
        mock_cache.set.assert_called_once_with(
            "search:tomate:5", 
            [{"fdcId": "123", "description": "Tomate"}], 
            expire=3600
        )
        
        # Verificar resultado
        assert result == [{"fdcId": "123", "description": "Tomate"}]

    def test_search_foods_without_cache(self, mock_usda_client):
        """Prueba la búsqueda de alimentos sin caché."""
        # Configurar mock del cliente
        mock_usda_client.search_foods.return_value = {
            "foods": [{"fdcId": "123", "description": "Tomate"}]
        }
        
        # Crear servicio sin caché
        service = USDAService()
        
        # Realizar búsqueda
        result = service.search_foods("tomate", page_size=5)
        
        # Verificar que se llamó al cliente
        mock_usda_client.search_foods.assert_called_once_with("tomate", 5)
        
        # Verificar resultado
        assert result == [{"fdcId": "123", "description": "Tomate"}]

    def test_get_food_details_with_cache_hit(self, mock_usda_client, mock_cache):
        """Prueba la obtención de detalles de alimento con un hit en la caché."""
        # Configurar mock de caché
        mock_cache.get.return_value = {"fdcId": "123", "description": "Tomate"}
        
        # Crear servicio
        service = USDAService(cache=mock_cache)
        
        # Obtener detalles
        result = service.get_food_details("123")
        
        # Verificar que se usó la caché
        mock_cache.get.assert_called_once_with("food:123")
        assert result == {"fdcId": "123", "description": "Tomate"}
        
        # Verificar que no se llamó al cliente
        mock_usda_client.get_food_details.assert_not_called()

    def test_get_food_details_with_cache_miss(self, mock_usda_client, mock_cache):
        """Prueba la obtención de detalles de alimento con un fallo en la caché."""
        # Configurar mocks
        mock_cache.get.return_value = None
        mock_usda_client.get_food_details.return_value = {"fdcId": "123", "description": "Tomate"}
        
        # Crear servicio
        service = USDAService(cache=mock_cache)
        
        # Obtener detalles
        result = service.get_food_details("123")
        
        # Verificar que se usó la caché
        mock_cache.get.assert_called_once_with("food:123")
        
        # Verificar que se llamó al cliente
        mock_usda_client.get_food_details.assert_called_once_with("123")
        
        # Verificar que se guardó en caché
        mock_cache.set.assert_called_once_with(
            "food:123", 
            {"fdcId": "123", "description": "Tomate"}, 
            expire=86400
        )
        
        # Verificar resultado
        assert result == {"fdcId": "123", "description": "Tomate"}

    def test_get_food_nutrition_no_results(self, mock_usda_client):
        """Prueba la obtención de nutrición de alimento sin resultados."""
        # Configurar mock del cliente
        mock_usda_client.search_foods.return_value = {"foods": []}
        
        # Crear servicio
        service = USDAService()
        
        # Obtener nutrición
        result = service.get_food_nutrition("tomate")
        
        # Verificar resultado
        assert result == {}
        mock_usda_client.get_food_details.assert_not_called()

    def test_get_food_nutrition_with_results(self, mock_usda_client):
        """Prueba la obtención de nutrición de alimento con resultados."""
        # Configurar mock del cliente
        mock_usda_client.search_foods.return_value = {
            "foods": [{"fdcId": "123", "description": "Tomate"}]
        }
        mock_usda_client.get_food_details.return_value = {
            "fdcId": "123", 
            "description": "Tomate",
            "foodNutrients": [
                {"nutrientName": "Protein", "value": 0.9}
            ]
        }
        
        # Crear servicio
        service = USDAService()
        
        # Obtener nutrición
        result = service.get_food_nutrition("tomate")
        
        # Verificar llamadas
        mock_usda_client.search_foods.assert_called_once_with("tomate", 1)
        mock_usda_client.get_food_details.assert_called_once_with("123")
        
        # Verificar resultado
        assert result["fdcId"] == "123"
        assert result["description"] == "Tomate"
        assert "foodNutrients" in result 