import pytest
from unittest.mock import Mock, patch

from src.core.services.recommendation_service import RecommendationService


@pytest.fixture
def mock_usda_service():
    mock = Mock()
    return mock


@pytest.fixture
def recommendation_service(mock_usda_service):
    return RecommendationService(usda_service=mock_usda_service)


def test_get_recommendations_empty_result(recommendation_service, mock_usda_service):
    """Prueba obtener recomendaciones cuando no hay datos del ingrediente base."""
    # Configurar mock para que no devuelva datos del ingrediente base
    mock_usda_service.get_food_nutrition.return_value = None
    
    # Llamar al método
    recommendations = recommendation_service.get_recommendations("tomate")
    
    # Verificar que no hay recomendaciones
    assert recommendations == []
    mock_usda_service.get_food_nutrition.assert_called_once_with("tomate")


def test_get_recommendations_success(recommendation_service, mock_usda_service):
    """Prueba obtener recomendaciones con datos válidos."""
    # Configurar mocks
    mock_usda_service.get_food_nutrition.return_value = {"fdcId": "123", "description": "Tomate"}
    mock_usda_service.search_foods.return_value = [
        {"fdcId": "123", "description": "Tomate"},
        {"fdcId": "456", "description": "Salsa de tomate"},
        {"fdcId": "789", "description": "Puré de tomate"}
    ]
    mock_usda_service.get_food_details.return_value = {
        "fdcId": "456",
        "description": "Salsa de tomate",
        "foodNutrients": [
            {"nutrientName": "protein", "value": 1.5},
            {"nutrientName": "total lipid (fat)", "value": 0.5},
            {"nutrientName": "carbohydrate", "value": 3.5}
        ]
    }
    
    # Llamar al método
    recommendations = recommendation_service.get_recommendations("tomate", limit=2)
    
    # Verificar resultados
    assert len(recommendations) == 2
    assert recommendations[0]["name"] == "Salsa de tomate"
    assert "score" in recommendations[0]
    assert "nutrients" in recommendations[0]
    
    # Verificar llamadas a los métodos
    mock_usda_service.get_food_nutrition.assert_called_once_with("tomate")
    mock_usda_service.search_foods.assert_called_once_with("tomate", page_size=3)
    mock_usda_service.get_food_details.assert_called()


def test_enrich_recommendation(recommendation_service, mock_usda_service):
    """Prueba el enriquecimiento de una recomendación con datos nutricionales."""
    # Configurar mock
    food = {"fdcId": "456", "description": "Salsa de tomate"}
    mock_usda_service.get_food_details.return_value = {
        "fdcId": "456",
        "description": "Salsa de tomate",
        "foodNutrients": [
            {"nutrientName": "protein", "value": 1.5},
            {"nutrientName": "total lipid (fat)", "value": 0.5},
            {"nutrientName": "carbohydrate", "value": 3.5}
        ]
    }
    
    # Llamar al método interno
    result = recommendation_service._enrich_recommendation(food)
    
    # Verificar resultado
    assert result["id"] == "456"
    assert result["name"] == "Salsa de tomate"
    assert "score" in result
    assert "nutrients" in result
    
    # Verificar llamada al método
    mock_usda_service.get_food_details.assert_called_once_with("456")


def test_calculate_similarity_score_no_nutrients(recommendation_service):
    """Prueba el cálculo de puntaje de similitud sin nutrientes."""
    # Datos sin nutrientes
    food_details = {"fdcId": "456", "description": "Salsa de tomate", "foodNutrients": []}
    
    # Llamar al método
    score = recommendation_service._calculate_similarity_score(food_details)
    
    # Verificar que el puntaje es 0
    assert score == 0.0


def test_calculate_similarity_score_with_nutrients(recommendation_service):
    """Prueba el cálculo de puntaje de similitud con nutrientes."""
    # Datos con nutrientes clave
    food_details = {
        "fdcId": "456",
        "description": "Salsa de tomate",
        "foodNutrients": [
            {"nutrientName": "protein", "value": 1.5},
            {"nutrientName": "total lipid (fat)", "value": 0.5},
            {"nutrientName": "carbohydrate", "value": 3.5},
            {"nutrientName": "other nutrient", "value": 2.0}
        ]
    }
    
    # Llamar al método
    score = recommendation_service._calculate_similarity_score(food_details)
    
    # Verificar que el puntaje es mayor que 0
    assert score > 0.0
    assert score <= 10.0


def test_extract_key_nutrients(recommendation_service):
    """Prueba la extracción de nutrientes clave."""
    # Datos con varios nutrientes
    food_details = {
        "fdcId": "456",
        "description": "Salsa de tomate",
        "foodNutrients": [
            {"nutrientName": "protein", "value": 1.5},
            {"nutrientName": "total lipid (fat)", "value": 0.5},
            {"nutrientName": "carbohydrate", "value": 3.5},
            {"nutrientName": "fiber", "value": 1.2},
            {"nutrientName": "calcium", "value": 10.0},
            {"nutrientName": "other nutrient", "value": 2.0}
        ]
    }
    
    # Llamar al método
    nutrients = recommendation_service._extract_key_nutrients(food_details)
    
    # Verificar resultado
    assert "protein" in nutrients
    assert "total lipid (fat)" in nutrients
    assert "carbohydrate" in nutrients
    assert "fiber" in nutrients
    assert "calcium" in nutrients
    assert "other nutrient" not in nutrients
    assert nutrients["protein"] == 1.5


def test_get_nutritional_comparison_cache_hit(recommendation_service):
    """Prueba la comparación nutricional con caché."""
    # Configurar caché
    cache_key = "comp:tomate:cebolla"
    cached_result = {"Proteína": {"ingredient1": 1.0, "ingredient2": 1.2, "difference": 0.2}}
    recommendation_service._cache[cache_key] = cached_result
    
    # Llamar al método
    result = recommendation_service.get_nutritional_comparison("tomate", "cebolla")
    
    # Verificar resultado
    assert result == cached_result


def test_get_nutritional_comparison_success(recommendation_service, mock_usda_service):
    """Prueba la comparación nutricional con datos completos."""
    # Configurar mocks
    mock_usda_service.search_foods.side_effect = [
        {"foods": [{"fdcId": "123"}]},
        {"foods": [{"fdcId": "456"}]}
    ]
    mock_usda_service.get_food_details.side_effect = [
        {
            "foodNutrients": [
                {"nutrient": {"name": "Protein"}, "amount": 1.0},
                {"nutrient": {"name": "Total lipid (fat)"}, "amount": 0.5}
            ]
        },
        {
            "foodNutrients": [
                {"nutrient": {"name": "Protein"}, "amount": 1.2},
                {"nutrient": {"name": "Total lipid (fat)"}, "amount": 0.7}
            ]
        }
    ]
    
    # Llamar al método
    result = recommendation_service.get_nutritional_comparison("tomate", "cebolla")
    
    # Verificar resultado
    assert "Proteína" in result
    assert "Grasa total" in result
    assert result["Proteína"]["ingredient1"] == 1.0
    assert result["Proteína"]["ingredient2"] == 1.2
    assert result["Proteína"]["difference"] == pytest.approx(0.2)


def test_get_nutritional_comparison_no_results(recommendation_service, mock_usda_service):
    """Prueba la comparación nutricional sin resultados de búsqueda."""
    # Configurar mocks para que no devuelvan resultados
    mock_usda_service.search_foods.return_value = {}
    
    # Llamar al método
    result = recommendation_service.get_nutritional_comparison("tomate", "cebolla")
    
    # Verificar resultado
    assert result == {}


def test_get_nutritional_comparison_error(recommendation_service, mock_usda_service):
    """Prueba la comparación nutricional con errores."""
    # Configurar mock para lanzar excepción
    mock_usda_service.search_foods.side_effect = Exception("Error de conexión")
    
    # Llamar al método
    result = recommendation_service.get_nutritional_comparison("tomate", "cebolla")
    
    # Verificar resultado
    assert result == {} 