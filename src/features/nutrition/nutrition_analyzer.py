import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class Recipe:
    """Clase que representa una receta."""

    id: int
    name: str
    description: str
    ingredients: List["RecipeIngredient"]
    instructions: str
    created_at: datetime


@dataclass
class RecipeIngredient:
    """Clase que representa un ingrediente en una receta."""

    id: int
    name: str
    quantity: float
    unit: str
    recipe_id: int


class NutritionalProfile(BaseModel):
    macronutrients: Dict[str, float]
    micronutrients: Dict[str, float]
    fiber: float
    calories: float
    glycemic_index: float


class NutritionAnalyzer:
    """Analiza el contenido nutricional de recetas."""

    def __init__(self, usda_service):
        self.usda_service = usda_service
        self.nutrient_references = self._load_nutrient_references()
        # Base de datos de índices glucémicos
        self.glycemic_index_db = {
            # Vegetales de bajo índice glucémico
            "cauliflower": 15,
            "broccoli": 15,
            "spinach": 15,
            "kale": 15,
            "cabbage": 10,
            "zucchini": 15,
            "eggplant": 20,
            "bell pepper": 15,
            "tomato": 30,
            "carrot": 35,
            "beetroot": 65,
            "sweet potato": 70,
            # Legumbres
            "chickpea": 35,
            "lentil": 30,
            "bean": 40,
            # Harinas
            "rice flour": 95,
            "potato flour": 85,
            "corn starch": 85,
            "wheat flour": 85,
            "almond flour": 25,
            "coconut flour": 45,
            # Aditivos
            "xanthan gum": 0,
            "olive oil": 0,
            "salt": 0,
            "sugar": 65,
        }

    def _load_nutrient_references(self) -> Dict[str, Dict[str, float]]:
        """
        Cargar referencias nutricionales para diferentes tipos de productos
        """
        return {
            "pizza": {
                "protein": 15.0,
                "fiber": 8.0,
                "fat": 5.0,
                "carbohydrates": 30.0,
                "calories": 250.0,
            },
            "bread": {
                "protein": 12.0,
                "fiber": 6.0,
                "fat": 3.0,
                "carbohydrates": 45.0,
                "calories": 280.0,
            },
            "vegetable_based": {
                "protein": 6.0,
                "fiber": 12.0,
                "fat": 3.0,
                "carbohydrates": 20.0,
                "calories": 180.0,
            }
        }

    def analyze_nutritional_profile(self, ingredients: Dict[str, float]) -> NutritionalProfile:
        """
        Analizar el perfil nutricional de una formulación

        Args:
            ingredients: Diccionario con nombres de ingredientes y sus cantidades en gramos

        Returns:
            Perfil nutricional de la formulación
        """
        # Inicializar perfil nutricional
        macronutrients = {
            "protein": 0.0,
            "fat": 0.0,
            "carbohydrates": 0.0,
        }
        micronutrients = {
            "calcium": 0.0,
            "iron": 0.0,
            "potassium": 0.0,
            "magnesium": 0.0,
            "zinc": 0.0,
            "vitamin_c": 0.0,
            "vitamin_a": 0.0,
            "vitamin_b6": 0.0,
        }
        fiber = 0.0
        calories = 0.0
        
        # Analizar cada ingrediente
        for ingredient_name, quantity in ingredients.items():
            # Obtener datos nutricionales de USDA
            nutrition_data = self._get_nutritional_data(ingredient_name)
            
            if not nutrition_data:
                logger.warning(f"No se encontraron datos nutricionales para {ingredient_name}")
                continue
            
            # Escalar por cantidad
            scale_factor = quantity / 100.0  # Los datos nutricionales suelen ser por 100g
            
            # Acumular macronutrientes
            for nutrient, value in nutrition_data.get("macronutrients", {}).items():
                if nutrient in macronutrients:
                    macronutrients[nutrient] += value * scale_factor
            
            # Acumular micronutrientes
            for nutrient, value in nutrition_data.get("micronutrients", {}).items():
                if nutrient in micronutrients:
                    micronutrients[nutrient] += value * scale_factor
            
            # Acumular fibra
            fiber += nutrition_data.get("fiber", 0.0) * scale_factor
            
            # Acumular calorías
            calories += nutrition_data.get("calories", 0.0) * scale_factor
        
        # Calcular índice glucémico
        glycemic_index = self.calculate_glycemic_index(ingredients)
        
        return NutritionalProfile(
            macronutrients=macronutrients,
            micronutrients=micronutrients,
            fiber=fiber,
            calories=calories,
            glycemic_index=glycemic_index
        )

    def _get_nutritional_data(self, ingredient_name: str) -> Dict:
        """Obtener datos nutricionales de un ingrediente, ya sea de USDA o de datos locales"""
        try:
            # Intentar obtener datos de USDA
            usda_data = self.usda_service.get_food_nutrition(ingredient_name)
            
            if usda_data:
                # Convertir formato USDA al formato interno
                return self._format_usda_data(usda_data)
            
            # Si no hay datos USDA, usar datos predeterminados para vegetales comunes
            if ingredient_name.lower() in ["cauliflower", "coliflor"]:
                return {
                    "macronutrients": {"protein": 1.9, "fat": 0.3, "carbohydrates": 5.0},
                    "micronutrients": {"calcium": 22, "iron": 0.4, "vitamin_c": 48.2},
                    "fiber": 2.0,
                    "calories": 25,
                }
            elif ingredient_name.lower() in ["chickpea", "garbanzo"]:
                return {
                    "macronutrients": {"protein": 8.9, "fat": 2.6, "carbohydrates": 27.4},
                    "micronutrients": {"calcium": 49, "iron": 2.9, "vitamin_c": 1.3},
                    "fiber": 7.6,
                    "calories": 164,
                }
            # Agregar más ingredientes vegetales según sea necesario
            
            # Valores predeterminados si no se encuentra el ingrediente
            return {
                "macronutrients": {"protein": 2.0, "fat": 0.5, "carbohydrates": 5.0},
                "micronutrients": {"calcium": 20, "iron": 0.5, "vitamin_c": 10},
                "fiber": 2.0,
                "calories": 30,
            }
            
        except Exception as e:
            logger.error(f"Error al obtener datos nutricionales: {str(e)}")
            return {}

    def _format_usda_data(self, usda_data: Dict) -> Dict:
        """Convertir datos de formato USDA al formato interno"""
        nutrition_data = {
            "macronutrients": {},
            "micronutrients": {},
            "fiber": 0.0,
            "calories": 0.0,
        }
        
        # Mapeo de nombres de nutrientes USDA a nombres internos
        nutrient_mapping = {
            "Protein": "protein",
            "Total lipid (fat)": "fat",
            "Carbohydrate, by difference": "carbohydrates",
            "Energy": "calories",
            "Fiber, total dietary": "fiber",
            "Calcium, Ca": "calcium",
            "Iron, Fe": "iron",
            "Potassium, K": "potassium",
            "Magnesium, Mg": "magnesium",
            "Zinc, Zn": "zinc",
            "Vitamin C, total ascorbic acid": "vitamin_c",
            "Vitamin A, RAE": "vitamin_a",
            "Vitamin B-6": "vitamin_b6",
        }
        
        # Procesar nutrientes
        for nutrient in usda_data.get("foodNutrients", []):
            usda_name = nutrient.get("nutrient", {}).get("name", "")
            value = nutrient.get("amount", 0.0)
            
            if usda_name in nutrient_mapping:
                internal_name = nutrient_mapping[usda_name]
                
                if internal_name == "fiber":
                    nutrition_data["fiber"] = value
                elif internal_name == "calories":
                    nutrition_data["calories"] = value
                elif internal_name in ["protein", "fat", "carbohydrates"]:
                    nutrition_data["macronutrients"][internal_name] = value
                else:
                    nutrition_data["micronutrients"][internal_name] = value
        
        return nutrition_data

    def calculate_glycemic_index(self, ingredients: Dict[str, float]) -> float:
        """
        Calcular el índice glucémico de la formulación

        Args:
            ingredients: Diccionario con nombres de ingredientes y sus cantidades en gramos

        Returns:
            Índice glucémico ponderado de la formulación
        """
        if not ingredients:
            return 0.0
        
        total_weight = sum(ingredients.values())
        weighted_gi = 0.0
        
        for ingredient_name, quantity in ingredients.items():
            # Buscar el índice glucémico del ingrediente
            ingredient_key = next(
                (k for k in self.glycemic_index_db.keys() if k in ingredient_name.lower()), 
                None
            )
            
            if ingredient_key:
                gi = self.glycemic_index_db[ingredient_key]
            else:
                # Valor predeterminado moderado si no se encuentra
                gi = 50
            
            # Ponderar por peso/cantidad
            weight_factor = quantity / total_weight if total_weight > 0 else 0
            weighted_gi += gi * weight_factor
        
        return weighted_gi

    def optimize_for_nutrition(
        self, current_profile: NutritionalProfile, target_profile: NutritionalProfile
    ) -> Dict[str, float]:
        """
        Optimizar la formulación para alcanzar el perfil nutricional objetivo

        Args:
            current_profile: Perfil nutricional actual
            target_profile: Perfil nutricional objetivo

        Returns:
            Sugerencias de ajustes de ingredientes
        """
        adjustments = {}
        
        # Analizar macronutrientes
        for nutrient, target_value in target_profile.macronutrients.items():
            if nutrient in current_profile.macronutrients:
                current_value = current_profile.macronutrients[nutrient]
                difference = target_value - current_value
                
                # Si hay déficit o exceso significativo
                if abs(difference) > 0.1 * target_value:  # 10% de diferencia
                    if difference > 0:  # Necesitamos aumentar
                        if nutrient == "protein":
                            adjustments["chickpea"] = difference * 10  # 10g para 1g de proteína
                        elif nutrient == "fat":
                            adjustments["olive_oil"] = difference * 5  # 5g para 1g de grasa
                        elif nutrient == "carbohydrates":
                            adjustments["rice_flour"] = difference * 3  # 3g para 1g de carbohidratos
                    else:  # Necesitamos disminuir
                        if nutrient == "protein":
                            adjustments["reduce_chickpea"] = -difference * 10
                        elif nutrient == "fat":
                            adjustments["reduce_olive_oil"] = -difference * 5
                        elif nutrient == "carbohydrates":
                            adjustments["reduce_rice_flour"] = -difference * 3
        
        # Analizar fibra
        fiber_difference = target_profile.fiber - current_profile.fiber
        if abs(fiber_difference) > 0.1 * target_profile.fiber:
            if fiber_difference > 0:
                adjustments["add_vegetables"] = fiber_difference * 15  # 15g de vegetales para 1g de fibra
            else:
                adjustments["reduce_vegetables"] = -fiber_difference * 15
        
        # Analizar índice glucémico
        gi_difference = target_profile.glycemic_index - current_profile.glycemic_index
        if abs(gi_difference) > 5:  # Diferencia de 5 puntos en GI
            if gi_difference < 0:  # Necesitamos reducir GI
                adjustments["cauliflower"] = abs(gi_difference) * 2  # Aumentar vegetales de bajo GI
                adjustments["reduce_rice_flour"] = abs(gi_difference) * 2  # Reducir harinas de alto GI
        
        return adjustments

    def calculate_nutritional_score(self, recipe: Recipe) -> float:
        """Calcula el puntaje nutricional de una receta."""
        if not recipe.ingredients:
            return 0.0

        total_score = 0.0
        total_weight = 0.0

        for ingredient in recipe.ingredients:
            nutrition_data = self._get_ingredient_nutrition(ingredient)
            if nutrition_data:
                score = self._calculate_ingredient_score(nutrition_data)
                weight = ingredient.quantity
                total_score += score * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _get_ingredient_nutrition(self, ingredient: RecipeIngredient) -> Optional[Dict]:
        """Obtiene los datos nutricionales de un ingrediente."""
        try:
            return self.usda_service.get_food_nutrition(ingredient.name)
        except Exception as e:
            logger.error(f"Error al obtener datos nutricionales: {str(e)}")
            return None

    def _calculate_ingredient_score(self, nutrition_data: Dict) -> float:
        """Calcula el puntaje nutricional de un ingrediente."""
        score = 0.0

        # Puntos por nutrientes beneficiosos
        if "protein" in nutrition_data:
            score += nutrition_data["protein"] * 0.5
        if "fiber" in nutrition_data:
            score += nutrition_data["fiber"] * 0.3

        # Punalización por nutrientes perjudiciales
        if "sugar" in nutrition_data:
            score -= nutrition_data["sugar"] * 0.2
        if "saturated_fat" in nutrition_data:
            score -= nutrition_data["saturated_fat"] * 0.3

        return max(0.0, min(10.0, score))
