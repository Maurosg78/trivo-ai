import pytest
from unittest.mock import MagicMock

from src.features.nutrition.nutrition_analyzer import NutritionAnalyzer, NutritionalProfile
from src.core.services.recommendation_service import RecommendationService
from src.features.nutrition.recipe_optimizer import RecipeOptimizer


class TestRecipeOptimizer:
    """Tests para el optimizador de recetas."""

    @pytest.fixture
    def mock_analyzer(self):
        """Mock del analizador nutricional."""
        mock = MagicMock(spec=NutritionAnalyzer)
        
        # Configurar comportamiento del mock para analyze_nutritional_profile
        mock.analyze_nutritional_profile.return_value = NutritionalProfile(
            macronutrients={"protein": 10.0, "fat": 8.0, "carbohydrates": 35.0},
            micronutrients={},
            fiber=5.0,
            calories=300.0,
            glycemic_index=60.0
        )
        
        # Configurar comportamiento del mock para optimize_for_nutrition
        mock.optimize_for_nutrition.return_value = {
            "chickpea": 30.0,           # Añadir 30g de garbanzos
            "reduce_rice_flour": 20.0,  # Reducir 20g de harina de arroz
            "add_vegetables": 50.0      # Añadir 50g de vegetales
        }
        
        return mock

    @pytest.fixture
    def mock_recommender(self):
        """Mock del servicio de recomendaciones."""
        mock = MagicMock(spec=RecommendationService)
        
        # Configurar comportamiento del mock para get_vegetable_recommendations
        mock.get_vegetable_recommendations.return_value = [
            {
                "name": "cauliflower",
                "score": 8.5,
                "properties": {"water_content": 92, "binding": "low"},
                "usage_tips": ["Pre-cocinar y escurrir bien"],
                "substitution_ratio": {"flour": 0.7}
            },
            {
                "name": "chickpea",
                "score": 7.2,
                "properties": {"water_content": 60, "binding": "high"},
                "usage_tips": ["Moler finamente"],
                "substitution_ratio": {"flour": 1.0}
            }
        ]
        
        return mock

    @pytest.fixture
    def recipe_optimizer(self, mock_analyzer, mock_recommender):
        """Instancia del optimizador de recetas con mocks."""
        return RecipeOptimizer(mock_analyzer, mock_recommender)

    def test_optimize_recipe(self, recipe_optimizer, mock_analyzer, mock_recommender):
        """Test de optimización de receta."""
        # Receta inicial
        ingredients = {
            "rice_flour": 100.0,
            "potato": 50.0,
            "olive_oil": 15.0,
            "salt": 5.0
        }
        
        # Optimizar receta
        optimized_ingredients, recommendations = recipe_optimizer.optimize_recipe(
            ingredients, recipe_type="pizza"
        )
        
        # Verificar que se llamaron los métodos correctos
        mock_analyzer.analyze_nutritional_profile.assert_called_once_with(ingredients)
        assert mock_analyzer.optimize_for_nutrition.call_count == 1
        mock_recommender.get_vegetable_recommendations.assert_called_once()
        
        # Verificar ajustes aplicados
        assert "chickpea" in optimized_ingredients
        assert optimized_ingredients["chickpea"] == 30.0
        assert optimized_ingredients["rice_flour"] == 80.0  # 100 - 20
        
        # Verificar que se agregaron los vegetales
        assert "cauliflower" in optimized_ingredients
        assert "zucchini" in optimized_ingredients
        assert "spinach" in optimized_ingredients
        
        # Verificar que hay recomendaciones
        assert len(recommendations) == 2
        assert recommendations[0]["name"] == "cauliflower"

    def test_optimize_recipe_with_constraints(self, recipe_optimizer, mock_recommender):
        """Test de optimización con restricciones."""
        # Receta inicial
        ingredients = {
            "rice_flour": 100.0,
            "potato": 50.0,
            "olive_oil": 15.0,
            "salt": 5.0
        }
        
        # Restricciones
        constraints = {
            "allergies": ["chickpea"],
            "low_carb": True,
            "texture_preference": "elastic"
        }
        
        # Optimizar receta
        recipe_optimizer.optimize_recipe(
            ingredients, recipe_type="pizza", constraints=constraints
        )
        
        # Verificar que se pasaron las propiedades deseadas correctamente
        expected_properties = {
            "water_content": 85,
            "texture": "elastic"
        }
        mock_recommender.get_vegetable_recommendations.assert_called_with(
            recipe_type="pizza", 
            desired_properties=expected_properties
        )

    def test_visualize_nutritional_profile(self, recipe_optimizer, mock_analyzer):
        """Test de visualización del perfil nutricional."""
        # Receta
        ingredients = {
            "cauliflower": 300.0,
            "chickpea": 100.0,
            "olive_oil": 15.0,
            "salt": 5.0
        }
        
        # Obtener datos de visualización
        visualization_data = recipe_optimizer.visualize_nutritional_profile(
            ingredients, recipe_type="pizza"
        )
        
        # Verificar estructura de datos
        assert "macronutrients" in visualization_data
        assert "fiber" in visualization_data
        assert "calories" in visualization_data
        assert "glycemic_index" in visualization_data
        
        # Verificar que cada sección tiene current y target
        assert "current" in visualization_data["macronutrients"]
        assert "target" in visualization_data["macronutrients"]
        
        # Verificar categorización del índice glucémico
        assert "category" in visualization_data["glycemic_index"]
        assert visualization_data["glycemic_index"]["category"] == "medio"  # GI = 60 