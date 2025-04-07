import pytest
from unittest.mock import MagicMock

from src.core.services.recommendation_service import RecommendationService
from src.core.services.usda_service import USDAService


class TestVegetableRecommendations:
    """Tests para el servicio de recomendaciones de vegetales."""

    @pytest.fixture
    def mock_usda_service(self):
        """Mock del servicio USDA."""
        return MagicMock(spec=USDAService)

    @pytest.fixture
    def recommendation_service(self, mock_usda_service):
        """Instancia del servicio de recomendaciones."""
        return RecommendationService(mock_usda_service)

    def test_get_vegetable_recommendations(self, recommendation_service):
        """Test de obtención de recomendaciones de vegetales."""
        # Obtener recomendaciones para pizza
        recommendations = recommendation_service.get_vegetable_recommendations("pizza")
        
        # Verificar que hay recomendaciones
        assert len(recommendations) > 0
        
        # Verificar estructura de las recomendaciones
        for rec in recommendations:
            assert "name" in rec
            assert "score" in rec
            assert "properties" in rec
            assert "usage_tips" in rec
            assert "substitution_ratio" in rec
            
        # Verificar que las recomendaciones están ordenadas por puntuación
        scores = [rec["score"] for rec in recommendations]
        assert sorted(scores, reverse=True) == scores, "Las recomendaciones deben estar ordenadas por puntuación"
        
        # Verificar que el vegetal mejor puntuado para pizza es adecuado (bajo contenido de agua)
        best_rec = recommendations[0]
        assert best_rec["properties"]["water_content"] < 80, "El mejor vegetal para pizza debe tener bajo contenido de agua"

    def test_vegetable_recommendations_with_properties(self, recommendation_service):
        """Test de recomendaciones con propiedades específicas."""
        # Definir propiedades deseadas
        desired_properties = {
            "texture": "elastic",
            "flavor": "mild",
            "color": "white"
        }
        
        # Obtener recomendaciones para pizza con propiedades específicas
        recommendations = recommendation_service.get_vegetable_recommendations(
            "pizza", 
            desired_properties=desired_properties
        )
        
        # Verificar que hay recomendaciones
        assert len(recommendations) > 0
        
        # Verificar que la puntuación refleja las propiedades deseadas
        for rec in recommendations:
            properties = rec["properties"]
            
            # Los vegetales con propiedades que coinciden deberían tener mayor puntuación
            if properties["texture"] == "elastic":
                assert rec["score"] > 2, "Vegetales con textura elástica deberían tener buena puntuación"
            
            if properties["flavor"] == "mild" and properties["color"] == "white":
                assert rec["score"] > 3, "Vegetales con sabor suave y color blanco deberían tener buena puntuación"

    def test_vegetable_recommendations_for_different_recipes(self, recommendation_service):
        """Test de recomendaciones para diferentes tipos de recetas."""
        # Obtener recomendaciones para diferentes tipos de recetas
        pizza_recs = recommendation_service.get_vegetable_recommendations("pizza")
        bread_recs = recommendation_service.get_vegetable_recommendations("bread")
        
        # Verificar que hay diferencias en las recomendaciones
        assert pizza_recs[0]["name"] != bread_recs[0]["name"], "Las recetas diferentes deberían tener recomendaciones diferentes"
        
        # Para pan, los vegetales con mayor contenido de almidón deberían tener mejor puntuación
        best_bread_rec = bread_recs[0]
        assert best_bread_rec["properties"]["starch"] > 5, "El mejor vegetal para pan debe tener buen contenido de almidón"
        
        # Para pizza, verificar consejos de uso
        pizza_tips = pizza_recs[0]["usage_tips"]
        assert any("pizza" in tip.lower() for tip in pizza_tips), "Deben incluirse consejos específicos para pizza"
        
        # Para pan, verificar consejos de uso
        bread_tips = bread_recs[0]["usage_tips"]
        assert any("fermentación" in tip.lower() for tip in bread_tips), "Deben incluirse consejos de fermentación para pan"

    def test_get_substitution_ratio(self, recommendation_service):
        """Test de obtención de ratios de sustitución."""
        # Verificar ratios para diferentes vegetales
        cauliflower_ratio = recommendation_service._get_substitution_ratio("cauliflower")
        chickpea_ratio = recommendation_service._get_substitution_ratio("chickpea")
        
        # Verificar estructura
        assert "flour" in cauliflower_ratio
        assert "flour" in chickpea_ratio
        
        # El garbanzo debería tener una ratio de sustitución mayor (más cercana a 1:1)
        assert chickpea_ratio["flour"] > cauliflower_ratio["flour"], "El garbanzo debería tener una ratio mayor de sustitución de harina"
        
        # La harina de garbanzo debería tener una ratio cercana a 1:1
        assert chickpea_ratio["flour"] == 1.0, "La harina de garbanzo debería tener una ratio 1:1"
        
        # Vegetales con alto contenido de agua deberían tener ratios menores
        zucchini_ratio = recommendation_service._get_substitution_ratio("zucchini")
        assert zucchini_ratio["flour"] < 0.5, "Vegetales con alto contenido de agua deberían tener ratios menores" 