#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para el módulo de reglas de validación.
"""

import os
import unittest
from src.features.validation.validation_rules import (
    ValidationRule,
    HydrationRatioRule,
    SaltRatioRule,
    YeastRatioRule,
    SpecialtyDoughIngredientsRule,
    ScaleLimitsRule,
    FermentationParametersRule,
    get_validation_rules,
    get_rule_by_code
)

class TestValidationRules(unittest.TestCase):
    """Pruebas para las reglas de validación."""

    def test_hydration_ratio_rule(self):
        """Prueba la regla de ratio de hidratación."""
        rule = HydrationRatioRule()
        
        # Caso válido: hidratación óptima
        recipe_ok = {"harina": 1000, "agua": 600}
        is_valid, _, _ = rule.validate(recipe_ok, "pizza", "individual")
        self.assertTrue(is_valid)
        
        # Caso inválido: hidratación demasiado baja
        recipe_low = {"harina": 1000, "agua": 400}
        is_valid, error, recommendation = rule.validate(recipe_low, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("demasiado baja", error)
        
        # Caso inválido: hidratación demasiado alta
        recipe_high = {"harina": 1000, "agua": 800}
        is_valid, error, recommendation = rule.validate(recipe_high, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("demasiado alta", error)
        
        # Caso borde: sin harina
        recipe_no_flour = {"agua": 600}
        is_valid, error, _ = rule.validate(recipe_no_flour, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("No se encontró harina", error)

    def test_salt_ratio_rule(self):
        """Prueba la regla de proporción de sal."""
        rule = SaltRatioRule()
        
        # Caso válido: proporción de sal óptima
        recipe_ok = {"harina": 1000, "sal": 20}
        is_valid, _, _ = rule.validate(recipe_ok, "pizza", "individual")
        self.assertTrue(is_valid)
        
        # Caso inválido: proporción de sal demasiado baja
        recipe_low = {"harina": 1000, "sal": 10}
        is_valid, error, _ = rule.validate(recipe_low, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("demasiado baja", error)
        
        # Caso inválido: proporción de sal demasiado alta
        recipe_high = {"harina": 1000, "sal": 40}
        is_valid, error, _ = rule.validate(recipe_high, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("demasiado alta", error)
        
        # Caso borde: sin sal
        recipe_no_salt = {"harina": 1000}
        is_valid, error, _ = rule.validate(recipe_no_salt, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("No se encontró sal", error)

    def test_yeast_ratio_rule(self):
        """Prueba la regla de proporción de levadura."""
        rule = YeastRatioRule()
        
        # Caso válido: proporción de levadura óptima
        recipe_ok = {"harina": 1000, "levadura": 10}
        is_valid, _, _ = rule.validate(recipe_ok, "pizza", "individual")
        self.assertTrue(is_valid)
        
        # Caso válido: usando masa madre en lugar de levadura
        recipe_sourdough = {"harina": 1000, "masa_madre": 200}
        is_valid, _, _ = rule.validate(recipe_sourdough, "pan", "individual")
        self.assertTrue(is_valid)
        
        # Caso inválido: proporción de levadura demasiado alta
        recipe_high = {"harina": 1000, "levadura": 30}
        is_valid, error, _ = rule.validate(recipe_high, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("demasiado alta", error)
        
        # Caso inválido: sin levadura ni masa madre
        recipe_no_yeast = {"harina": 1000}
        is_valid, error, _ = rule.validate(recipe_no_yeast, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("No se encontró levadura ni masa madre", error)

    def test_specialty_dough_ingredients_rule(self):
        """Prueba la regla de ingredientes esenciales para masas especiales."""
        rule = SpecialtyDoughIngredientsRule()
        
        # Caso válido: brioche con todos los ingredientes
        recipe_brioche_ok = {
            "harina": 1000, 
            "huevo": 200, 
            "mantequilla": 200, 
            "azucar": 100, 
            "leche": 300
        }
        is_valid, _, _ = rule.validate(recipe_brioche_ok, "brioche", "individual")
        self.assertTrue(is_valid)
        
        # Caso inválido: brioche sin mantequilla
        recipe_brioche_missing = {
            "harina": 1000, 
            "huevo": 200, 
            "azucar": 100, 
            "leche": 300
        }
        is_valid, error, _ = rule.validate(recipe_brioche_missing, "brioche", "individual")
        self.assertFalse(is_valid)
        self.assertIn("mantequilla", error)
        
        # Caso válido: pizza (no es una masa especial)
        recipe_pizza = {"harina": 1000, "agua": 600, "sal": 20, "levadura": 10}
        is_valid, _, _ = rule.validate(recipe_pizza, "pizza", "individual")
        self.assertTrue(is_valid)

    def test_scale_limits_rule(self):
        """Prueba la regla de límites de escala."""
        rule = ScaleLimitsRule()
        
        # Caso válido: dentro de los límites para escala individual
        recipe_individual_ok = {"harina": 1000, "agua": 600, "sal": 20, "levadura": 5}
        is_valid, _, _ = rule.validate(recipe_individual_ok, "pizza", "individual")
        self.assertTrue(is_valid)
        
        # Caso inválido: demasiado grande para escala individual
        recipe_individual_too_big = {
            "harina": 5000, "agua": 3000, "sal": 100, "levadura": 50
        }
        is_valid, error, _ = rule.validate(recipe_individual_too_big, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("excede el máximo", error)
        
        # Caso inválido: demasiado pequeño para escala industrial
        recipe_industrial_too_small = {
            "harina": 1000, "agua": 600, "sal": 20, "levadura": 5
        }
        is_valid, error, _ = rule.validate(recipe_industrial_too_small, "pizza", "industrial")
        self.assertFalse(is_valid)
        self.assertIn("inferior al mínimo", error)

    def test_fermentation_parameters_rule(self):
        """Prueba la regla de parámetros de fermentación."""
        rule = FermentationParametersRule()
        
        # Caso válido: parámetros óptimos para pizza napolitana
        recipe_ok = {
            "harina": 1000, 
            "agua": 600, 
            "temperatura_fermentacion": 20, 
            "tiempo_fermentacion": 24,
            "tipo_napolitana": True
        }
        is_valid, _, _ = rule.validate(recipe_ok, "pizza", "individual")
        self.assertTrue(is_valid)
        
        # Caso inválido: temperatura demasiado alta
        recipe_high_temp = {
            "harina": 1000, 
            "agua": 600, 
            "temperatura_fermentacion": 30, 
            "tiempo_fermentacion": 24,
            "tipo_napolitana": True
        }
        is_valid, error, _ = rule.validate(recipe_high_temp, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("Temperatura de fermentación demasiado alta", error)
        
        # Caso inválido: tiempo demasiado corto
        recipe_short_time = {
            "harina": 1000, 
            "agua": 600, 
            "temperatura_fermentacion": 20, 
            "tiempo_fermentacion": 4,
            "tipo_napolitana": True
        }
        is_valid, error, _ = rule.validate(recipe_short_time, "pizza", "individual")
        self.assertFalse(is_valid)
        self.assertIn("Tiempo de fermentación demasiado corto", error)
        
        # Caso válido: sin parámetros de fermentación (no se valida)
        recipe_no_params = {"harina": 1000, "agua": 600}
        is_valid, _, _ = rule.validate(recipe_no_params, "pizza", "individual")
        self.assertTrue(is_valid)

    def test_get_validation_rules(self):
        """Prueba la función get_validation_rules."""
        rules = get_validation_rules()
        self.assertTrue(len(rules) >= 6)
        
        rule_types = {type(rule) for rule in rules}
        self.assertIn(HydrationRatioRule, rule_types)
        self.assertIn(SaltRatioRule, rule_types)
        self.assertIn(YeastRatioRule, rule_types)
        self.assertIn(SpecialtyDoughIngredientsRule, rule_types)
        self.assertIn(ScaleLimitsRule, rule_types)
        self.assertIn(FermentationParametersRule, rule_types)

    def test_get_rule_by_code(self):
        """Prueba la función get_rule_by_code."""
        hydration_rule = get_rule_by_code("HYDRATION_01")
        self.assertIsInstance(hydration_rule, HydrationRatioRule)
        
        salt_rule = get_rule_by_code("SALT_01")
        self.assertIsInstance(salt_rule, SaltRatioRule)
        
        nonexistent_rule = get_rule_by_code("NONEXISTENT_RULE")
        self.assertIsNone(nonexistent_rule)

if __name__ == "__main__":
    unittest.main() 