from typing import Dict, List

import numpy as np
from pydantic import BaseModel

from src.core.services.usda_service import FoodItem, USDAService
from src.features.nutrition.nutrition_analyzer import NutritionAnalyzer


class UserPreferences(BaseModel):
    dietary_restrictions: List[str] = []
    nutritional_goals: Dict[str, float] = {}
    favorite_ingredients: List[str] = []
    disliked_ingredients: List[str] = []


class Recommendation(BaseModel):
    food_item: FoodItem
    score: float
    reasons: List[str]
    nutritional_benefits: Dict[str, float]


class RecommendationEngine:
    def __init__(self):
        self.usda_service = USDAService()
        self.nutrition_analyzer = NutritionAnalyzer()

    async def get_recommendations(
        self, user_prefs: UserPreferences, current_diet: List[FoodItem], limit: int = 5
    ) -> List[Recommendation]:
        """Genera recomendaciones personalizadas basadas en preferencias y dieta actual."""
        # Obtener alimentos potenciales
        potential_foods = await self._get_potential_foods(user_prefs)

        # Calcular scores para cada alimento
        scored_foods = []
        for food in potential_foods:
            score = await self._calculate_food_score(food, user_prefs, current_diet)
            if score > 0:
                reasons = self._generate_recommendation_reasons(food, score)
                nutritional_benefits = self._calculate_nutritional_benefits(food, current_diet)

                scored_foods.append(
                    Recommendation(
                        food_item=food,
                        score=score,
                        reasons=reasons,
                        nutritional_benefits=nutritional_benefits,
                    )
                )

        # Ordenar por score y retornar los mejores
        scored_foods.sort(key=lambda x: x.score, reverse=True)
        return scored_foods[:limit]

    async def _get_potential_foods(self, user_prefs: UserPreferences) -> List[FoodItem]:
        """Obtiene alimentos potenciales basados en preferencias."""
        # Buscar por ingredientes favoritos
        search_terms = user_prefs.favorite_ingredients
        if not search_terms:
            search_terms = ["pizza", "dough", "cheese", "tomato"]

        all_foods = []
        for term in search_terms:
            foods = await self.usda_service.search_foods(term)
            all_foods.extend(foods)

        # Filtrar por restricciones dietéticas
        filtered_foods = []
        for food in all_foods:
            if not any(
                restriction in food.description.lower()
                for restriction in user_prefs.dietary_restrictions
            ):
                filtered_foods.append(food)

        return filtered_foods

    async def _calculate_food_score(
        self, food: FoodItem, user_prefs: UserPreferences, current_diet: List[FoodItem]
    ) -> float:
        """Calcula un score para un alimento basado en preferencias y dieta actual."""
        scores = []

        # Score por preferencias nutricionales
        if user_prefs.nutritional_goals:
            nutritional_score = self._calculate_nutritional_score(
                food, user_prefs.nutritional_goals
            )
            scores.append(nutritional_score)

        # Score por ingredientes favoritos
        if user_prefs.favorite_ingredients:
            ingredient_score = self._calculate_ingredient_score(
                food, user_prefs.favorite_ingredients
            )
            scores.append(ingredient_score)

        # Score por balance nutricional
        balance_score = self._calculate_balance_score(food, current_diet)
        scores.append(balance_score)

        # Promedio de scores
        return np.mean(scores) if scores else 0.0

    def _calculate_nutritional_score(
        self, food: FoodItem, nutritional_goals: Dict[str, float]
    ) -> float:
        """Calcula score basado en objetivos nutricionales."""
        scores = []
        for nutrient, target in nutritional_goals.items():
            nutrient_value = next(
                (n.amount for n in food.nutrients if n.name.lower() == nutrient.lower()), 0.0
            )
            # Normalizar score entre 0 y 1
            score = 1 - abs(nutrient_value - target) / max(target, nutrient_value)
            scores.append(score)
        return np.mean(scores) if scores else 0.0

    def _calculate_ingredient_score(self, food: FoodItem, favorite_ingredients: List[str]) -> float:
        """Calcula score basado en ingredientes favoritos."""
        if not favorite_ingredients:
            return 0.5

        matches = sum(
            1
            for ingredient in favorite_ingredients
            if ingredient.lower() in food.description.lower()
        )
        return matches / len(favorite_ingredients)

    def _calculate_balance_score(self, food: FoodItem, current_diet: List[FoodItem]) -> float:
        """Calcula score basado en balance nutricional con la dieta actual."""
        if not current_diet:
            return 0.5

        # Analizar perfil nutricional actual
        current_profile = self.nutrition_analyzer.analyze_nutritional_profile(current_diet)

        # Analizar perfil con el nuevo alimento
        new_profile = self.nutrition_analyzer.analyze_nutritional_profile(current_diet + [food])

        # Calcular mejora en balance
        improvements = []
        for nutrient in current_profile.macronutrients:
            current = current_profile.macronutrients[nutrient]
            new = new_profile.macronutrients[nutrient]
            if current > 0:
                improvement = (new - current) / current
                improvements.append(max(0, improvement))

        return np.mean(improvements) if improvements else 0.0

    def _generate_recommendation_reasons(self, food: FoodItem, score: float) -> List[str]:
        """Genera razones para la recomendación."""
        reasons = []

        # Razones basadas en nutrientes principales
        main_nutrients = {"protein": "proteína", "carbohydrate": "carbohidratos", "fat": "grasas"}

        for nutrient, name in main_nutrients.items():
            value = next((n.amount for n in food.nutrients if n.name.lower() == nutrient), None)
            if value is not None:
                reasons.append(f"Buena fuente de {name}")

        # Razones basadas en score
        if score > 0.8:
            reasons.append("Excelente opción para tus objetivos")
        elif score > 0.6:
            reasons.append("Buena opción para tu dieta")

        return reasons

    def _calculate_nutritional_benefits(
        self, food: FoodItem, current_diet: List[FoodItem]
    ) -> Dict[str, float]:
        """Calcula beneficios nutricionales al añadir el alimento."""
        if not current_diet:
            return {nutrient.name: nutrient.amount for nutrient in food.nutrients}

        current_profile = self.nutrition_analyzer.analyze_nutritional_profile(current_diet)
        new_profile = self.nutrition_analyzer.analyze_nutritional_profile(current_diet + [food])

        benefits = {}
        for nutrient in new_profile.macronutrients:
            current = current_profile.macronutrients[nutrient]
            new = new_profile.macronutrients[nutrient]
            if new > current:
                benefits[nutrient] = new - current

        return benefits
