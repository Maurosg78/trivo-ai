"""
Generador de recetas basado en parámetros y requisitos del usuario.

Este módulo proporciona la funcionalidad para generar recetas basándose
en los parámetros y restricciones proporcionados por el usuario.
"""

from typing import Dict, List, Any, Optional, Tuple
import random
from .recipe_model import Recipe, Ingredient


class RecipeGenerator:
    """
    Generador de recetas que produce formulas basadas en parámetros proporcionados.
    
    Esta clase base define la interfaz para los generadores de recetas.
    Las implementaciones específicas deben heredar de esta clase y 
    proporcionar la lógica de generación.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el generador con configuración opcional.
        
        Args:
            config: Diccionario de configuración para el generador
        """
        self.config = config or {}
        self.ingredient_database: Dict[str, Dict[str, Any]] = {}
        
    def load_ingredients(self, ingredients_data: Dict[str, Dict[str, Any]]) -> None:
        """
        Carga una base de datos de ingredientes disponibles.
        
        Args:
            ingredients_data: Diccionario con información de ingredientes
        """
        self.ingredient_database = ingredients_data
        
    def generate_recipe(self, params: Dict[str, Any]) -> Recipe:
        """
        Genera una receta basada en los parámetros proporcionados.
        
        Este es un método abstracto que debe ser implementado por las clases derivadas.
        
        Args:
            params: Parámetros para la generación de la receta
            
        Returns:
            Una receta generada
            
        Raises:
            NotImplementedError: Si la clase hija no implementa este método
        """
        raise NotImplementedError("Las subclases deben implementar este método")
    
    def get_available_ingredients(self, category: Optional[str] = None) -> List[str]:
        """
        Obtiene la lista de ingredientes disponibles, opcionalmente filtrados por categoría.
        
        Args:
            category: Categoría para filtrar los ingredientes (opcional)
            
        Returns:
            Lista de nombres de ingredientes disponibles
        """
        if category:
            return [
                name for name, data in self.ingredient_database.items()
                if data.get("category") == category
            ]
        return list(self.ingredient_database.keys())


class BasicRecipeGenerator(RecipeGenerator):
    """
    Implementación básica del generador de recetas.
    
    Genera recetas simples basadas en templates y requisitos básicos.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el generador básico.
        
        Args:
            config: Configuración para el generador
        """
        super().__init__(config)
        self.templates: Dict[str, Dict[str, Any]] = {}
        
    def load_templates(self, templates_data: Dict[str, Dict[str, Any]]) -> None:
        """
        Carga templates de recetas para usar como base.
        
        Args:
            templates_data: Diccionario con templates de recetas
        """
        self.templates = templates_data
        
    def generate_recipe(self, params: Dict[str, Any]) -> Recipe:
        """
        Genera una receta básica basada en los parámetros proporcionados.
        
        Args:
            params: Parámetros para la generación incluyendo:
                   - base_template: Nombre del template base a usar
                   - name: Nombre para la receta
                   - size: Tamaño de la receta (pequeña, mediana, grande)
                   - preferences: Preferencias dietéticas o de ingredientes
            
        Returns:
            Receta generada con los parámetros especificados
        """
        # Obtener template base si se especifica
        template_name = params.get("base_template")
        template = self.templates.get(template_name, {}) if template_name else {}
        
        # Crear nueva receta
        recipe_name = params.get("name", "Receta generada")
        recipe = Recipe(name=recipe_name)
        
        # Añadir propiedades de la receta
        recipe.properties = {
            "size": params.get("size", "mediana"),
            "preferences": params.get("preferences", []),
            "source": "generator"
        }
        
        # Añadir ingredientes base del template
        base_ingredients = template.get("base_ingredients", {})
        for ing_name, properties in base_ingredients.items():
            if ing_name in self.ingredient_database:
                amount = properties.get("amount", 100.0)
                
                # Aplicar factor de tamaño
                size_factor = self._get_size_factor(params.get("size", "mediana"))
                amount *= size_factor
                
                ingredient = Ingredient(
                    name=ing_name,
                    amount=amount,
                    properties=self.ingredient_database[ing_name].copy()
                )
                recipe.add_ingredient(ingredient)
        
        # Aplicar ajustes basados en preferencias
        preferences = params.get("preferences", [])
        self._apply_preferences(recipe, preferences)
        
        return recipe
    
    def _get_size_factor(self, size: str) -> float:
        """
        Obtiene el factor de escala basado en el tamaño especificado.
        
        Args:
            size: Tamaño de la receta (pequeña, mediana, grande)
            
        Returns:
            Factor de escala para los ingredientes
        """
        size_factors = {
            "pequeña": 0.7,
            "mediana": 1.0,
            "grande": 1.5,
            "familiar": 2.0,
        }
        return size_factors.get(size.lower(), 1.0)
    
    def _apply_preferences(self, recipe: Recipe, preferences: List[str]) -> None:
        """
        Aplica modificaciones a la receta basadas en preferencias.
        
        Args:
            recipe: Receta a modificar
            preferences: Lista de preferencias a aplicar
        """
        for preference in preferences:
            if preference.lower() == "sin_gluten":
                self._make_gluten_free(recipe)
            elif preference.lower() == "vegana":
                self._make_vegan(recipe)
            elif preference.lower() == "integral":
                self._make_whole_grain(recipe)
    
    def _make_gluten_free(self, recipe: Recipe) -> None:
        """
        Modifica la receta para hacerla sin gluten.
        
        Args:
            recipe: Receta a modificar
        """
        # Buscar harinas con gluten y reemplazarlas
        for ingredient in list(recipe.ingredients):
            properties = ingredient.properties
            if (
                properties.get("category") == "harina" and 
                properties.get("contains_gluten", False)
            ):
                # Eliminar la harina con gluten
                recipe.remove_ingredient(ingredient.name)
                
                # Añadir mezcla de harinas sin gluten
                gluten_free_flours = self.get_available_ingredients("harina_sin_gluten")
                if gluten_free_flours:
                    for flour in gluten_free_flours[:2]:  # Usar hasta 2 harinas sin gluten
                        gf_ingredient = Ingredient(
                            name=flour,
                            amount=ingredient.amount / len(gluten_free_flours[:2]),
                            properties=self.ingredient_database[flour].copy()
                        )
                        recipe.add_ingredient(gf_ingredient)
        
        # Añadir goma xantana si hay harinas sin gluten
        has_gf_flour = any(
            self.ingredient_database.get(i.name, {}).get("category") == "harina_sin_gluten"
            for i in recipe.ingredients
        )
        
        if has_gf_flour and "goma_xantana" in self.ingredient_database:
            total_flour = sum(
                i.amount for i in recipe.ingredients
                if self.ingredient_database.get(i.name, {}).get("category") in 
                ["harina", "harina_sin_gluten"]
            )
            
            xanthan_amount = total_flour * 0.005  # 0.5% del peso de la harina
            recipe.add_ingredient(
                Ingredient(
                    name="goma_xantana",
                    amount=xanthan_amount,
                    properties=self.ingredient_database["goma_xantana"].copy()
                )
            )
        
        # Actualizar propiedades de la receta
        recipe.properties["gluten_free"] = True
    
    def _make_vegan(self, recipe: Recipe) -> None:
        """
        Modifica la receta para hacerla vegana.
        
        Args:
            recipe: Receta a modificar
        """
        # Reemplazar ingredientes de origen animal
        for ingredient in list(recipe.ingredients):
            properties = ingredient.properties
            if properties.get("animal_origin", False):
                # Eliminar ingrediente de origen animal
                recipe.remove_ingredient(ingredient.name)
                
                # Buscar alternativa vegana
                category = properties.get("category", "")
                vegan_alternatives = [
                    name for name, data in self.ingredient_database.items()
                    if data.get("category") == f"vegan_{category}" or 
                       (data.get("category") == category and not data.get("animal_origin", False))
                ]
                
                if vegan_alternatives:
                    alt = vegan_alternatives[0]
                    alt_ingredient = Ingredient(
                        name=alt,
                        amount=ingredient.amount,
                        properties=self.ingredient_database[alt].copy()
                    )
                    recipe.add_ingredient(alt_ingredient)
        
        # Actualizar propiedades de la receta
        recipe.properties["vegan"] = True
    
    def _make_whole_grain(self, recipe: Recipe) -> None:
        """
        Modifica la receta para usar granos integrales.
        
        Args:
            recipe: Receta a modificar
        """
        # Reemplazar harinas refinadas por integrales
        for ingredient in list(recipe.ingredients):
            properties = ingredient.properties
            if (
                properties.get("category") == "harina" and 
                not properties.get("whole_grain", False)
            ):
                # Buscar alternativa integral
                base_name = ingredient.name.split()[0]  # Obtener nombre base (ej: "trigo" de "harina de trigo")
                whole_grain_alt = f"harina integral de {base_name}"
                
                if whole_grain_alt in self.ingredient_database:
                    # Eliminar harina refinada
                    recipe.remove_ingredient(ingredient.name)
                    
                    # Añadir harina integral
                    wg_ingredient = Ingredient(
                        name=whole_grain_alt,
                        amount=ingredient.amount,
                        properties=self.ingredient_database[whole_grain_alt].copy()
                    )
                    recipe.add_ingredient(wg_ingredient)
        
        # Actualizar propiedades de la receta
        recipe.properties["whole_grain"] = True 