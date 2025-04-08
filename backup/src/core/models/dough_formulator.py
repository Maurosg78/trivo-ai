import json
import os
from typing import Dict, List

import numpy as np
from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    color: str
    nutritional_value: Dict[str, float]
    cost: float
    availability: float
    sustainability_score: float
    texture_properties: Dict[str, float]


class DoughFormulation(BaseModel):
    ingredients: List[Dict[str, float]]
    target_properties: Dict[str, float]
    nutritional_profile: Dict[str, float]
    cost: float
    sustainability_score: float


class DoughFormulator:
    def __init__(self):
        self.ingredients_db = {}
        self.load_ingredients()

    def load_ingredients(self):
        """Cargar base de datos de ingredientes"""
        try:
            # Ruta al archivo de ingredientes
            ingredients_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "ingredients.json"
            )

            with open(ingredients_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convertir los datos a objetos Ingredient
            for category, ingredients in data.items():
                self.ingredients_db[category] = {
                    name: Ingredient(**ingredient) for name, ingredient in ingredients.items()
                }
        except Exception as e:
            print(f"Error al cargar ingredientes: {e}")
            # Cargar datos de ejemplo si hay error
            self.ingredients_db = {
                "vegetables": {
                    "beetroot": Ingredient(
                        name="beetroot",
                        color="red",
                        nutritional_value={
                            "protein": 1.6,
                            "fiber": 2.8,
                            "fat": 0.2,
                            "carbohydrates": 9.6,
                        },
                        cost=2.5,
                        availability=0.8,
                        sustainability_score=0.9,
                        texture_properties={"elasticity": 0.7, "firmness": 0.6, "moisture": 0.8},
                    )
                }
            }

    def optimize_formulation(self, target_properties: Dict[str, float]) -> DoughFormulation:
        """
        Optimizar la formulación considerando:
        - Propiedades nutricionales
        - Costos
        - Disponibilidad local
        - Sostenibilidad
        - Textura y sabor
        """
        # Inicializar variables
        best_formulation = None
        best_score = float("-inf")

        # Generar combinaciones de ingredientes
        for category, ingredients in self.ingredients_db.items():
            for name, ingredient in ingredients.items():
                # Calcular proporciones iniciales
                proportions = self._calculate_initial_proportions(ingredient, target_properties)

                # Crear formulación
                formulation = DoughFormulation(
                    ingredients=[{name: prop} for prop in proportions],
                    target_properties=target_properties,
                    nutritional_profile=self._calculate_nutritional_profile(
                        proportions, ingredient
                    ),
                    cost=self._calculate_cost(proportions, ingredient),
                    sustainability_score=self._calculate_sustainability(proportions, ingredient),
                )

                # Evaluar formulación
                score = self._evaluate_formulation_score(formulation)

                # Actualizar mejor formulación
                if score > best_score:
                    best_score = score
                    best_formulation = formulation

        return best_formulation

    def evaluate_formulation(self, formulation: DoughFormulation) -> Dict[str, float]:
        """
        Evaluar una formulación considerando:
        - Sabor y textura
        - Costos
        - Sostenibilidad
        - Escalabilidad
        - Viabilidad comercial
        """
        evaluation = {
            "taste_score": self._evaluate_taste(formulation),
            "texture_score": self._evaluate_texture(formulation),
            "cost_score": self._evaluate_cost(formulation),
            "sustainability_score": self._evaluate_sustainability(formulation),
            "scalability_score": self._evaluate_scalability(formulation),
            "commercial_viability": self._evaluate_commercial_viability(formulation),
        }

        # Calcular score total
        evaluation["total_score"] = np.mean(list(evaluation.values()))

        return evaluation

    def _calculate_initial_proportions(
        self, ingredient: Ingredient, target_properties: Dict[str, float]
    ) -> List[float]:
        """Calcular proporciones iniciales basadas en propiedades objetivo"""
        # Calcular proporciones basadas en valores nutricionales objetivo
        proportions = []

        for nutrient, target_value in target_properties.items():
            if nutrient in ingredient.nutritional_value:
                proportion = target_value / ingredient.nutritional_value[nutrient]
                proportions.append(min(1.0, proportion))  # Limitar a 1.0

        # Normalizar proporciones
        if proportions:
            total = sum(proportions)
            proportions = [p / total for p in proportions]
        else:
            proportions = [0.3, 0.4, 0.3]  # Valores por defecto si no hay coincidencias

        return proportions

    def _calculate_nutritional_profile(
        self, proportions: List[float], ingredient: Ingredient
    ) -> Dict[str, float]:
        """Calcular perfil nutricional de la formulación"""
        return {
            nutrient: value * sum(proportions)
            for nutrient, value in ingredient.nutritional_value.items()
        }

    def _calculate_cost(self, proportions: List[float], ingredient: Ingredient) -> float:
        """Calcular costo total de la formulación"""
        return ingredient.cost * sum(proportions)

    def _calculate_sustainability(self, proportions: List[float], ingredient: Ingredient) -> float:
        """Calcular score de sostenibilidad"""
        return ingredient.sustainability_score * sum(proportions)

    def _evaluate_formulation_score(self, formulation: DoughFormulation) -> float:
        """Evaluar score general de la formulación"""
        evaluation = self.evaluate_formulation(formulation)
        return evaluation["total_score"]

    def _evaluate_taste(self, formulation: DoughFormulation) -> float:
        """Evaluar sabor de la formulación"""
        # Calcular score de sabor basado en ingredientes y sus proporciones
        taste_score = 0.0
        total_weight = 0.0

        for ingredient_dict in formulation.ingredients:
            for name, proportion in ingredient_dict.items():
                # Buscar el ingrediente en la base de datos
                for category in self.ingredients_db.values():
                    if name in category:
                        ingredient = category[name]
                        # Considerar propiedades que afectan el sabor
                        taste_score += (
                            proportion
                            * (
                                ingredient.texture_properties.get("moisture", 0.5)
                                + ingredient.texture_properties.get("firmness", 0.5)
                            )
                            / 2
                        )
                        total_weight += proportion

        return taste_score / total_weight if total_weight > 0 else 0.5

    def _evaluate_texture(self, formulation: DoughFormulation) -> float:
        """Evaluar textura de la formulación"""
        # Calcular score de textura basado en propiedades de los ingredientes
        texture_score = 0.0
        total_weight = 0.0

        for ingredient_dict in formulation.ingredients:
            for name, proportion in ingredient_dict.items():
                # Buscar el ingrediente en la base de datos
                for category in self.ingredients_db.values():
                    if name in category:
                        ingredient = category[name]
                        # Considerar propiedades de textura
                        texture_score += (
                            proportion
                            * (
                                ingredient.texture_properties.get("elasticity", 0.5)
                                + ingredient.texture_properties.get("firmness", 0.5)
                            )
                            / 2
                        )
                        total_weight += proportion

        return texture_score / total_weight if total_weight > 0 else 0.5

    def _evaluate_cost(self, formulation: DoughFormulation) -> float:
        """Evaluar costo de la formulación"""
        # Calcular score de costo (menor costo = mayor score)
        max_cost = 100.0  # Costo máximo aceptable
        cost_score = 1.0 - (formulation.cost / max_cost)
        return max(0.0, min(1.0, cost_score))

    def _evaluate_sustainability(self, formulation: DoughFormulation) -> float:
        """Evaluar sostenibilidad de la formulación"""
        return formulation.sustainability_score

    def _evaluate_scalability(self, formulation: DoughFormulation) -> float:
        """Evaluar escalabilidad de la formulación"""
        # Calcular score de escalabilidad basado en disponibilidad de ingredientes
        scalability_score = 0.0
        total_weight = 0.0

        for ingredient_dict in formulation.ingredients:
            for name, proportion in ingredient_dict.items():
                # Buscar el ingrediente en la base de datos
                for category in self.ingredients_db.values():
                    if name in category:
                        ingredient = category[name]
                        # Considerar disponibilidad y costos
                        scalability_score += (
                            proportion
                            * (
                                ingredient.availability
                                + (1.0 - ingredient.cost / 100.0)  # Normalizar costo
                            )
                            / 2
                        )
                        total_weight += proportion

        return scalability_score / total_weight if total_weight > 0 else 0.5

    def _evaluate_commercial_viability(self, formulation: DoughFormulation) -> float:
        """Evaluar viabilidad comercial de la formulación"""
        # Calcular score de viabilidad comercial basado en múltiples factores
        viability_score = 0.0
        total_weight = 0.0

        for ingredient_dict in formulation.ingredients:
            for name, proportion in ingredient_dict.items():
                # Buscar el ingrediente en la base de datos
                for category in self.ingredients_db.values():
                    if name in category:
                        ingredient = category[name]
                        # Considerar costo, disponibilidad y sostenibilidad
                        viability_score += (
                            proportion
                            * (
                                (1.0 - ingredient.cost / 100.0)  # Normalizar costo
                                + ingredient.availability
                                + ingredient.sustainability_score
                            )
                            / 3
                        )
                        total_weight += proportion

        return viability_score / total_weight if total_weight > 0 else 0.5

    def _calculate_nutritional_score(self, nutrients: Dict[str, float]) -> float:
        """Calcula el puntaje nutricional basado en los nutrientes."""
        score = 0.0
        for nutrient, value in nutrients.items():
            if nutrient in self.nutrient_weights:
                score += value * self.nutrient_weights[nutrient]
        return score
