import logging
import json
import os
import random
from datetime import datetime
from pathlib import Path
from config import DATA_DIR

class MockLanguageProcessor:
    """Versión simulada del procesador de lenguaje natural para ambientes sin acceso a APIs."""
    
    def __init__(self):
        """Inicializa el procesador de lenguaje natural simulado."""
        self.logger = logging.getLogger("mock-nlp")
        self.logger.info("Procesador de lenguaje natural simulado inicializado (modo MOCK)")
        
        # Cargar plantillas de recetas para simulación
        self._templates = self._load_templates()
    
    def _load_templates(self):
        """Carga plantillas de recetas para simulación."""
        templates = [
            {
                "nombre": "Pizza Margherita",
                "ingredientes": "300g harina, 175ml agua, 7g levadura, 5g sal, 20ml aceite de oliva, 150g salsa de tomate, 200g mozzarella, albahaca fresca",
                "instrucciones": "1. Mezclar harina, agua, levadura, sal y aceite. Amasar por 10 minutos.\n2. Dejar reposar la masa por 2 horas.\n3. Estirar la masa y agregar salsa de tomate y mozzarella.\n4. Hornear a 250°C por 10 minutos.\n5. Decorar con albahaca fresca."
            },
            {
                "nombre": "Pizza Vegetariana",
                "ingredientes": "300g harina, 175ml agua, 7g levadura, 5g sal, 20ml aceite de oliva, 150g salsa de tomate, 150g mozzarella, 50g pimiento, 50g cebolla, 50g champiñones, 50g aceitunas",
                "instrucciones": "1. Mezclar harina, agua, levadura, sal y aceite. Amasar por 10 minutos.\n2. Dejar reposar la masa por 2 horas.\n3. Estirar la masa y agregar salsa de tomate y mozzarella.\n4. Agregar los vegetales: pimiento, cebolla, champiñones y aceitunas.\n5. Hornear a 250°C por 12 minutos."
            },
            {
                "nombre": "Pizza Mediterránea",
                "ingredientes": "300g harina, 175ml agua, 7g levadura, 5g sal, 30ml aceite de oliva, 100g tomates cherry, 150g mozzarella, 50g queso feta, 30g aceitunas negras, orégano, romero",
                "instrucciones": "1. Mezclar harina, agua, levadura, sal y aceite. Amasar por 10 minutos.\n2. Dejar reposar la masa por 2 horas.\n3. Estirar la masa y agregar aceite de oliva y tomates cherry.\n4. Agregar mozzarella, queso feta y aceitunas.\n5. Espolvorear orégano y romero.\n6. Hornear a 230°C por 12 minutos."
            }
        ]
        return templates
    
    def process_request(self, text):
        """
        Simula el procesamiento de una solicitud en lenguaje natural.
        
        Args:
            text (str): Texto de entrada con la solicitud
            
        Returns:
            dict: Resultado simulado con una receta
        """
        self.logger.info(f"Procesando solicitud: '{text[:50]}...' (SIMULADO)")
        
        # Elegir una plantilla aleatoria
        template = random.choice(self._templates)
        
        # Generar ID único para la receta
        recipe_id = f"mock-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Crear respuesta
        response = {
            "id": recipe_id,
            "nombre": template["nombre"],
            "ingredientes": template["ingredientes"],
            "instrucciones": template["instrucciones"],
            "success": True,
            "message": "Receta generada exitosamente (SIMULADA)",
            "query_analysis": {
                "intención": "generar_receta",
                "tipo_masa": "tradicional",
                "ingredientes_detectados": ["harina", "agua", "levadura", "sal", "aceite"],
                "estilo_detectado": "italiano"
            }
        }
        
        # Añadir variaciones basadas en el texto de entrada
        if "vegana" in text.lower() or "vegetariana" in text.lower():
            response["nombre"] += " Vegana"
            response["query_analysis"]["tipo_dieta"] = "vegana"
        
        if "sin gluten" in text.lower():
            response["nombre"] += " Sin Gluten"
            response["ingredientes"] = response["ingredientes"].replace("harina", "harina sin gluten")
            response["query_analysis"]["restricciones"] = ["sin_gluten"]
        
        return response
    
    def analyze_pizza_description(self, description):
        """
        Simula el análisis de una descripción de pizza.
        
        Args:
            description (str): Descripción de la pizza
            
        Returns:
            dict: Resultado simulado del análisis
        """
        self.logger.info(f"Analizando descripción: '{description[:50]}...' (SIMULADO)")
        
        # Simular análisis
        analysis = {
            "ingredientes_detectados": ["harina", "agua", "levadura", "sal"],
            "técnicas_detectadas": ["amasado", "fermentación", "horneado"],
            "estilo_detectado": "napolitano",
            "tiempo_estimado": 120,
            "dificultad_estimada": "media",
            "confianza": 0.85
        }
        
        # Añadir variaciones basadas en el texto de entrada
        if "vegana" in description.lower():
            analysis["ingredientes_detectados"].extend(["tofu", "levadura nutricional"])
            analysis["estilo_detectado"] = "vegano"
        
        if "rápida" in description.lower() or "express" in description.lower():
            analysis["tiempo_estimado"] = 45
            analysis["técnicas_detectadas"].append("fermentación_rápida")
        
        return analysis
    
    def generate_explanation(self, recipe_data):
        """
        Genera una explicación simulada para una receta.
        
        Args:
            recipe_data (dict): Datos de la receta
            
        Returns:
            str: Explicación simulada
        """
        name = recipe_data.get("nombre", "esta receta")
        return f"Esta es una explicación simulada para {name}. La receta utiliza técnicas tradicionales de preparación de pizza, con un enfoque en ingredientes de calidad y métodos de cocción que resaltan los sabores naturales." 