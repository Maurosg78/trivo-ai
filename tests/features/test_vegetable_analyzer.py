import pytest
from unittest.mock import MagicMock, patch

from src.features.nutrition.nutrition_analyzer import NutritionAnalyzer, NutritionalProfile
from src.core.services.usda_service import USDAService


class TestVegetableAnalyzer:
    """Tests para el analizador nutricional con énfasis en vegetales."""

    @pytest.fixture
    def mock_usda_service(self):
        """Mock del servicio USDA."""
        mock_service = MagicMock(spec=USDAService)
        
        # Configurar respuestas simuladas para los vegetales
        mock_service.get_food_nutrition.side_effect = lambda name: {
            "cauliflower": {
                "fdcId": "123",
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
            "chickpea": {
                "fdcId": "456",
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
            "rice flour": {
                "fdcId": "789",
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
        }.get(name, {})
        
        return mock_service

    @pytest.fixture
    def nutrition_analyzer(self, mock_usda_service):
        """Instancia del analizador nutricional con servicio USDA mockeado."""
        return NutritionAnalyzer(mock_usda_service)

    def test_calculate_glycemic_index(self, nutrition_analyzer):
        """Test de cálculo del índice glucémico para una receta con vegetales."""
        # Receta base de pizza con coliflor
        ingredients = {
            "cauliflower": 300.0,       # Base de coliflor
            "chickpea": 100.0,          # Harina de garbanzo
            "rice flour": 50.0,         # Harina de arroz
            "olive oil": 15.0,          # Aceite de oliva
            "salt": 5.0                 # Sal
        }
        
        # Calcular índice glucémico
        gi = nutrition_analyzer.calculate_glycemic_index(ingredients)
        
        # Verificar que el GI es menor a 55 (bajo GI)
        assert gi < 55, "La receta con base de coliflor debería tener un índice glucémico bajo"
        
        # Calcular GI para una versión con más harina de arroz
        high_carb_ingredients = {
            "cauliflower": 100.0,
            "chickpea": 100.0,
            "rice flour": 300.0,        # Más harina de arroz (alto GI)
            "olive oil": 15.0,
            "salt": 5.0
        }
        
        high_gi = nutrition_analyzer.calculate_glycemic_index(high_carb_ingredients)
        
        # Verificar que el GI es mayor
        assert high_gi > gi, "Una receta con más harina de arroz debería tener un GI más alto"
        assert high_gi > 70, "Una receta alta en carbohidratos debería tener un GI alto"

    def test_analyze_nutritional_profile(self, nutrition_analyzer):
        """Test del análisis del perfil nutricional para una receta con vegetales."""
        # Receta base de pizza con coliflor
        ingredients = {
            "cauliflower": 300.0,
            "chickpea": 100.0,
            "rice flour": 50.0,
            "olive oil": 15.0,
            "salt": 5.0
        }
        
        # Analizar perfil nutricional
        profile = nutrition_analyzer.analyze_nutritional_profile(ingredients)
        
        # Verificar que el perfil es una instancia de NutritionalProfile
        assert isinstance(profile, NutritionalProfile)
        
        # Verificar que contiene los nutrientes esperados
        assert "protein" in profile.macronutrients
        assert "fat" in profile.macronutrients
        assert "carbohydrates" in profile.macronutrients
        assert profile.fiber > 0
        assert profile.calories > 0
        assert profile.glycemic_index > 0
        
        # Verificar valores esperados para la receta
        assert profile.macronutrients["protein"] > 15, "La receta debería tener un buen contenido proteico"
        assert profile.fiber > 10, "La receta debería ser rica en fibra"
        assert profile.glycemic_index < 55, "La receta debería tener un GI bajo"

    def test_optimize_for_nutrition(self, nutrition_analyzer):
        """Test de la optimización nutricional para una receta con vegetales."""
        # Perfil nutricional actual
        current_profile = NutritionalProfile(
            macronutrients={"protein": 12.0, "fat": 8.0, "carbohydrates": 40.0},
            micronutrients={"calcium": 100.0, "iron": 2.0},
            fiber=8.0,
            calories=300.0,
            glycemic_index=60.0
        )
        
        # Perfil nutricional objetivo
        target_profile = NutritionalProfile(
            macronutrients={"protein": 15.0, "fat": 5.0, "carbohydrates": 35.0},
            micronutrients={"calcium": 120.0, "iron": 3.0},
            fiber=12.0,
            calories=280.0,
            glycemic_index=50.0
        )
        
        # Optimizar la receta
        adjustments = nutrition_analyzer.optimize_for_nutrition(current_profile, target_profile)
        
        # Verificar que hay ajustes sugeridos
        assert len(adjustments) > 0
        
        # Verificar los ajustes específicos
        assert "chickpea" in adjustments, "Debería sugerir aumentar garbanzos para proteínas"
        assert "reduce_olive_oil" in adjustments, "Debería sugerir reducir aceite para menos grasa"
        assert "cauliflower" in adjustments, "Debería sugerir aumentar coliflor para reducir GI"
        assert "add_vegetables" in adjustments, "Debería sugerir aumentar vegetales para más fibra"

    def test_calculate_nutritional_score(self, nutrition_analyzer, mock_usda_service):
        """Test de cálculo de puntaje nutricional para vegetales."""
        from src.features.nutrition.nutrition_analyzer import Recipe, RecipeIngredient
        from datetime import datetime
        
        # Crear una receta con vegetales
        recipe = Recipe(
            id=1,
            name="Pizza de Coliflor",
            description="Pizza con base de coliflor sin gluten",
            ingredients=[
                RecipeIngredient(id=1, name="cauliflower", quantity=300.0, unit="g", recipe_id=1),
                RecipeIngredient(id=2, name="chickpea", quantity=100.0, unit="g", recipe_id=1),
                RecipeIngredient(id=3, name="olive oil", quantity=15.0, unit="g", recipe_id=1)
            ],
            instructions="Mezclar todos los ingredientes, formar la base y hornear.",
            created_at=datetime.now()
        )
        
        # Mockear el método _get_ingredient_nutrition para usar datos de prueba
        with patch.object(
            nutrition_analyzer, '_get_ingredient_nutrition', 
            side_effect=lambda ing: {
                "protein": 1.9 if ing.name == "cauliflower" else 8.9 if ing.name == "chickpea" else 0.0,
                "fiber": 2.0 if ing.name == "cauliflower" else 7.6 if ing.name == "chickpea" else 0.0,
                "sugar": 1.9 if ing.name == "cauliflower" else 0.0,
                "saturated_fat": 0.0 if ing.name == "cauliflower" else 0.0 if ing.name == "chickpea" else 2.0
            }
        ):
            score = nutrition_analyzer.calculate_nutritional_score(recipe)
            
            # Verificar que el puntaje es positivo
            assert score > 0, "La receta debería tener un puntaje nutricional positivo"
            
            # La coliflor y el garbanzo son ricos en fibra y proteínas, así que deberían tener un buen puntaje
            assert score > 3, "La receta con coliflor y garbanzo debería tener un buen puntaje nutricional" 