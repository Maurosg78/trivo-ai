"""
Optimizador de recetas que integra análisis nutricional y recomendaciones.
"""

import logging
from typing import Dict, List, Optional, Tuple

from src.features.nutrition.nutrition_analyzer import NutritionAnalyzer, NutritionalProfile
from src.core.services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)


class RecipeOptimizer:
    """Optimiza recetas basadas en objetivos nutricionales y preferencias."""
    
    def __init__(
        self, 
        nutrition_analyzer: NutritionAnalyzer, 
        recommendation_service: RecommendationService
    ):
        """
        Inicializa el optimizador de recetas.
        
        Args:
            nutrition_analyzer: Analizador nutricional
            recommendation_service: Servicio de recomendaciones
        """
        self.nutrition_analyzer = nutrition_analyzer
        self.recommendation_service = recommendation_service
    
    def optimize_recipe(
        self, 
        ingredients: Dict[str, float], 
        target_profile: Optional[NutritionalProfile] = None,
        recipe_type: str = "pizza",
        constraints: Optional[Dict[str, any]] = None
    ) -> Tuple[Dict[str, float], List[Dict]]:
        """
        Optimiza una receta para alcanzar objetivos nutricionales.
        
        Args:
            ingredients: Diccionario de ingredientes actuales con sus cantidades
            target_profile: Perfil nutricional objetivo
            recipe_type: Tipo de receta (pizza, bread, etc.)
            constraints: Restricciones adicionales (alergias, preferencias, etc.)
            
        Returns:
            Ingredientes optimizados y recomendaciones adicionales
        """
        # Analizar perfil nutricional actual
        current_profile = self.nutrition_analyzer.analyze_nutritional_profile(ingredients)
        
        # Si no se especifica un perfil objetivo, usar uno por defecto
        if target_profile is None:
            target_profile = self._get_default_target_profile(recipe_type)
        
        # Obtener sugerencias de ajustes basados en nutrición
        nutritional_adjustments = self.nutrition_analyzer.optimize_for_nutrition(
            current_profile, target_profile
        )
        
        # Aplicar ajustes a los ingredientes
        optimized_ingredients = self._apply_nutritional_adjustments(
            ingredients, nutritional_adjustments
        )
        
        # Obtener recomendaciones de vegetales
        vegetable_recommendations = self.recommendation_service.get_vegetable_recommendations(
            recipe_type=recipe_type,
            desired_properties=self._extract_desired_properties(constraints)
        )
        
        # Filtrar recomendaciones según restricciones
        if constraints and "allergies" in constraints:
            vegetable_recommendations = self._filter_for_allergies(
                vegetable_recommendations, constraints["allergies"]
            )
        
        return optimized_ingredients, vegetable_recommendations
    
    def visualize_nutritional_profile(
        self, 
        ingredients: Dict[str, float], 
        target_profile: Optional[NutritionalProfile] = None,
        recipe_type: str = "pizza"
    ) -> Dict:
        """
        Genera datos para visualizar el perfil nutricional.
        
        Args:
            ingredients: Diccionario de ingredientes con sus cantidades
            target_profile: Perfil nutricional objetivo
            recipe_type: Tipo de receta
            
        Returns:
            Datos para visualización comparativa
        """
        # Analizar perfil nutricional actual
        current_profile = self.nutrition_analyzer.analyze_nutritional_profile(ingredients)
        
        # Si no se especifica un perfil objetivo, usar uno por defecto
        if target_profile is None:
            target_profile = self._get_default_target_profile(recipe_type)
        
        # Preparar datos para visualización
        visualization_data = {
            "macronutrients": {
                "current": current_profile.macronutrients,
                "target": target_profile.macronutrients
            },
            "fiber": {
                "current": current_profile.fiber,
                "target": target_profile.fiber
            },
            "calories": {
                "current": current_profile.calories,
                "target": target_profile.calories
            },
            "glycemic_index": {
                "current": current_profile.glycemic_index,
                "target": target_profile.glycemic_index,
                "category": self._categorize_gi(current_profile.glycemic_index)
            }
        }
        
        return visualization_data
    
    def _get_default_target_profile(self, recipe_type: str) -> NutritionalProfile:
        """Obtiene un perfil nutricional objetivo por defecto según el tipo de receta."""
        if recipe_type == "pizza":
            return NutritionalProfile(
                macronutrients={"protein": 15.0, "fat": 5.0, "carbohydrates": 30.0},
                micronutrients={},
                fiber=8.0,
                calories=250.0,
                glycemic_index=50.0
            )
        elif recipe_type == "bread":
            return NutritionalProfile(
                macronutrients={"protein": 12.0, "fat": 3.0, "carbohydrates": 45.0},
                micronutrients={},
                fiber=6.0,
                calories=280.0,
                glycemic_index=55.0
            )
        else:  # vegetable_based
            return NutritionalProfile(
                macronutrients={"protein": 6.0, "fat": 3.0, "carbohydrates": 20.0},
                micronutrients={},
                fiber=12.0,
                calories=180.0,
                glycemic_index=40.0
            )
    
    def _apply_nutritional_adjustments(
        self, ingredients: Dict[str, float], adjustments: Dict[str, float]
    ) -> Dict[str, float]:
        """Aplica ajustes nutricionales a los ingredientes."""
        optimized = ingredients.copy()
        
        for adjustment, value in adjustments.items():
            if adjustment.startswith("reduce_"):
                # Reducir un ingrediente
                ingredient_to_reduce = adjustment[7:]  # Eliminar "reduce_"
                if ingredient_to_reduce in optimized and optimized[ingredient_to_reduce] >= value:
                    optimized[ingredient_to_reduce] -= value
                    if optimized[ingredient_to_reduce] <= 0:
                        del optimized[ingredient_to_reduce]
            elif adjustment == "add_vegetables":
                # Distribución de vegetales a añadir
                vegetable_distribution = {
                    "cauliflower": 0.5,  # 50% coliflor
                    "zucchini": 0.3,     # 30% calabacín
                    "spinach": 0.2       # 20% espinacas
                }
                for veggie, ratio in vegetable_distribution.items():
                    if veggie in optimized:
                        optimized[veggie] += value * ratio
                    else:
                        optimized[veggie] = value * ratio
            else:
                # Añadir o aumentar un ingrediente
                if adjustment in optimized:
                    optimized[adjustment] += value
                else:
                    optimized[adjustment] = value
        
        return optimized
    
    def _extract_desired_properties(self, constraints: Optional[Dict]) -> Dict[str, any]:
        """Extrae propiedades deseadas de las restricciones."""
        desired_properties = {}
        
        if not constraints:
            return desired_properties
        
        # Mapeo de restricciones a propiedades deseadas
        if "low_carb" in constraints and constraints["low_carb"]:
            desired_properties["water_content"] = 85  # Preferir vegetales con alto contenido de agua
        
        if "texture_preference" in constraints:
            desired_properties["texture"] = constraints["texture_preference"]
        
        if "flavor_preference" in constraints:
            desired_properties["flavor"] = constraints["flavor_preference"]
        
        return desired_properties
    
    def _filter_for_allergies(
        self, recommendations: List[Dict], allergies: List[str]
    ) -> List[Dict]:
        """Filtra recomendaciones según alergias."""
        filtered_recommendations = []
        
        for rec in recommendations:
            is_allergenic = False
            
            # Comprobar si el vegetal está en la lista de alergias
            for allergy in allergies:
                if allergy.lower() in rec["name"].lower():
                    is_allergenic = True
                    break
            
            if not is_allergenic:
                filtered_recommendations.append(rec)
        
        return filtered_recommendations
    
    def _categorize_gi(self, gi_value: float) -> str:
        """Categoriza el índice glucémico."""
        if gi_value < 55:
            return "bajo"
        elif gi_value < 70:
            return "medio"
        else:
            return "alto" 