"""
Procesador de lenguaje natural para interpretar recetas a partir de descripciones.
"""

class LanguageProcessor:
    """Procesador de lenguaje natural para recetas."""
    
    def __init__(self):
        """Inicializa el procesador de lenguaje natural."""
        # En el MVP, usamos una implementación simplificada
        self.keywords = {
            "pizza_types": ["margarita", "napolitana", "pepperoni", "hawaiana", "vegana"],
            "dough_types": ["delgada", "gruesa", "crujiente", "suave", "integral"],
            "sizes": ["personal", "mediana", "familiar", "industrial"],
            "restrictions": ["sin gluten", "vegana", "keto", "baja en sodio"],
            "colors": ["blanca", "roja", "verde", "integral"]
        }
    
    def process_request(self, text):
        """
        Procesa una solicitud en lenguaje natural.
        
        Args:
            text: Texto de la solicitud
            
        Returns:
            Diccionario con las propiedades detectadas y la receta generada
        """
        # Versión simplificada para el MVP
        text = text.lower()
        
        # Detectar propiedades
        properties = {
            "pizza_type": next((t for t in self.keywords["pizza_types"] if t in text), None),
            "dough_type": next((t for t in self.keywords["dough_types"] if t in text), None),
            "size": next((s for s in self.keywords["sizes"] if s in text), "mediana"),
            "restrictions": [r for r in self.keywords["restrictions"] if r in text],
            "color": next((c for c in self.keywords["colors"] if c in text), None)
        }
        
        # Generar una receta básica basada en las propiedades
        recipe = self._generate_recipe(properties)
        
        return {
            "properties": properties,
            "recipe": recipe,
            "status": "success"
        }
    
    def _generate_recipe(self, properties):
        """
        Genera una receta basada en las propiedades detectadas.
        
        Args:
            properties: Diccionario con propiedades detectadas
            
        Returns:
            Diccionario con la receta generada
        """
        # Implementación simplificada para el MVP
        recipe = {
            "name": f"Masa para pizza {properties['pizza_type'] or 'básica'}",
            "ingredients": {
                "harina": 1000  # g
            },
            "instructions": []
        }
        
        # Ajustar ingredientes según tipo
        if "sin gluten" in properties["restrictions"]:
            recipe["ingredients"] = {
                "harina de arroz": 700,  # g
                "almidón de maíz": 300,  # g
                "goma xantana": 20       # g
            }
        
        # Ajustar hidratación según tipo de masa
        if properties["dough_type"] == "delgada":
            recipe["ingredients"]["agua"] = 550  # ml
        elif properties["dough_type"] == "gruesa":
            recipe["ingredients"]["agua"] = 700  # ml
        else:
            recipe["ingredients"]["agua"] = 650  # ml
        
        # Agregar ingredientes básicos
        recipe["ingredients"]["sal"] = 20        # g
        recipe["ingredients"]["levadura"] = 10   # g
        recipe["ingredients"]["aceite de oliva"] = 30  # ml
        
        # Generar instrucciones básicas
        recipe["instructions"] = [
            "Mezclar la harina y la sal en un recipiente grande.",
            "Disolver la levadura en agua tibia.",
            "Incorporar el agua con levadura a la mezcla de harina.",
            "Amasar durante 10 minutos hasta obtener una masa elástica.",
            "Dejar reposar tapado por 1 hora o hasta que duplique su volumen.",
            "Dividir y formar según el uso deseado."
        ]
        
        return recipe