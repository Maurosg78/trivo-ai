import os
import json
import unittest
from unittest.mock import patch, mock_open

import pytest
from pydantic import BaseModel

from src.core.models.dough_formulator import DoughFormulator, DoughFormulation, Ingredient


class TestDoughFormulator(unittest.TestCase):
    def setUp(self):
        """Configurar recursos para las pruebas."""
        # Mock de datos de ingredientes
        self.mock_ingredients_data = {
            "flours": {
                "wheat_flour": {
                    "name": "wheat_flour",
                    "color": "cream",
                    "nutritional_value": {
                        "protein": 10.0,
                        "fiber": 2.7,
                        "fat": 1.2,
                        "carbohydrates": 76.3
                    },
                    "cost": 1.5,
                    "availability": 0.9,
                    "sustainability_score": 0.7,
                    "texture_properties": {
                        "elasticity": 0.8,
                        "firmness": 0.6,
                        "moisture": 0.4
                    }
                },
                "chickpea_flour": {
                    "name": "chickpea_flour",
                    "color": "beige",
                    "nutritional_value": {
                        "protein": 22.0,
                        "fiber": 10.0,
                        "fat": 6.0,
                        "carbohydrates": 58.0
                    },
                    "cost": 3.0,
                    "availability": 0.7,
                    "sustainability_score": 0.85,
                    "texture_properties": {
                        "elasticity": 0.5,
                        "firmness": 0.7,
                        "moisture": 0.3
                    }
                }
            }
        }

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("os.path.join")
    def test_init_and_load_ingredients(self, mock_join, mock_json_load, mock_file_open):
        """Prueba la inicialización y carga de ingredientes."""
        # Configurar mocks
        mock_join.return_value = "mocked/path/to/ingredients.json"
        mock_json_load.return_value = self.mock_ingredients_data

        # Crear instancia
        formulator = DoughFormulator()
        
        # Verificar que se intentó abrir el archivo
        mock_file_open.assert_called_once_with("mocked/path/to/ingredients.json", "r", encoding="utf-8")
        
        # Verificar que se cargaron los ingredientes
        assert "flours" in formulator.ingredients_db
        assert "wheat_flour" in formulator.ingredients_db["flours"]
        assert isinstance(formulator.ingredients_db["flours"]["wheat_flour"], Ingredient)
        assert formulator.ingredients_db["flours"]["wheat_flour"].nutritional_value["protein"] == 10.0

    @patch("builtins.open", side_effect=Exception("Error al abrir archivo"))
    @patch("os.path.join")
    def test_load_ingredients_fallback(self, mock_join, mock_file_open):
        """Prueba la carga de ingredientes de respaldo cuando ocurre un error."""
        # Configurar mocks
        mock_join.return_value = "mocked/path/to/ingredients.json"
        
        # Crear instancia
        formulator = DoughFormulator()
        
        # Verificar que se intentó abrir el archivo
        mock_file_open.assert_called_once()
        
        # Verificar que se cargaron los ingredientes de respaldo
        assert "vegetables" in formulator.ingredients_db
        assert "beetroot" in formulator.ingredients_db["vegetables"]
        assert isinstance(formulator.ingredients_db["vegetables"]["beetroot"], Ingredient)

    @patch.object(DoughFormulator, "load_ingredients")
    @patch.object(DoughFormulator, "evaluate_formulation")
    def test_optimize_formulation(self, mock_evaluate, mock_load):
        """Prueba la optimización de la formulación."""
        # Configurar mocks
        mock_evaluate.return_value = {"total_score": 0.8}
        
        # Crear instancia y configurar su base de datos
        formulator = DoughFormulator()
        formulator.ingredients_db = {
            "flours": {
                "wheat_flour": Ingredient(
                    name="wheat_flour",
                    color="cream",
                    nutritional_value={
                        "protein": 10.0,
                        "fiber": 2.7,
                        "fat": 1.2,
                        "carbohydrates": 76.3
                    },
                    cost=1.5,
                    availability=0.9,
                    sustainability_score=0.7,
                    texture_properties={
                        "elasticity": 0.8,
                        "firmness": 0.6,
                        "moisture": 0.4
                    }
                )
            }
        }
        
        # Llamar al método
        target_properties = {"protein": 12.0, "fiber": 3.0}
        formulation = formulator.optimize_formulation(target_properties)
        
        # Verificar resultado
        assert isinstance(formulation, DoughFormulation)
        assert formulation.target_properties == target_properties
        assert formulation.ingredients
        assert mock_evaluate.called

    @patch.object(DoughFormulator, "load_ingredients")
    def test_evaluate_formulation(self, mock_load):
        """Prueba la evaluación de una formulación."""
        # Crear instancia y configurar su base de datos
        formulator = DoughFormulator()
        formulator.ingredients_db = {
            "flours": {
                "wheat_flour": Ingredient(
                    name="wheat_flour",
                    color="cream",
                    nutritional_value={
                        "protein": 10.0,
                        "fiber": 2.7,
                        "fat": 1.2,
                        "carbohydrates": 76.3
                    },
                    cost=1.5,
                    availability=0.9,
                    sustainability_score=0.7,
                    texture_properties={
                        "elasticity": 0.8,
                        "firmness": 0.6,
                        "moisture": 0.4
                    }
                )
            }
        }
        
        # Crear formulación de prueba
        formulation = DoughFormulation(
            ingredients=[{"wheat_flour": 0.8}],
            target_properties={"protein": 12.0},
            nutritional_profile={"protein": 8.0},
            cost=1.2,
            sustainability_score=0.6
        )
        
        # Llamar al método
        evaluation = formulator.evaluate_formulation(formulation)
        
        # Verificar resultado
        assert isinstance(evaluation, dict)
        assert "taste_score" in evaluation
        assert "texture_score" in evaluation
        assert "total_score" in evaluation
        assert 0 <= evaluation["total_score"] <= 1.0

    @patch.object(DoughFormulator, "load_ingredients")
    def test_calculate_initial_proportions(self, mock_load):
        """Prueba el cálculo de proporciones iniciales."""
        # Crear instancia
        formulator = DoughFormulator()
        
        # Crear ingrediente de prueba
        ingredient = Ingredient(
            name="wheat_flour",
            color="cream",
            nutritional_value={
                "protein": 10.0,
                "fiber": 2.7,
                "fat": 1.2,
                "carbohydrates": 76.3
            },
            cost=1.5,
            availability=0.9,
            sustainability_score=0.7,
            texture_properties={
                "elasticity": 0.8,
                "firmness": 0.6,
                "moisture": 0.4
            }
        )
        
        # Llamar al método
        target_props = {"protein": 12.0, "fiber": 3.0}
        proportions = formulator._calculate_initial_proportions(ingredient, target_props)
        
        # Verificar resultado
        assert isinstance(proportions, list)
        assert len(proportions) > 0
        assert all(0 <= p <= 1.0 for p in proportions)
        assert sum(proportions) > 0

    @patch.object(DoughFormulator, "load_ingredients")
    def test_calculate_nutritional_profile(self, mock_load):
        """Prueba el cálculo del perfil nutricional."""
        # Crear instancia
        formulator = DoughFormulator()
        
        # Crear ingrediente de prueba
        ingredient = Ingredient(
            name="wheat_flour",
            color="cream",
            nutritional_value={
                "protein": 10.0,
                "fiber": 2.7
            },
            cost=1.5,
            availability=0.9,
            sustainability_score=0.7,
            texture_properties={
                "elasticity": 0.8,
                "firmness": 0.6
            }
        )
        
        # Llamar al método
        proportions = [0.5, 0.3]
        profile = formulator._calculate_nutritional_profile(proportions, ingredient)
        
        # Verificar resultado
        assert isinstance(profile, dict)
        assert "protein" in profile
        assert "fiber" in profile
        assert profile["protein"] == 10.0 * 0.8  # sum of proportions is 0.8
        assert profile["fiber"] == 2.7 * 0.8

    @patch.object(DoughFormulator, "load_ingredients")
    def test_calculate_cost(self, mock_load):
        """Prueba el cálculo del costo de la formulación."""
        # Crear instancia
        formulator = DoughFormulator()
        
        # Crear ingrediente de prueba
        ingredient = Ingredient(
            name="wheat_flour",
            color="cream",
            nutritional_value={"protein": 10.0},
            cost=1.5,
            availability=0.9,
            sustainability_score=0.7,
            texture_properties={"elasticity": 0.8}
        )
        
        # Llamar al método
        proportions = [0.5, 0.3]
        cost = formulator._calculate_cost(proportions, ingredient)
        
        # Verificar resultado
        assert cost == 1.5 * 0.8  # cost * sum of proportions

    @patch.object(DoughFormulator, "load_ingredients")
    def test_calculate_sustainability(self, mock_load):
        """Prueba el cálculo del score de sostenibilidad."""
        # Crear instancia
        formulator = DoughFormulator()
        
        # Crear ingrediente de prueba
        ingredient = Ingredient(
            name="wheat_flour",
            color="cream",
            nutritional_value={"protein": 10.0},
            cost=1.5,
            availability=0.9,
            sustainability_score=0.7,
            texture_properties={"elasticity": 0.8}
        )
        
        # Llamar al método
        proportions = [0.5, 0.3]
        score = formulator._calculate_sustainability(proportions, ingredient)
        
        # Verificar resultado
        assert score == 0.7 * 0.8  # sustainability_score * sum of proportions
        
    @patch.object(DoughFormulator, "load_ingredients")
    @patch.object(DoughFormulator, "evaluate_formulation")
    def test_evaluate_formulation_score(self, mock_evaluate, mock_load):
        """Prueba el cálculo del score general de la formulación."""
        # Configurar mock
        mock_evaluate.return_value = {"total_score": 0.75}
        
        # Crear instancia
        formulator = DoughFormulator()
        
        # Crear formulación de prueba
        formulation = DoughFormulation(
            ingredients=[{"wheat_flour": 0.8}],
            target_properties={"protein": 12.0},
            nutritional_profile={"protein": 8.0},
            cost=1.2,
            sustainability_score=0.6
        )
        
        # Llamar al método
        score = formulator._evaluate_formulation_score(formulation)
        
        # Verificar resultado
        assert score == 0.75
        mock_evaluate.assert_called_once_with(formulation) 