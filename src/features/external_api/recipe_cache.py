"""
Sistema de caché inteligente para recetas que permite reutilizar y adaptar recetas
similares sin necesidad de hacer nuevas consultas a la API.
"""

import os
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)

class RecipeCache:
    """
    Sistema de caché inteligente para recetas externas.
    
    Permite almacenar y recuperar recetas, así como adaptarlas sin necesidad
    de realizar nuevas consultas a APIs externas.
    """
    
    def __init__(self, cache_dir: str = "cache/recipes"):
        """
        Inicializa el sistema de caché.
        
        Args:
            cache_dir: Directorio donde se almacenan las recetas
        """
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
        self.recipe_index = self._load_recipe_index()
        
    def _ensure_cache_dir(self) -> None:
        """Asegura que exista el directorio de caché"""
        os.makedirs(self.cache_dir, exist_ok=True)
        index_path = os.path.join(self.cache_dir, "index.json")
        if not os.path.exists(index_path):
            with open(index_path, 'w') as f:
                json.dump({"recipes": {}}, f)
    
    def _load_recipe_index(self) -> Dict[str, Any]:
        """Carga el índice de recetas desde el archivo JSON"""
        index_path = os.path.join(self.cache_dir, "index.json")
        try:
            with open(index_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("No se pudo cargar el índice de recetas, creando uno nuevo")
            return {"recipes": {}}
    
    def _save_recipe_index(self) -> None:
        """Guarda el índice de recetas en el archivo JSON"""
        index_path = os.path.join(self.cache_dir, "index.json")
        with open(index_path, 'w') as f:
            json.dump(self.recipe_index, f, indent=2)
    
    def _generate_recipe_id(self, recipe: Dict[str, Any]) -> str:
        """
        Genera un ID único para una receta.
        
        Args:
            recipe: Receta a indexar
            
        Returns:
            ID único para la receta
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        recipe_type = recipe.get("detected_type", "unknown")
        name = recipe.get("name", "unknown").lower().replace(" ", "_")
        return f"{recipe_type}_{name}_{timestamp}"
    
    def add_recipe(self, recipe: Dict[str, Any]) -> str:
        """
        Añade una receta al caché.
        
        Args:
            recipe: Receta a añadir
            
        Returns:
            ID de la receta
        """
        recipe_id = self._generate_recipe_id(recipe)
        
        # Almacenar el archivo de receta
        recipe_path = os.path.join(self.cache_dir, f"{recipe_id}.json")
        with open(recipe_path, 'w') as f:
            json.dump(recipe, f, indent=2)
        
        # Indexar la receta para búsquedas rápidas
        recipe_type = recipe.get("detected_type", "unknown")
        properties = recipe.get("properties", {})
        
        # Detectar fruta principal
        recipe_name = recipe.get("name", "").lower()
        detected_fruit = self._detect_fruit(recipe_name, recipe)
        
        index_entry = {
            "id": recipe_id,
            "type": recipe_type,
            "name": recipe.get("name", ""),
            "fruit": detected_fruit,
            "properties": {
                "sin_gluten": properties.get("sin_gluten", False),
                "sin_lactosa": properties.get("sin_lactosa", False),
                "vegano": properties.get("vegano", False)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self.recipe_index["recipes"][recipe_id] = index_entry
        self._save_recipe_index()
        
        return recipe_id
    
    def get_recipe(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una receta del caché por su ID.
        
        Args:
            recipe_id: ID de la receta
            
        Returns:
            Receta o None si no existe
        """
        if recipe_id not in self.recipe_index["recipes"]:
            return None
        
        recipe_path = os.path.join(self.cache_dir, f"{recipe_id}.json")
        
        try:
            with open(recipe_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning(f"No se pudo cargar la receta {recipe_id}")
            return None
    
    def find_similar_recipe(self, recipe_type: str, fruit: str = "", gluten_free: bool = False, 
                           dairy_free: bool = False) -> Optional[str]:
        """
        Encuentra una receta similar en el caché.
        
        Args:
            recipe_type: Tipo de receta (ej: "cheesecake")
            fruit: Fruta principal
            gluten_free: Si debe ser sin gluten
            dairy_free: Si debe ser sin lactosa
            
        Returns:
            ID de la receta similar o None si no hay coincidencias
        """
        candidates = []
        
        for recipe_id, recipe_info in self.recipe_index["recipes"].items():
            # Debe ser del mismo tipo
            if recipe_info["type"] != recipe_type:
                continue
                
            # Calcular puntuación de similitud
            score = 0
            
            # Coincidencia exacta de restricciones dietéticas (muy importante)
            if recipe_info["properties"]["sin_gluten"] == gluten_free:
                score += 3
                
            if recipe_info["properties"]["sin_lactosa"] == dairy_free:
                score += 3
                
            # Coincidencia de fruta (importante pero adaptable)
            if recipe_info.get("fruit", "") == fruit:
                score += 2
            
            candidates.append((recipe_id, score))
        
        # Ordenar por puntuación y devolver el mejor candidato si supera el umbral
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        if candidates and candidates[0][1] >= 3:  # Umbral mínimo de similitud
            return candidates[0][0]
            
        return None
    
    def adapt_recipe(self, recipe_id: str, new_fruit: Optional[str] = None, 
                    gluten_free: Optional[bool] = None, dairy_free: Optional[bool] = None) -> Dict[str, Any]:
        """
        Adapta una receta existente para cambiar fruta o restricciones dietéticas.
        
        Args:
            recipe_id: ID de la receta a adaptar
            new_fruit: Nueva fruta principal (None para mantener)
            gluten_free: Nueva restricción sin gluten (None para mantener)
            dairy_free: Nueva restricción sin lactosa (None para mantener)
            
        Returns:
            Receta adaptada
        """
        # Obtener receta original
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            logger.error(f"No se encontró la receta {recipe_id} para adaptar")
            return {}
            
        # Crear copia para modificar
        adapted_recipe = recipe.copy()
        
        # Adaptar fruta si se especificó
        if new_fruit is not None:
            original_fruit = self._detect_fruit(recipe.get("name", ""), recipe)
            if original_fruit:
                # Reemplazar fruta en el nombre
                if original_fruit in adapted_recipe.get("name", "").lower():
                    adapted_recipe["name"] = adapted_recipe["name"].replace(
                        original_fruit, new_fruit
                    ).replace(original_fruit.capitalize(), new_fruit.capitalize())
                else:
                    adapted_recipe["name"] += f" con {new_fruit}"
                
                # Reemplazar en ingredientes
                ingredients = adapted_recipe.get("ingredients", {})
                normalized_original = original_fruit.replace(" ", "_")
                normalized_new = new_fruit.replace(" ", "_")
                
                if normalized_original in ingredients:
                    quantity = ingredients[normalized_original]
                    del ingredients[normalized_original]
                    ingredients[normalized_new] = quantity
                else:
                    # No encontramos la fruta original, añadir la nueva
                    ingredients[normalized_new] = 200.0  # Cantidad estimada
                
                # Reemplazar en instrucciones
                for i, instruction in enumerate(adapted_recipe.get("instructions", [])):
                    if original_fruit in instruction.lower():
                        adapted_recipe["instructions"][i] = instruction.replace(
                            original_fruit, new_fruit
                        ).replace(original_fruit.capitalize(), new_fruit.capitalize())
            else:
                # No había fruta original, añadir la nueva
                adapted_recipe["name"] += f" con {new_fruit}"
                adapted_recipe["ingredients"][new_fruit.replace(" ", "_")] = 200.0
                adapted_recipe["instructions"].append(f"Decorar con {new_fruit} frescas antes de servir.")
        
        # Adaptar restricciones dietéticas
        if gluten_free is not None or dairy_free is not None:
            # Actualizar propiedades
            if "properties" not in adapted_recipe:
                adapted_recipe["properties"] = {}
                
            if gluten_free is not None:
                adapted_recipe["properties"]["sin_gluten"] = gluten_free
                
            if dairy_free is not None:
                adapted_recipe["properties"]["sin_lactosa"] = dairy_free
                adapted_recipe["properties"]["vegano"] = dairy_free
            
            # Actualizar nombre con nuevas propiedades
            name_parts = []
            base_name = adapted_recipe.get("name", "Receta").split(" con ")[0]
            
            if " Sin " in base_name:
                base_name = base_name.split(" Sin ")[0]
                
            name_parts.append(base_name)
            
            if adapted_recipe["properties"].get("sin_gluten", False):
                name_parts.append("Sin Gluten")
                
            if adapted_recipe["properties"].get("sin_lactosa", False):
                name_parts.append("Sin Lácteos")
                
            # Añadir fruta al final si existe
            if new_fruit or self._detect_fruit(adapted_recipe.get("name", ""), adapted_recipe):
                fruit_to_use = new_fruit if new_fruit else self._detect_fruit(adapted_recipe.get("name", ""), adapted_recipe)
                name_parts.append(f"con {fruit_to_use}")
                
            adapted_recipe["name"] = " ".join(name_parts)
            
            # Nota: Aquí podríamos implementar sustituciones de ingredientes
            # para adaptar a restricciones dietéticas, pero eso requeriría un
            # conocimiento detallado de ingredientes alternativos
        
        return adapted_recipe
    
    def _detect_fruit(self, recipe_name: str, recipe: Dict[str, Any]) -> str:
        """
        Detecta la fruta principal de una receta.
        
        Args:
            recipe_name: Nombre de la receta
            recipe: Datos completos de la receta
            
        Returns:
            Fruta detectada o cadena vacía
        """
        # Lista de frutas comunes
        fruits = [
            "fresa", "fresas", "frambuesa", "frambuesas", "arándano", "arándanos",
            "mora", "moras", "limón", "naranja", "mango", "kiwi", "piña", "manzana",
            "pera", "melocotón", "durazno", "cereza", "cerezas", "plátano", "banana",
            "albaricoque", "coco", "higo", "granada", "melón", "sandía", "uva", "uvas",
            "mandarina", "maracuyá", "caqui", "fruta de la pasión", "papaya", "guayaba"
        ]
        
        # Primero buscar en el nombre
        for fruit in fruits:
            pattern = rf'\b{re.escape(fruit)}\b'
            if re.search(pattern, recipe_name.lower()):
                return fruit
        
        # Luego buscar en ingredientes
        for ingredient in recipe.get("ingredients", {}).keys():
            ingredient_norm = ingredient.lower().replace("_", " ")
            for fruit in fruits:
                pattern = rf'\b{re.escape(fruit)}\b'
                if re.search(pattern, ingredient_norm):
                    return fruit
        
        # Finalmente buscar en instrucciones
        for instruction in recipe.get("instructions", []):
            for fruit in fruits:
                pattern = rf'\b{re.escape(fruit)}\b'
                if re.search(pattern, instruction.lower()):
                    return fruit
        
        return ""
        
    def clear_cache(self) -> None:
        """Elimina todas las recetas del caché"""
        if not os.path.exists(self.cache_dir):
            return
            
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Error al eliminar {file_path}: {e}")
        
        # Reiniciar índice
        self.recipe_index = {"recipes": {}}
        self._save_recipe_index()
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Devuelve estadísticas del caché.
        
        Returns:
            Diccionario con estadísticas
        """
        recipe_types = {}
        total_recipes = len(self.recipe_index["recipes"])
        
        for recipe_info in self.recipe_index["recipes"].values():
            recipe_type = recipe_info["type"]
            if recipe_type not in recipe_types:
                recipe_types[recipe_type] = 0
            recipe_types[recipe_type] += 1
            
        return {
            "total_recipes": total_recipes,
            "recipe_types": recipe_types
        } 