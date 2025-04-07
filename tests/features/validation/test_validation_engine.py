#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para el motor de validación.
"""

import os
import json
import tempfile
import unittest
from pathlib import Path
from src.features.validation.validation_engine import (
    ValidationEngine,
    ValidationResult,
    quick_validate_recipe,
    check_system_integrity
)

class TestValidationEngine(unittest.TestCase):
    """Pruebas para el motor de validación."""

    def setUp(self):
        """Configuración para las pruebas."""
        # Crear directorio temporal para pruebas
        self.temp_dir = tempfile.mkdtemp()
        
        # Crear una receta válida para pruebas
        self.valid_recipe = {
            "harina": 1000,
            "agua": 600,
            "sal": 20,
            "levadura": 10,
            "aceite_oliva": 30
        }
        
        # Crear una receta inválida para pruebas
        self.invalid_recipe = {
            "harina": 1000,
            "agua": 400,  # Hidratación muy baja
            "sal": 50,    # Sal excesiva
            "levadura": 0  # Sin levadura
        }
        
        # Inicializar motor de validación
        self.engine = ValidationEngine()

    def tearDown(self):
        """Limpieza después de las pruebas."""
        # Eliminar archivos temporales
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_validate_recipe(self):
        """Prueba la validación de recetas."""
        # Probar receta válida
        results = self.engine.validate_recipe(self.valid_recipe, "pizza", "individual")
        self.assertTrue(all(r.is_valid for r in results if r.severity == "critical"))
        
        # Probar receta inválida
        results = self.engine.validate_recipe(self.invalid_recipe, "pizza", "individual")
        invalid_results = [r for r in results if not r.is_valid]
        self.assertTrue(len(invalid_results) >= 3)  # Al menos 3 reglas deben fallar

    def test_validate_recipe_from_file(self):
        """Prueba la validación de recetas desde archivo."""
        # Crear archivo temporal con receta válida
        valid_file = os.path.join(self.temp_dir, "valid_recipe.json")
        with open(valid_file, 'w') as f:
            json.dump(self.valid_recipe, f)
        
        # Probar receta válida desde archivo
        recipe, results = self.engine.validate_recipe_from_file(valid_file, "pizza", "individual")
        self.assertEqual(len(recipe), len(self.valid_recipe))
        self.assertTrue(all(r.is_valid for r in results if r.severity == "critical"))
        
        # Crear archivo temporal con receta inválida
        invalid_file = os.path.join(self.temp_dir, "invalid_recipe.json")
        with open(invalid_file, 'w') as f:
            json.dump(self.invalid_recipe, f)
        
        # Probar receta inválida desde archivo
        recipe, results = self.engine.validate_recipe_from_file(invalid_file, "pizza", "individual")
        invalid_results = [r for r in results if not r.is_valid]
        self.assertTrue(len(invalid_results) >= 3)  # Al menos 3 reglas deben fallar
        
        # Probar archivo inexistente
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.json")
        recipe, results = self.engine.validate_recipe_from_file(nonexistent_file, "pizza", "individual")
        self.assertEqual(len(recipe), 0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].rule_code, "FILE_ERROR")

    def test_summarize_results(self):
        """Prueba la generación de resúmenes de resultados."""
        # Crear resultados de prueba
        results = [
            ValidationResult("TEST_01", "Regla crítica 1", False, "critical", "Error 1", "Recomendación 1"),
            ValidationResult("TEST_02", "Regla crítica 2", True, "critical", None, None),
            ValidationResult("TEST_03", "Regla media 1", False, "medium", "Error 2", "Recomendación 2"),
            ValidationResult("TEST_04", "Regla media 2", True, "medium", None, None),
            ValidationResult("TEST_05", "Regla baja 1", False, "low", "Error 3", "Recomendación 3")
        ]
        
        # Generar resumen
        summary = self.engine.summarize_results(results)
        
        # Verificar resumen
        self.assertFalse(summary["is_viable"])  # No viable por regla crítica fallida
        self.assertEqual(summary["total_rules_checked"], 5)
        self.assertEqual(summary["total_issues"], 3)
        self.assertEqual(summary["issues_by_severity"]["critical"], 1)
        self.assertEqual(summary["issues_by_severity"]["medium"], 1)
        self.assertEqual(summary["issues_by_severity"]["low"], 1)
        self.assertEqual(len(summary["recommendations"]), 3)

    def test_export_results(self):
        """Prueba la exportación de resultados a archivo."""
        # Crear resultados de prueba
        results = [
            ValidationResult("TEST_01", "Regla crítica 1", False, "critical", "Error 1", "Recomendación 1"),
            ValidationResult("TEST_02", "Regla crítica 2", True, "critical", None, None)
        ]
        
        # Exportar resultados
        output_file = os.path.join(self.temp_dir, "results.json")
        success = self.engine.export_results(results, output_file)
        
        # Verificar exportación
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))
        
        # Verificar contenido del archivo
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("validation_results", data)
        self.assertIn("summary", data)
        self.assertEqual(len(data["validation_results"]), 2)

    def test_quick_validate_recipe(self):
        """Prueba la función rápida de validación."""
        # Crear archivo temporal con receta válida
        valid_file = os.path.join(self.temp_dir, "valid_recipe.json")
        with open(valid_file, 'w') as f:
            json.dump(self.valid_recipe, f)
        
        # Probar función rápida
        output_file = os.path.join(self.temp_dir, "quick_results.json")
        summary = quick_validate_recipe(valid_file, "pizza", "individual", output_file)
        
        # Verificar resultados
        self.assertIn("is_viable", summary)
        self.assertIn("total_rules_checked", summary)
        self.assertTrue(os.path.exists(output_file))

    def test_check_system_integrity(self):
        """Prueba la verificación de integridad del sistema."""
        result = check_system_integrity()
        
        # Verificar resultado
        self.assertEqual(result["status"], "OK")
        self.assertIn("rules_count", result)
        self.assertIn("rules_by_severity", result)
        self.assertIn("ingredient_limits_count", result)
        self.assertIn("process_params_count", result)
        self.assertIn("directories_ready", result)

if __name__ == "__main__":
    unittest.main() 