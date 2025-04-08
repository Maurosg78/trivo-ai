from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from src.core.services.usda_service import FoodItem, USDAService
from src.features.nutrition.nutrition_analyzer import NutritionAnalyzer


class UserPreferences(BaseModel):
    dietary_restrictions: List[str] = []
    nutritional_goals: Dict[str, float] = {}
    favorite_ingredients: List[str] = []
    disliked_ingredients: List[str] = []


@dataclass
class Recommendation:
    recipe_id: str
    score: float
    reason: str
    improvements: List[str]


class RecommendationEngine:
    def __init__(self):
        self.usda_service = USDAService()
        self.nutrition_analyzer = NutritionAnalyzer()
        self.vectorizer = TfidfVectorizer()
        self.recipe_features: Dict[str, List[float]] = {}
        self.recipe_metadata: Dict[str, Dict[str, Any]] = {}

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
                        recipe_id=food.id,
                        score=score,
                        reason=reasons[0],
                        improvements=reasons[1:]
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
    ) -> List[str]:
        """Calcula beneficios nutricionales al añadir el alimento."""
        if not current_diet:
            return []

        current_profile = self.nutrition_analyzer.analyze_nutritional_profile(current_diet)
        new_profile = self.nutrition_analyzer.analyze_nutritional_profile(current_diet + [food])

        improvements = []
        for nutrient in new_profile.macronutrients:
            current = current_profile.macronutrients[nutrient]
            new = new_profile.macronutrients[nutrient]
            if new > current:
                improvements.append(f"Aumento en {nutrient}: {new - current:.2f} g")

        return improvements

    def add_recipe(self, recipe_id: str, ingredients: List[str], metadata: Dict[str, Any]) -> None:
        """Agrega una receta al motor de recomendaciones."""
        # Vectorizar ingredientes
        ingredients_text = " ".join(ingredients)
        if not self.recipe_features:
            # Primera receta, inicializar vectorizador
            self.recipe_features[recipe_id] = self.vectorizer.fit_transform([ingredients_text]).toarray()[0]
        else:
            # Recetas subsiguientes, usar vectorizador existente
            self.recipe_features[recipe_id] = self.vectorizer.transform([ingredients_text]).toarray()[0]
        
        self.recipe_metadata[recipe_id] = metadata

    def get_recommendations(self, recipe_id: str, n_recommendations: int = 5) -> List[Recommendation]:
        """Obtiene recomendaciones para una receta específica."""
        if recipe_id not in self.recipe_features:
            raise ValueError(f"Recipe {recipe_id} not found in recommendation engine")

        # Calcular similitud con todas las recetas
        similarities = {}
        target_vector = self.recipe_features[recipe_id].reshape(1, -1)
        
        for other_id, other_vector in self.recipe_features.items():
            if other_id != recipe_id:
                other_vector = other_vector.reshape(1, -1)
                similarity = cosine_similarity(target_vector, other_vector)[0][0]
                similarities[other_id] = similarity

        # Ordenar por similitud
        sorted_recipes = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        # Generar recomendaciones
        recommendations = []
        for other_id, similarity in sorted_recipes[:n_recommendations]:
            improvements = self._generate_improvements(recipe_id, other_id)
            recommendations.append(Recommendation(
                recipe_id=other_id,
                score=similarity,
                reason=self._generate_reason(recipe_id, other_id, similarity),
                improvements=improvements
            ))

        return recommendations

    def _generate_improvements(self, recipe_id: str, other_id: str) -> List[str]:
        """Genera sugerencias de mejora basadas en las diferencias entre recetas."""
        improvements = []
        target_metadata = self.recipe_metadata[recipe_id]
        other_metadata = self.recipe_metadata[other_id]

        # Comparar tiempos de fermentación
        if target_metadata.get("fermentation_time", 0) < other_metadata.get("fermentation_time", 0):
            improvements.append("Considera aumentar el tiempo de fermentación para mejorar el sabor")

        # Comparar temperaturas de horneado
        if target_metadata.get("baking_temperature", 0) < other_metadata.get("baking_temperature", 0):
            improvements.append("Una temperatura de horneado más alta podría mejorar la textura")

        return improvements

    def _generate_reason(self, recipe_id: str, other_id: str, similarity: float) -> str:
        """Genera una explicación para la recomendación."""
        target_metadata = self.recipe_metadata[recipe_id]
        other_metadata = self.recipe_metadata[other_id]

        reasons = []
        if abs(target_metadata.get("fermentation_time", 0) - other_metadata.get("fermentation_time", 0)) < 2:
            reasons.append("tiempos de fermentación similares")
        if abs(target_metadata.get("baking_temperature", 0) - other_metadata.get("baking_temperature", 0)) < 10:
            reasons.append("temperaturas de horneado similares")

        if reasons:
            return f"Recomendada por tener {', '.join(reasons)}"
        else:
            return f"Recomendada por similitud general (score: {similarity:.2f})"
