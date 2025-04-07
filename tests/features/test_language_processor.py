#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pruebas para el procesador de lenguaje natural.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.features.nlp.language_processor import LanguageProcessor

class TestLanguageProcessor(unittest.TestCase):
    """
    Pruebas para el procesador de lenguaje natural que interpreta
    las solicitudes de recetas en lenguaje humano.
    """

    def setUp(self):
        """Inicializa el objeto LanguageProcessor para las pruebas."""
        self.processor = LanguageProcessor()

    def test_process_request_pizza(self):
        """Prueba que el procesador detecte correctamente una solicitud de pizza."""
        text = "Quiero una pizza napolitana familiar"
        result = self.processor.process_request(text)
        
        # Verificar que detecta el tipo y tamaño correctos
        self.assertEqual(result["recipe_type"], "pizza")
        self.assertEqual(result["extracted_information"]["size"], "grande")
        
        # Verificar que la receta base contiene los ingredientes esperados para pizza
        self.assertIn("harina", result["base_recipe"])
        self.assertIn("agua", result["base_recipe"])
        self.assertIn("levadura", result["base_recipe"])
        self.assertIn("sal", result["base_recipe"])

    def test_process_request_bread(self):
        """Prueba que el procesador detecte correctamente una solicitud de pan."""
        text = "Necesito una receta de pan integral con semillas"
        result = self.processor.process_request(text)
        
        # Verificar que detecta el tipo correcto
        self.assertEqual(result["recipe_type"], "pan")
        
        # Verificar que la receta base contiene los ingredientes esperados para pan
        self.assertIn("harina", result["base_recipe"])
        self.assertIn("agua", result["base_recipe"])
        self.assertIn("levadura", result["base_recipe"])
        self.assertIn("sal", result["base_recipe"])

    def test_process_request_dietary_restrictions(self):
        """Prueba que el procesador detecte correctamente restricciones dietéticas."""
        text = "Quiero una pizza sin gluten para celíacos"
        result = self.processor.process_request(text)
        
        # Verificar que detecta la restricción sin gluten
        self.assertIn("sin_gluten", result["extracted_information"]["restrictions"])
        
        # Verificar que la propiedad está marcada correctamente
        self.assertTrue(result["properties"]["es_sin_gluten"])

    def test_process_request_color(self):
        """Prueba que el procesador detecte correctamente colores mencionados."""
        text = "Quiero una masa de color verde con espinacas"
        result = self.processor.process_request(text)
        
        # Verificar que detecta el color verde
        self.assertIn("verde", result["extracted_information"]["colors"])
        
        # Verificar que la propiedad está marcada correctamente
        self.assertTrue(result["properties"]["colores"]["verde"])

    def test_process_request_nutritional(self):
        """Prueba que el procesador detecte correctamente propiedades nutricionales."""
        text = "Quiero una masa nutritiva y saludable"
        result = self.processor.process_request(text)
        
        # Verificar que detecta la propiedad nutricional
        self.assertTrue(result["extracted_information"]["nutritional"])
        
        # Verificar que la propiedad está marcada correctamente
        self.assertTrue(result["properties"]["es_nutricional"])

    # Nuevas pruebas para las masas especiales añadidas en el Sprint 4
    def test_process_request_brioche(self):
        """Prueba que el procesador detecte correctamente una solicitud de brioche."""
        text = "Necesito una receta de brioche para el desayuno"
        result = self.processor.process_request(text)
        
        # Verificar que detecta el tipo correcto
        self.assertEqual(result["recipe_type"], "brioche")
        
        # Verificar que la receta base contiene los ingredientes esperados para brioche
        self.assertIn("harina", result["base_recipe"])
        self.assertIn("mantequilla", result["base_recipe"])
        self.assertIn("huevo", result["base_recipe"])
        self.assertIn("azucar", result["base_recipe"])

    def test_process_request_croissant(self):
        """Prueba que el procesador detecte correctamente una solicitud de croissant."""
        text = "Quiero hacer croissants para el desayuno"
        result = self.processor.process_request(text)
        
        # Verificar que detecta el tipo correcto
        self.assertEqual(result["recipe_type"], "croissant")
        
        # Verificar que la receta base contiene los ingredientes esperados para croissant
        self.assertIn("harina_fuerza", result["base_recipe"])
        self.assertIn("mantequilla_laminado", result["base_recipe"])

    def test_process_request_pasta_fresca(self):
        """Prueba que el procesador detecte correctamente una solicitud de pasta fresca."""
        text = "Quiero preparar pasta fresca casera para tallarines"
        result = self.processor.process_request(text)
        
        # Verificar que detecta el tipo correcto
        self.assertEqual(result["recipe_type"], "pasta_fresca")
        
        # Verificar que la receta base contiene los ingredientes esperados para pasta
        self.assertIn("harina", result["base_recipe"])
        self.assertIn("huevo", result["base_recipe"])

    def test_process_request_specialty_with_color(self):
        """Prueba una solicitud compleja de masa especial con color y restricciones."""
        text = "Quiero hacer croissants integrales de color verde para el desayuno"
        result = self.processor.process_request(text)
        
        # Verificar que detecta el tipo correcto y color
        self.assertEqual(result["recipe_type"], "croissant")
        self.assertIn("verde", result["extracted_information"]["colors"])
        
        # Verificar ingredientes adicionales
        base_recipe = result["base_recipe"]
        # Debería contener algún ingrediente que aporte color verde
        verde_detectado = False
        for ingrediente in base_recipe.keys():
            if ingrediente in ["espinaca", "pure_espinaca"]:
                verde_detectado = True
                break
        
        self.assertTrue(verde_detectado, "No se detectó ingrediente para el color verde")

if __name__ == "__main__":
    unittest.main() 