#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para procesar solicitudes en lenguaje natural y traducirlas en parámetros técnicos
para la formulación de recetas.

Este módulo analiza el texto proporcionado por el usuario en lenguaje natural y extrae
información relevante como ingredientes deseados, restricciones dietéticas, características 
sensoriales y propósitos específicos.
"""

import re
import json
import os
from typing import Dict, Any, Tuple, List, Optional
import random


class LanguageProcessor:
    """
    Procesador de lenguaje natural para interpretar solicitudes de recetas.
    Esta implementación utiliza técnicas básicas de NLP sin depender de servicios externos.
    """
    
    def __init__(self):
        """Inicializa el procesador de lenguaje con patrones y conocimiento base."""
        # Tipos de recetas
        self.recipe_types = {
            "pizza": ["pizza", "napolitana", "margarita", "romana", "bbq", "barbacoa"],
            "pan": ["pan", "hogaza", "baguette", "chapata", "ciabatta", "bollo"],
            "flatbread": ["flatbread", "focaccia", "naan", "pita", "plano"],
            # Nuevos tipos de masas especiales
            "brioche": ["brioche", "pan brioche", "bollo suizo", "pan dulce"],
            "croissant": ["croissant", "cruasán", "croissants", "medialunas", "pain au chocolat"],
            "masa_filo": ["filo", "phyllo", "masa filo", "hojaldre fino"],
            "pasta_fresca": ["pasta", "pasta fresca", "fideos", "ravioli", "tallarines"],
            "masa_strudel": ["strudel", "masa strudel"],
            "kouign_amann": ["kouign amann", "kouign-amann", "pastel bretón"]
        }
        
        # Ingredientes por categoría
        self.ingredients = {
            "harinas": {
                "harina": ["harina", "harina de trigo", "00", "tipo 00", "trigo"],
                "harina_integral": ["integral", "trigo integral", "salvado"],
                "harina_de_arroz": ["arroz", "de arroz"],
                "harina_de_maíz": ["maíz", "maicena", "de maíz"],
                "almidón_de_maíz": ["almidón", "de patata", "fécula"],
                "harina_fuerza": ["harina de fuerza", "alta proteína", "harina fuerte", "proteica"],
                "semola_trigo_duro": ["sémola", "semolina", "trigo duro", "durum"]
            },
            "líquidos": {
                "agua": ["agua", "h2o"],
                "leche": ["leche", "leche vegetal", "leche de almendra"],
                "yogur": ["yogur", "yogurt", "kéfir"]
            },
            "grasas": {
                "aceite_de_oliva": ["aceite", "aove", "oliva", "aceite de oliva"],
                "mantequilla": ["mantequilla", "margarina"]
            },
            "fermentos": {
                "levadura": ["levadura", "levadura seca", "levadura fresca", "madre", "masa madre"],
                "bicarbonato": ["bicarbonato", "polvo de hornear"]
            },
            "otros": {
                "sal": ["sal", "sal marina"],
                "azúcar": ["azúcar", "miel", "sirope", "dulce"],
                "goma_xantana": ["xantana", "goma", "espesante"],
                "semillas_de_lino": ["lino", "linaza"],
                "semillas_de_chía": ["chía"],
                "semillas_de_girasol": ["girasol", "pipas"],
                "salvado": ["salvado", "fibra"],
                "remolacha": ["remolacha", "betabel", "rojo", "rojiza"],
                "espinaca": ["espinaca", "verde", "verdosa"],
                "carbón_activado": ["carbón", "negro", "negra", "oscura"]
            }
        }
        
        # Restricciones dietéticas
        self.dietary_restrictions = {
            "sin_gluten": ["sin gluten", "gluten free", "celíaco", "celiaco", "celiacos", "intolerancia al gluten"],
            "vegano": ["vegano", "vegana", "sin productos animales"],
            "bajo_sodio": ["bajo en sodio", "bajo en sal", "hipertensión", "sin sal"]
        }
        
        # Tamaños
        self.sizes = {
            "pequeño": ["pequeño", "pequeña", "pequeños", "pequeñas", "individual", "chico", "chica"],
            "mediano": ["mediano", "mediana", "medianos", "medianas", "medio"],
            "grande": ["grande", "grandes", "familiar", "fiesta", "gigante"]
        }
        
        # Colores
        self.colors = {
            "rojo": ["rojo", "roja", "rojizo", "rojiza"],
            "verde": ["verde", "verdoso", "verdosa"],
            "negro": ["negro", "negra", "negruzco", "oscuro", "oscura"]
        }
        
        # Propiedades nutricionales
        self.nutritional_properties = {
            "proteína": ["proteína", "proteínas", "rico en proteínas", "protéico"],
            "fibra": ["fibra", "alto en fibra", "rica en fibra"],
            "saludable": ["saludable", "sano", "sana", "nutritivo", "nutritiva", "nutricional"]
        }
        
        # Palabras clave para la combinación de ingredientes
        self.combination_keywords = {
            "simple": ["simple", "básica", "clásica", "tradicional", "auténtica"],
            "creativa": ["creativa", "original", "innovadora", "diferente", "única"],
            "experimental": ["experimental", "vanguardia", "moderna", "atrevida"]
        }
        
        # Cargar conceptos adicionales si existen
        self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> None:
        """Carga base de conocimiento adicional si existe."""
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        if os.path.exists(kb_path):
            try:
                with open(kb_path, "r", encoding="utf-8") as f:
                    kb = json.load(f)
                    
                # Extender conocimiento existente
                for category, items in kb.get("ingredients", {}).items():
                    if category not in self.ingredients:
                        self.ingredients[category] = {}
                    for ingredient, synonyms in items.items():
                        self.ingredients[category][ingredient] = synonyms
                
                print(f"Base de conocimiento cargada desde {kb_path}")
            except Exception as e:
                print(f"Error al cargar base de conocimiento: {e}")
    
    def process_request(self, text: str) -> Dict[str, Any]:
        """
        Procesa una solicitud en lenguaje natural y extrae información sobre
        la receta deseada.
        
        Args:
            text: Texto de la solicitud en lenguaje natural
            
        Returns:
            Diccionario con información extraída y propiedades detectadas
        """
        # Normalizar texto
        normalized_text = self._normalize_text(text)
        
        # Extraer información de la solicitud
        recipe_type = self._detect_recipe_type(normalized_text)
        size = self._detect_size(normalized_text)
        restrictions = self._detect_restrictions(normalized_text)
        colors = self._detect_colors(normalized_text)
        nutritional = self._detect_nutritional(normalized_text)
        creativity_level = self._detect_creativity(normalized_text)
        
        # Detectar ingredientes mencionados explícitamente
        explicit_ingredients = self._detect_explicit_ingredients(normalized_text)
        
        # Construir receta base
        base_recipe = self._build_base_recipe(recipe_type, size, restrictions, colors, nutritional)
        
        # Añadir ingredientes mencionados explícitamente
        for ingredient, amount in explicit_ingredients.items():
            base_recipe[ingredient] = amount
        
        # Generar propiedades para el optimizador
        properties = {
            "es_sin_gluten": "sin_gluten" in restrictions,
            "es_nutricional": nutritional,
            "colores": {
                "rojo": "rojo" in colors,
                "verde": "verde" in colors,
                "negro": "negro" in colors
            },
            "tamaño": size,
            "creatividad": creativity_level
        }
        
        # Generar respuesta
        response = {
            "recipe_name": self._generate_recipe_name(recipe_type, restrictions, colors),
            "recipe_type": recipe_type,
            "base_recipe": base_recipe,
            "properties": properties,
            "extracted_information": {
                "size": size,
                "restrictions": restrictions,
                "colors": colors,
                "nutritional": nutritional,
                "creativity_level": creativity_level,
                "explicit_ingredients": explicit_ingredients
            },
            "instructions": self._generate_instructions(recipe_type, base_recipe, properties),
            "explanation": self._generate_explanation(recipe_type, restrictions, colors, nutritional, creativity_level)
        }
        
        return response
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza el texto para facilitar el procesamiento."""
        # Convertir a minúsculas
        normalized = text.lower()
        
        # Eliminar acentos
        accents = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ü': 'u', 'ñ': 'n'
        }
        for accent, no_accent in accents.items():
            normalized = normalized.replace(accent, no_accent)
        
        # Eliminar caracteres especiales
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Reemplazar múltiples espacios con uno solo
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _detect_recipe_type(self, text: str) -> str:
        """Detecta el tipo de receta mencionado en el texto."""
        text_tokens = text.split()
        
        # Buscamos coincidencias exactas con palabras completas primero
        for recipe_type, keywords in self.recipe_types.items():
            for keyword in keywords:
                # Verificar si la palabra clave está en el texto como palabra completa
                if keyword in text_tokens:
                    return recipe_type
        
        # Si no encontramos coincidencias exactas, buscamos como subcadenas
        for recipe_type, keywords in self.recipe_types.items():
            for keyword in keywords:
                if keyword in text:
                    return recipe_type
        
        # Corregir detección de tipos específicos que pueden confundirse
        if "brioche" in text or "pan dulce" in text or "bollo suizo" in text:
            return "brioche"
        
        # Por defecto, si no se detecta ningún tipo específico, asumimos pizza
        return "pizza"
    
    def _detect_size(self, text: str) -> str:
        """Detecta el tamaño mencionado en el texto."""
        for size, keywords in self.sizes.items():
            for keyword in keywords:
                if keyword in text.split():
                    return size
        
        # Por defecto, si no se detecta ningún tamaño específico, asumimos mediano
        return "mediano"
    
    def _detect_restrictions(self, text: str) -> List[str]:
        """Detecta restricciones dietéticas mencionadas en el texto."""
        restrictions = []
        
        for restriction, keywords in self.dietary_restrictions.items():
            for keyword in keywords:
                if keyword in text:
                    restrictions.append(restriction)
                    break
        
        return restrictions
    
    def _detect_colors(self, text: str) -> List[str]:
        """Detecta colores mencionados en el texto."""
        colors = []
        
        for color, keywords in self.colors.items():
            for keyword in keywords:
                if keyword in text.split():
                    colors.append(color)
                    break
        
        return colors
    
    def _detect_nutritional(self, text: str) -> bool:
        """Detecta si se mencionan propiedades nutricionales en el texto."""
        for property_type, keywords in self.nutritional_properties.items():
            for keyword in keywords:
                if keyword in text.split():
                    return True
        
        return False
    
    def _detect_creativity(self, text: str) -> str:
        """Detecta el nivel de creatividad solicitado."""
        for level, keywords in self.combination_keywords.items():
            for keyword in keywords:
                if keyword in text.split():
                    return level
        
        # Por defecto, nivel medio de creatividad
        return "creativa"
    
    def _detect_explicit_ingredients(self, text: str) -> Dict[str, float]:
        """Detecta ingredientes mencionados explícitamente en el texto."""
        explicit_ingredients = {}
        
        # Buscar menciones de ingredientes en todas las categorías
        for category, ingredients in self.ingredients.items():
            for ingredient_id, synonyms in ingredients.items():
                for synonym in synonyms:
                    if synonym in text:
                        # Si ya está en la lista, no lo añadimos de nuevo
                        if ingredient_id not in explicit_ingredients:
                            # Asignamos un valor predeterminado (se ajustará durante la optimización)
                            explicit_ingredients[ingredient_id] = 1.0
        
        return explicit_ingredients
    
    def _build_base_recipe(self, recipe_type: str, size: str, restrictions: List[str], 
                          colors: List[str], nutritional: bool) -> Dict[str, float]:
        """
        Construye una receta base según el tipo, tamaño y restricciones.
        
        Args:
            recipe_type: Tipo de receta (pizza, pan, etc.)
            size: Tamaño (pequeño, mediano, grande)
            restrictions: Lista de restricciones dietéticas
            colors: Lista de colores deseados
            nutritional: Si debe ser nutricionalmente mejorada
            
        Returns:
            Diccionario con ingredientes y cantidades base
        """
        # Factores de escala por tamaño
        size_factors = {
            "pequeño": 0.7,
            "mediano": 1.0,
            "grande": 1.5
        }
        
        # Obtener factor de escala
        scale_factor = size_factors.get(size, 1.0)
        
        # Intentar obtener receta de masas especiales (nuevas adiciones Sprint 4)
        specialty_types = ["brioche", "croissant", "masa_filo", "pasta_fresca", "masa_strudel", "kouign_amann"]
        if recipe_type in specialty_types:
            try:
                from src.data.recipes_db.specialty_doughs import get_specialty_dough
                specialty_recipe = get_specialty_dough(recipe_type)
                if specialty_recipe:
                    # Aplicar factor de escala
                    recipe = {}
                    for key, value in specialty_recipe.items():
                        if key != "descripcion":  # No escalar la descripción
                            recipe[key] = value * scale_factor
                        else:
                            recipe[key] = value
                    return recipe
            except ImportError:
                # Si hay error, continuar con recetas base estándar
                pass
        
        # Receta base según tipo (cantidades relativas a 1kg de harina total)
        base_recipes = {
            "pizza": {
                "harina": 1000 * scale_factor,
                "agua": 650 * scale_factor,
                "sal": 20 * scale_factor,
                "levadura": 5 * scale_factor,
                "aceite_de_oliva": 50 * scale_factor
            },
            "pan": {
                "harina": 1000 * scale_factor,
                "agua": 700 * scale_factor,
                "sal": 20 * scale_factor,
                "levadura": 7 * scale_factor
            },
            "flatbread": {
                "harina": 1000 * scale_factor,
                "agua": 600 * scale_factor,
                "sal": 18 * scale_factor,
                "levadura": 3 * scale_factor,
                "aceite_de_oliva": 80 * scale_factor
            },
            "brioche": {
                "harina": 1000 * scale_factor,
                "agua": 150 * scale_factor,
                "leche": 200 * scale_factor,
                "sal": 20 * scale_factor,
                "levadura": 20 * scale_factor,
                "azucar": 100 * scale_factor,
                "mantequilla": 300 * scale_factor,
                "huevo": 250 * scale_factor
            },
            "croissant": {
                "harina_fuerza": 1000 * scale_factor,
                "agua": 500 * scale_factor,
                "leche": 50 * scale_factor,
                "sal": 20 * scale_factor,
                "levadura": 20 * scale_factor,
                "azucar": 100 * scale_factor,
                "mantequilla_laminado": 400 * scale_factor
            },
            "pasta_fresca": {
                "harina": 1000 * scale_factor,
                "huevo": 550 * scale_factor,
                "sal": 10 * scale_factor,
                "aceite_oliva": 20 * scale_factor
            }
        }
        
        # Obtener receta base según tipo
        recipe = base_recipes.get(recipe_type, base_recipes["pizza"])
        
        # Aplicar restricciones
        if "sin_gluten" in restrictions:
            # Reemplazar harina con alternativas sin gluten
            gluten_free_flour = recipe.pop("harina", 0)
            recipe["harina_de_arroz"] = gluten_free_flour * 0.7
            recipe["almidón_de_maíz"] = gluten_free_flour * 0.3
            recipe["goma_xantana"] = gluten_free_flour * 0.03
        
        if "bajo_sodio" in restrictions:
            # Reducir cantidad de sal
            if "sal" in recipe:
                recipe["sal"] = recipe["sal"] * 0.5
        
        # Aplicar colores
        for color in colors:
            if color == "rojo" and "remolacha" not in recipe:
                recipe["remolacha"] = recipe.get("harina", 0) * 0.15
            elif color == "verde" and "espinaca" not in recipe:
                recipe["espinaca"] = recipe.get("harina", 0) * 0.15
            elif color == "negro" and "carbón_activado" not in recipe:
                recipe["carbón_activado"] = recipe.get("harina", 0) * 0.05
        
        # Aplicar propiedades nutricionales
        if nutritional:
            total_flour = 0
            for key in recipe:
                if "harina" in key:
                    total_flour += recipe[key]
            
            recipe["semillas_de_lino"] = total_flour * 0.05
            recipe["semillas_de_chía"] = total_flour * 0.03
            
            # Si no es sin gluten, añadir algo de harina integral
            if "sin_gluten" not in restrictions and "harina" in recipe:
                integral_amount = recipe["harina"] * 0.3
                recipe["harina"] -= integral_amount
                recipe["harina_integral"] = integral_amount
        
        return recipe
    
    def _generate_recipe_name(self, recipe_type: str, restrictions: List[str], colors: List[str]) -> str:
        """Genera un nombre para la receta basado en sus características."""
        # Mapeo de tipos de receta a nombres en español
        type_names = {
            "pizza": "Pizza",
            "pan": "Pan",
            "flatbread": "Focaccia"
        }
        
        # Base del nombre
        base_name = type_names.get(recipe_type, "Receta")
        
        # Añadir características especiales
        special_traits = []
        
        # Añadir restricciones al nombre
        restriction_names = {
            "sin_gluten": "Sin Gluten",
            "vegano": "Vegana",
            "bajo_sodio": "Baja en Sodio"
        }
        
        for restriction in restrictions:
            if restriction in restriction_names:
                special_traits.append(restriction_names[restriction])
        
        # Añadir colores al nombre
        color_names = {
            "rojo": "Roja",
            "verde": "Verde",
            "negro": "Negra"
        }
        
        for color in colors:
            if color in color_names:
                special_traits.append(color_names[color])
        
        # Generar nombre final
        if special_traits:
            return f"{base_name} {' '.join(special_traits)}"
        else:
            return f"{base_name} Clásica"
    
    def _generate_instructions(self, recipe_type: str, recipe: Dict[str, float],
                             properties: Dict[str, Any]) -> List[str]:
        """
        Genera instrucciones paso a paso para la receta.
        
        Args:
            recipe_type: Tipo de receta
            recipe: Diccionario con ingredientes y cantidades
            properties: Propiedades de la receta
            
        Returns:
            Lista de instrucciones paso a paso
        """
        instructions = []
        is_gluten_free = properties.get("es_sin_gluten", False)
        has_color = any(properties.get("colores", {}).values())
        
        # Paso 1: Mezclar ingredientes secos
        dry_ingredients = []
        for ingredient in recipe:
            if ingredient in ["harina", "harina_integral", "harina_de_arroz", "almidón_de_maíz",
                             "sal", "semillas_de_lino", "semillas_de_chía", "semillas_de_girasol",
                             "salvado", "goma_xantana"]:
                if recipe[ingredient] > 0:
                    dry_ingredients.append(ingredient.replace("_", " "))
        
        if dry_ingredients:
            dry_str = ", ".join(dry_ingredients[:-1]) + " y " + dry_ingredients[-1] if len(dry_ingredients) > 1 else dry_ingredients[0]
            instructions.append(f"1. En un recipiente grande, mezcla los ingredientes secos: {dry_str}.")
        
        # Paso 2: Preparar los ingredientes especiales (colores)
        if has_color:
            color_ingredients = []
            color_instructions = ""
            
            if properties["colores"].get("rojo", False) and "remolacha" in recipe:
                color_ingredients.append("remolacha")
                color_instructions = "Pela y ralla finamente la remolacha. Exprime para extraer el jugo y reserva."
            elif properties["colores"].get("verde", False) and "espinaca" in recipe:
                color_ingredients.append("espinaca")
                color_instructions = "Blanquea las espinacas en agua hirviendo durante 30 segundos. Enfría en agua con hielo, escurre y tritura hasta obtener un puré fino."
            elif properties["colores"].get("negro", False) and "carbón_activado" in recipe:
                color_ingredients.append("carbón activado")
                color_instructions = "Mide con precisión la cantidad de carbón activado. Utiliza guantes para manipularlo y evita inhalar el polvo."
            
            if color_ingredients:
                instructions.append(f"2. Prepara los ingredientes para el color: {color_instructions}")
        
        # Paso 3: Disolver levadura (si la hay)
        if "levadura" in recipe and recipe["levadura"] > 0:
            if recipe_type == "pizza":
                instructions.append("3. En un recipiente aparte, disuelve la levadura en agua tibia (30°C) con una pizca de azúcar. Deja reposar 5-10 minutos hasta que se forme espuma.")
            else:
                instructions.append("3. En un recipiente aparte, disuelve la levadura en una parte del agua tibia (30°C). Deja reposar 5-10 minutos hasta que se active.")
        
        # Paso 4: Formación de la masa
        liquid_step = "4. "
        if "levadura" in recipe and recipe["levadura"] > 0:
            liquid_step += "Añade la mezcla de levadura a los ingredientes secos. "
        
        if has_color:
            if properties["colores"].get("rojo", False):
                liquid_step += "Incorpora el jugo de remolacha junto con el resto de agua. "
            elif properties["colores"].get("verde", False):
                liquid_step += "Incorpora el puré de espinacas junto con el resto de agua. "
            elif properties["colores"].get("negro", False):
                liquid_step += "Incorpora el carbón activado mezclado con una parte del agua. "
        else:
            liquid_step += "Añade el agua gradualmente. "
        
        if "aceite_de_oliva" in recipe and recipe["aceite_de_oliva"] > 0:
            liquid_step += "Finalmente, añade el aceite de oliva. "
        
        liquid_step += "Mezcla hasta que todos los ingredientes estén bien incorporados."
        instructions.append(liquid_step)
        
        # Paso 5: Amasado
        if is_gluten_free:
            instructions.append("5. Mezcla hasta obtener una masa homogénea. La masa sin gluten no necesita amasado extenso como las masas tradicionales.")
        else:
            if recipe_type == "pizza":
                instructions.append("5. Amasa enérgicamente sobre una superficie ligeramente enharinada durante 10-15 minutos, hasta obtener una masa elástica y suave.")
            elif recipe_type == "pan":
                instructions.append("5. Amasa enérgicamente sobre una superficie ligeramente enharinada durante 15-20 minutos, hasta que la masa pase la 'prueba de la ventana' (se estira sin romperse).")
            else:  # flatbread
                instructions.append("5. Amasa durante 5-10 minutos hasta que la masa esté homogénea. No es necesario un amasado tan extenso como para el pan.")
        
        # Paso 6: Primera fermentación
        if "levadura" in recipe and recipe["levadura"] > 0:
            if recipe_type == "pizza":
                instructions.append("6. Forma una bola con la masa, colócala en un recipiente ligeramente aceitado y cúbrelo con film plástico. Deja fermentar a temperatura ambiente (unos 24°C) durante 1-2 horas, o hasta que duplique su tamaño.")
            elif recipe_type == "pan":
                instructions.append("6. Forma una bola con la masa, colócala en un recipiente ligeramente aceitado y cúbrelo con un paño húmedo. Deja fermentar a temperatura ambiente durante 1-2 horas, o hasta que duplique su tamaño.")
            else:  # flatbread
                instructions.append("6. Forma una bola con la masa, colócala en un recipiente ligeramente aceitado y cúbrelo. Deja reposar a temperatura ambiente durante 30-45 minutos.")
        
        # Paso 7: Formado
        if recipe_type == "pizza":
            instructions.append("7. Pasado el tiempo de fermentación, divide la masa según el tamaño deseado. Forma bolas y déjalas reposar cubiertas durante 30 minutos más.")
            instructions.append("8. Estira cada bola de masa para formar discos, utilizando los dedos o un rodillo. Para una auténtica pizza, estira desde el centro hacia afuera, dejando un borde ligeramente más grueso.")
        elif recipe_type == "pan":
            instructions.append("7. Pasado el tiempo de fermentación, desgasifica suavemente la masa y dale forma según el tipo de pan deseado (hogaza, barra, etc.).")
            instructions.append("8. Coloca la masa formada en un molde o bandeja de horno enharinada. Realiza cortes decorativos en la superficie con un cuchillo afilado.")
        else:  # flatbread
            instructions.append("7. Extiende la masa en una bandeja de horno aceitada, presionando con las yemas de los dedos para formar hoyuelos característicos.")
            instructions.append("8. Cepilla la superficie con aceite de oliva y espolvorea con sal marina si lo deseas.")
        
        # Paso 9: Segunda fermentación (si aplica)
        if recipe_type == "pan":
            instructions.append("9. Deja que el pan fermente nuevamente durante 30-45 minutos, o hasta que aumente visiblemente su volumen.")
        
        # Paso 10: Horneado
        if recipe_type == "pizza":
            instructions.append("9. Hornea en un horno precalentado a máxima temperatura (idealmente 250-300°C) durante 5-8 minutos, o hasta que los bordes estén dorados y crujientes.")
        elif recipe_type == "pan":
            instructions.append("10. Hornea en un horno precalentado a 220°C durante los primeros 15 minutos, luego reduce a 190°C y continúa horneando durante 25-35 minutos más, hasta que el pan esté dorado y suene hueco al golpear la base.")
        else:  # flatbread
            instructions.append("9. Hornea en un horno precalentado a 220°C durante 15-18 minutos, o hasta que los bordes estén dorados y la superficie ligeramente crujiente.")
        
        # Paso final
        if recipe_type == "pizza":
            instructions.append("10. ¡Disfruta tu pizza con tus ingredientes favoritos!")
        elif recipe_type == "pan":
            instructions.append("11. Retira el pan del horno y deja que se enfríe completamente sobre una rejilla antes de cortarlo.")
        else:  # flatbread
            instructions.append("10. Sirve caliente, opcionalmente con aceite de oliva adicional o tus condimentos favoritos.")
        
        return instructions
    
    def _generate_explanation(self, recipe_type: str, restrictions: List[str], 
                            colors: List[str], nutritional: bool, 
                            creativity_level: str) -> str:
        """Genera una explicación de cómo la IA interpretó la solicitud."""
        parts = []
        
        # Tipo de receta
        type_names = {
            "pizza": "una masa de pizza",
            "pan": "una masa de pan",
            "flatbread": "una masa plana tipo focaccia"
        }
        parts.append(f"Entendí que buscabas {type_names.get(recipe_type, 'una receta')}")
        
        # Restricciones
        restriction_explanations = []
        for restriction in restrictions:
            if restriction == "sin_gluten":
                restriction_explanations.append("sin gluten, por lo que utilicé una combinación de harinas alternativas y goma xantana")
            elif restriction == "vegano":
                restriction_explanations.append("vegana, sin ingredientes de origen animal")
            elif restriction == "bajo_sodio":
                restriction_explanations.append("baja en sodio, reduciendo la cantidad de sal")
        
        if restriction_explanations:
            parts.append(", ".join(restriction_explanations))
        
        # Colores
        color_explanations = []
        for color in colors:
            if color == "rojo":
                color_explanations.append("roja (usando remolacha para el color)")
            elif color == "verde":
                color_explanations.append("verde (usando espinaca para el color)")
            elif color == "negro":
                color_explanations.append("negra (usando carbón activado para el color)")
        
        if color_explanations:
            parts.append(", ".join(color_explanations))
        
        # Propiedades nutricionales
        if nutritional:
            parts.append("con propiedades nutricionales mejoradas (añadiendo semillas y fibra)")
        
        # Nivel de creatividad
        creativity_explanations = {
            "simple": "siguiendo una receta clásica y tradicional",
            "creativa": "con un toque de creatividad en la combinación de ingredientes",
            "experimental": "con una combinación experimental e innovadora de ingredientes"
        }
        
        if creativity_level in creativity_explanations:
            parts.append(creativity_explanations[creativity_level])
        
        # Unir todas las partes
        return " ".join(parts) + "."


if __name__ == "__main__":
    # Código de prueba
    processor = LanguageProcessor()
    
    # Ejemplos de solicitudes
    examples = [
        "Quiero una masa de pizza familiar, de color rojo, sin gluten, nutricionalmente optimizada.",
        "Necesito una receta de pan integral de alta proteína.",
        "Dame una focaccia tradicional con aceite de oliva.",
        "Quiero un pan plano tipo pita que sea vegano."
    ]
    
    for i, example in enumerate(examples):
        print(f"\nEjemplo {i+1}: {example}")
        recipe = processor.process_request(example)
        print("\nReceta generada:")
        for ing, amount in recipe["base_recipe"].items():
            if ing not in ["recipe_name", "recipe_id"]:
                print(f"  {ing}: {amount:.1f}g")
        
        print("\nPropiedades detectadas:")
        for prop_type, values in recipe["properties"].items():
            if isinstance(values, dict):
                detected = [k for k, v in values.items() if v]
                if detected:
                    print(f"  {prop_type}: {', '.join(detected)}")
            else:
                print(f"  {prop_type}: {values}")
        
        print("\nInstrucciones:")
        for instruction in recipe["instructions"]:
            print(f"  - {instruction}")
        
        print("\nExplicación:")
        print(recipe["explanation"]) 