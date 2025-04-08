"""
Procesador de lenguaje natural para interpretar recetas a partir de descripciones.
"""

class LanguageProcessor:
    """Procesador de lenguaje natural para recetas."""
    
    def __init__(self):
        """Inicializa el procesador de lenguaje natural."""
        # En el MVP, usamos una implementación simplificada
        self.keywords = {
            "pizza_types": ["margarita", "napolitana", "pepperoni", "hawaiana", "vegana", "cuatro quesos", "barbacoa", "marinera"],
            "dough_types": ["delgada", "gruesa", "crujiente", "suave", "integral", "artesanal", "tradicional", "nueva york", "estilo chicago"],
            "sizes": ["personal", "mediana", "familiar", "industrial", "grande", "pequeña", "individual", "extra grande"],
            "restrictions": ["sin gluten", "vegana", "keto", "baja en sodio", "sin lácteos", "sin huevo", "sin azúcar"],
            "colors": ["blanca", "roja", "verde", "integral", "negra", "dorada"],
            "cooking_methods": ["horno de leña", "horno eléctrico", "sartén", "plancha", "parrilla"]
        }
        
        # Palabras clave adicionales para detectar requisitos específicos
        self.gluten_free_keywords = [
            "sin gluten", "gluten free", "celíaco", "celiaco", "celíaca", "celiaca", 
            "intolerancia al gluten", "sensibilidad al gluten"
        ]
        
        # Propiedades deseadas para masas sin gluten
        self.gluten_free_properties = {
            "elasticidad": ["elástica", "elástico", "que se estire", "flexible", "maleable"],
            "crujiente": ["crujiente", "crocante", "crunch", "con corteza dura", "corteza crujiente"],
            "suave": ["suave", "tierna", "tierno", "blanda", "blando", "esponjosa", "esponjoso"],
            "ligera": ["ligera", "ligero", "liviana", "liviano", "no pesada", "fácil de digerir"]
        }
    
    def process_request(self, text):
        """
        Procesa una solicitud en lenguaje natural.
        
        Args:
            text: Texto de la solicitud
            
        Returns:
            Diccionario con las propiedades detectadas y la receta generada
        """
        # Versión mejorada
        text = text.lower()
        
        # Detectar propiedades básicas
        properties = {
            "pizza_type": next((t for t in self.keywords["pizza_types"] if t in text), None),
            "dough_type": next((t for t in self.keywords["dough_types"] if t in text), None),
            "size": next((s for s in self.keywords["sizes"] if s in text), "mediana"),
            "restrictions": [r for r in self.keywords["restrictions"] if r in text],
            "color": next((c for c in self.keywords["colors"] if c in text), None),
            "cooking_method": next((m for m in self.keywords["cooking_methods"] if m in text), None)
        }
        
        # Detectar si es sin gluten con más profundidad
        is_gluten_free = any(keyword in text for keyword in self.gluten_free_keywords)
        if is_gluten_free and "sin gluten" not in properties["restrictions"]:
            properties["restrictions"].append("sin gluten")
        
        # Detectar propiedades deseadas para masas sin gluten
        if "sin gluten" in properties["restrictions"]:
            gluten_free_desired_properties = {}
            for prop, keywords in self.gluten_free_properties.items():
                if any(keyword in text for keyword in keywords):
                    gluten_free_desired_properties[prop] = True
            
            if gluten_free_desired_properties:
                properties["gluten_free_properties"] = gluten_free_desired_properties
        
        # Generar una receta adaptada a las propiedades
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
        # Implementación mejorada
        recipe = {
            "name": f"Masa para pizza {properties['pizza_type'] or 'básica'}",
            "ingredients": {
                "harina": 1000  # g
            },
            "instructions": []
        }
        
        # Ajustar ingredientes según restricciones
        if "sin gluten" in properties["restrictions"]:
            # Proporciones base para masa sin gluten
            recipe["ingredients"] = {}
            
            # Ajustar según propiedades deseadas para masa sin gluten
            if "gluten_free_properties" in properties:
                gf_props = properties["gluten_free_properties"]
                
                if gf_props.get("elasticidad"):
                    # Más goma xantana para elasticidad
                    recipe["ingredients"] = {
                        "harina de arroz": 600,  # g
                        "almidón de maíz": 300,  # g
                        "harina de almendra": 100,  # g
                        "goma xantana": 25       # g
                    }
                elif gf_props.get("crujiente"):
                    # Más almidón para crujiente
                    recipe["ingredients"] = {
                        "harina de arroz": 500,  # g
                        "almidón de maíz": 400,  # g
                        "fécula de patata": 100,  # g
                        "goma xantana": 15       # g
                    }
                elif gf_props.get("suave"):
                    # Más variedad de harinas para suavidad
                    recipe["ingredients"] = {
                        "harina de arroz": 400,  # g
                        "almidón de maíz": 250,  # g
                        "harina de mijo": 150,  # g
                        "almidón de patata": 200,  # g
                        "goma xantana": 18       # g
                    }
                elif gf_props.get("ligera"):
                    # Más proteína para estructura más ligera
                    recipe["ingredients"] = {
                        "harina de arroz": 550,  # g
                        "almidón de maíz": 250,  # g
                        "harina de quinoa": 150,  # g
                        "psyllium husk": 50,  # g
                        "goma xantana": 15       # g
                    }
                else:
                    # Receta equilibrada sin propiedades específicas
                    recipe["ingredients"] = {
                        "harina de arroz": 650,  # g
                        "almidón de maíz": 300,  # g
                        "harina de garbanzo": 50,  # g
                        "goma xantana": 20       # g
                    }
            else:
                # Receta por defecto sin gluten
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
        
        # Ajustar instrucciones para sin gluten
        if "sin gluten" in properties["restrictions"]:
            recipe["instructions"] = [
                "Mezclar todos los ingredientes secos en un recipiente grande.",
                "Disolver la levadura en agua tibia.",
                "Incorporar lentamente el agua con levadura a la mezcla de harinas.",
                "Añadir el aceite de oliva y amasar durante 5-7 minutos hasta formar una masa homogénea.",
                "La masa sin gluten será más pegajosa que la tradicional, esto es normal.",
                "Dejar reposar tapado por 45-60 minutos.",
                "Manipular la masa con las manos ligeramente humedecidas para evitar que se pegue."
            ]
        
        return recipe