#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para optimizar la nutrición de recetas utilizando datos del USDA
"""

import os
import json
import logging
from typing import Dict, List, Any, Tuple
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

class USDANutritionOptimizer:
    """
    Optimizador de nutrición que utiliza datos de la API de USDA
    para mejorar el perfil nutricional de recetas.
    """
    
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    
    def __init__(self, api_key: str = None):
        """
        Inicializa el optimizador con la clave API de USDA
        
        Args:
            api_key: Clave API para acceder a USDA FoodData Central API.
                     Si no se proporciona, se intentará obtener de las variables de entorno.
        """
        self.api_key = api_key or os.environ.get("USDA_API_KEY")
        if not self.api_key:
            logger.warning("No se ha proporcionado clave API para USDA. Las funcionalidades de optimización nutricional estarán limitadas.")
        
        # Caché local para evitar múltiples llamadas a la API
        self.cache = {}
    
    def optimize_recipe(self, recipe: Dict[str, float], target_profile: str = "balanced") -> Tuple[Dict[str, float], List[str]]:
        """
        Optimiza una receta para mejorar su perfil nutricional
        
        Args:
            recipe: Diccionario con ingredientes y cantidades
            target_profile: Perfil nutricional objetivo (balanced, high_protein, low_carb, etc.)
            
        Returns:
            Receta optimizada y lista de recomendaciones
        """
        # Copia de la receta para optimizar
        optimized = recipe.copy()
        recommendations = []
        
        try:
            # Calcular perfil nutricional actual
            current_profile = self._calculate_nutritional_profile(recipe)
            
            # Identificar deficiencias o excesos
            issues = self._identify_nutritional_issues(current_profile, target_profile)
            
            # Aplicar optimizaciones según el perfil objetivo
            if target_profile == "balanced":
                optimized, recommendations = self._optimize_for_balanced(recipe, issues)
            elif target_profile == "high_protein":
                optimized, recommendations = self._optimize_for_high_protein(recipe, issues)
            elif target_profile == "low_carb":
                optimized, recommendations = self._optimize_for_low_carb(recipe, issues)
            else:
                # Si el perfil no es reconocido, devolver la receta sin cambios
                recommendations.append(f"Perfil nutricional '{target_profile}' no reconocido.")
                return recipe, recommendations
            
        except Exception as e:
            logger.error(f"Error en la optimización nutricional: {str(e)}")
            recommendations.append("No se pudo optimizar la nutrición debido a un error en el servicio.")
            return recipe, ["Error en optimización nutricional. Se devuelve receta original."]
        
        return optimized, recommendations
    
    def _calculate_nutritional_profile(self, recipe: Dict[str, float]) -> Dict[str, Any]:
        """
        Calcula el perfil nutricional de una receta
        
        Args:
            recipe: Diccionario con ingredientes y cantidades
            
        Returns:
            Perfil nutricional con macronutrientes, micronutrientes, etc.
        """
        if not self.api_key:
            return self._get_estimated_nutritional_profile(recipe)
            
        profile = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "fiber": 0,
            "vitamins": {},
            "minerals": {}
        }
        
        try:
            # Solicitar datos nutricionales para cada ingrediente
            for ingredient, amount in recipe.items():
                if ingredient in ["recipe_name", "recipe_id"]:
                    continue
                
                # Convertir nombres de ingredientes
                search_term = self._convert_ingredient_name(ingredient)
                
                # Buscar en caché primero
                if search_term in self.cache:
                    nutrition_data = self.cache[search_term]
                else:
                    # Llamar a la API de USDA
                    nutrition_data = self._get_food_nutrition(search_term)
                    self.cache[search_term] = nutrition_data
                
                # Sumar contribución de este ingrediente
                if nutrition_data:
                    # Convertir a base 100g y multiplicar por la cantidad en la receta
                    factor = amount / 100.0
                    
                    # Macronutrientes
                    profile["calories"] += nutrition_data.get("calories", 0) * factor
                    
                    if "macronutrients" in nutrition_data:
                        profile["protein"] += nutrition_data["macronutrients"].get("protein", 0) * factor
                        profile["carbs"] += nutrition_data["macronutrients"].get("carbohydrates", 0) * factor
                        profile["fat"] += nutrition_data["macronutrients"].get("fat", 0) * factor
                    
                    profile["fiber"] += nutrition_data.get("fiber", 0) * factor
                    
                    # Vitaminas
                    if "vitamins" in nutrition_data:
                        for vitamin, amount in nutrition_data["vitamins"].items():
                            if vitamin not in profile["vitamins"]:
                                profile["vitamins"][vitamin] = 0
                            profile["vitamins"][vitamin] += amount * factor
                    
                    # Minerales
                    if "minerals" in nutrition_data:
                        for mineral, amount in nutrition_data["minerals"].items():
                            if mineral not in profile["minerals"]:
                                profile["minerals"][mineral] = 0
                            profile["minerals"][mineral] += amount * factor
        
        except Exception as e:
            logger.error(f"Error al calcular perfil nutricional: {str(e)}")
            return self._get_estimated_nutritional_profile(recipe)
        
        return profile
    
    def _get_estimated_nutritional_profile(self, recipe: Dict[str, float]) -> Dict[str, Any]:
        """
        Genera un perfil nutricional estimado cuando no se pueden obtener datos reales
        
        Args:
            recipe: Diccionario con ingredientes y cantidades
            
        Returns:
            Perfil nutricional estimado
        """
        profile = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "fiber": 0,
            "vitamins": {},
            "minerals": {}
        }
        
        # Estimaciones básicas para ingredientes comunes
        estimates = {
            "harina": {"calories": 364, "protein": 10, "carbs": 76, "fat": 1, "fiber": 2.7},
            "agua": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0},
            "sal": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0},
            "levadura": {"calories": 105, "protein": 8, "carbs": 9, "fat": 1.5, "fiber": 4},
            "aceite_de_oliva": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100, "fiber": 0},
            "azucar": {"calories": 387, "protein": 0, "carbs": 100, "fat": 0, "fiber": 0},
            "mantequilla": {"calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81, "fiber": 0},
            "huevo": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "fiber": 0},
            "leche": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3, "fiber": 0}
        }
        
        # Calcular contribución de cada ingrediente
        for ingredient, amount in recipe.items():
            if ingredient in ["recipe_name", "recipe_id"]:
                continue
                
            # Buscar coincidencias parciales con los ingredientes conocidos
            found = False
            for known_ingredient, values in estimates.items():
                if known_ingredient in ingredient.lower():
                    factor = amount / 100.0
                    profile["calories"] += values["calories"] * factor
                    profile["protein"] += values["protein"] * factor
                    profile["carbs"] += values["carbs"] * factor
                    profile["fat"] += values["fat"] * factor
                    profile["fiber"] += values["fiber"] * factor
                    found = True
                    break
            
            # Si no se encuentra coincidencia, usar valores predeterminados
            if not found:
                # Valores predeterminados conservadores
                factor = amount / 100.0
                profile["calories"] += 200 * factor  # Estimación genérica de calorías
                profile["protein"] += 5 * factor
                profile["carbs"] += 25 * factor
                profile["fat"] += 5 * factor
                profile["fiber"] += 1 * factor
        
        return profile
    
    def _identify_nutritional_issues(self, profile: Dict[str, Any], target_profile: str) -> List[Dict[str, Any]]:
        """
        Identifica problemas nutricionales en la receta según el perfil objetivo
        
        Args:
            profile: Perfil nutricional actual
            target_profile: Perfil nutricional objetivo
            
        Returns:
            Lista de problemas identificados
        """
        issues = []
        
        # Calcular macronutrientes totales
        total_macros = profile["protein"] + profile["carbs"] + profile["fat"]
        
        if total_macros > 0:
            # Calcular porcentajes
            protein_percent = (profile["protein"] * 4 / profile["calories"]) * 100 if profile["calories"] > 0 else 0
            carbs_percent = (profile["carbs"] * 4 / profile["calories"]) * 100 if profile["calories"] > 0 else 0
            fat_percent = (profile["fat"] * 9 / profile["calories"]) * 100 if profile["calories"] > 0 else 0
            
            # Verificar según el perfil objetivo
            if target_profile == "balanced":
                # Para un perfil balanceado: ~15-20% proteína, ~55-60% carbohidratos, ~25-30% grasas
                if protein_percent < 15:
                    issues.append({"nutrient": "protein", "issue": "low", "current": protein_percent, "target": "15-20%"})
                elif protein_percent > 20:
                    issues.append({"nutrient": "protein", "issue": "high", "current": protein_percent, "target": "15-20%"})
                
                if carbs_percent < 55:
                    issues.append({"nutrient": "carbs", "issue": "low", "current": carbs_percent, "target": "55-60%"})
                elif carbs_percent > 60:
                    issues.append({"nutrient": "carbs", "issue": "high", "current": carbs_percent, "target": "55-60%"})
                
                if fat_percent < 25:
                    issues.append({"nutrient": "fat", "issue": "low", "current": fat_percent, "target": "25-30%"})
                elif fat_percent > 30:
                    issues.append({"nutrient": "fat", "issue": "high", "current": fat_percent, "target": "25-30%"})
            
            elif target_profile == "high_protein":
                # Para alto en proteínas: ~30-35% proteína, ~40-45% carbohidratos, ~25-30% grasas
                if protein_percent < 30:
                    issues.append({"nutrient": "protein", "issue": "low", "current": protein_percent, "target": "30-35%"})
                
                if carbs_percent > 45:
                    issues.append({"nutrient": "carbs", "issue": "high", "current": carbs_percent, "target": "40-45%"})
                
                if fat_percent > 30:
                    issues.append({"nutrient": "fat", "issue": "high", "current": fat_percent, "target": "25-30%"})
            
            elif target_profile == "low_carb":
                # Para bajo en carbohidratos: ~25-30% proteína, ~20-25% carbohidratos, ~45-50% grasas
                if protein_percent < 25:
                    issues.append({"nutrient": "protein", "issue": "low", "current": protein_percent, "target": "25-30%"})
                
                if carbs_percent > 25:
                    issues.append({"nutrient": "carbs", "issue": "high", "current": carbs_percent, "target": "20-25%"})
                
                if fat_percent < 45:
                    issues.append({"nutrient": "fat", "issue": "low", "current": fat_percent, "target": "45-50%"})
        
        # Verificar fibra (para todos los perfiles)
        if profile["fiber"] < 3:
            issues.append({"nutrient": "fiber", "issue": "low", "current": profile["fiber"], "target": ">3g"})
        
        return issues
    
    def _optimize_for_balanced(self, recipe: Dict[str, float], issues: List[Dict[str, Any]]) -> Tuple[Dict[str, float], List[str]]:
        """
        Optimiza la receta para un perfil nutricional balanceado
        
        Args:
            recipe: Receta original
            issues: Problemas nutricionales identificados
            
        Returns:
            Receta optimizada y recomendaciones
        """
        optimized = recipe.copy()
        recommendations = []
        
        # Procesar cada problema identificado
        for issue in issues:
            nutrient = issue["nutrient"]
            issue_type = issue["issue"]
            
            if nutrient == "protein" and issue_type == "low":
                # Ajustar para aumentar proteína
                if self._has_ingredient_like(recipe, "harina"):
                    # Si hay harina, reemplazar parte con fuentes de proteína
                    flour_key = self._find_ingredient_like(recipe, "harina")
                    if flour_key:
                        flour_amount = optimized[flour_key]
                        optimized[flour_key] = flour_amount * 0.9  # Reducir en 10%
                        
                        # Agregar harina de mayor proteína
                        protein_flour = "harina_de_fuerza"
                        optimized[protein_flour] = flour_amount * 0.1
                        
                        recommendations.append("Se reemplazó parte de la harina por harina de fuerza para aumentar el contenido proteico.")
            
            elif nutrient == "fiber" and issue_type == "low":
                # Aumentar la fibra
                if self._has_ingredient_like(recipe, "harina"):
                    flour_key = self._find_ingredient_like(recipe, "harina")
                    if flour_key:
                        flour_amount = optimized[flour_key]
                        
                        # Si no contiene salvado, agregar
                        if not self._has_ingredient_like(recipe, "salvado"):
                            optimized["salvado"] = flour_amount * 0.05
                            recommendations.append("Se agregó salvado para aumentar el contenido de fibra.")
            
            # Más ajustes según sea necesario para otros problemas...
        
        # Agregar recomendaciones generales
        recommendations.append("La receta se ha optimizado para un perfil nutricional equilibrado, con proporciones adecuadas de proteínas, carbohidratos y grasas.")
        
        return optimized, recommendations
    
    def _optimize_for_high_protein(self, recipe: Dict[str, float], issues: List[Dict[str, Any]]) -> Tuple[Dict[str, float], List[str]]:
        """
        Optimiza la receta para un perfil alto en proteínas
        
        Args:
            recipe: Receta original
            issues: Problemas nutricionales identificados
            
        Returns:
            Receta optimizada y recomendaciones
        """
        optimized = recipe.copy()
        recommendations = []
        
        # Implementar lógica para optimizar alto en proteínas
        if self._has_ingredient_like(recipe, "harina"):
            flour_key = self._find_ingredient_like(recipe, "harina")
            if flour_key:
                flour_amount = optimized[flour_key]
                
                # Reducir harina común
                optimized[flour_key] = flour_amount * 0.8
                
                # Agregar fuentes de proteína
                if not self._has_ingredient_like(recipe, "gluten"):
                    optimized["gluten_vital_de_trigo"] = flour_amount * 0.1
                    recommendations.append("Se agregó gluten vital de trigo para aumentar significativamente el contenido proteico.")
                
                if not self._has_ingredient_like(recipe, "semillas"):
                    optimized["semillas_de_girasol"] = flour_amount * 0.05
                    optimized["semillas_de_lino"] = flour_amount * 0.05
                    recommendations.append("Se agregaron semillas de girasol y lino para aumentar el aporte proteico y de ácidos grasos esenciales.")
        
        return optimized, recommendations
    
    def _optimize_for_low_carb(self, recipe: Dict[str, float], issues: List[Dict[str, Any]]) -> Tuple[Dict[str, float], List[str]]:
        """
        Optimiza la receta para un perfil bajo en carbohidratos
        
        Args:
            recipe: Receta original
            issues: Problemas nutricionales identificados
            
        Returns:
            Receta optimizada y recomendaciones
        """
        optimized = recipe.copy()
        recommendations = []
        
        # Implementar lógica para optimizar bajo en carbohidratos
        if self._has_ingredient_like(recipe, "harina"):
            flour_key = self._find_ingredient_like(recipe, "harina")
            if flour_key:
                flour_amount = optimized[flour_key]
                
                # Reducir la cantidad de harina significativamente
                optimized[flour_key] = flour_amount * 0.6
                
                # Agregar alternativas bajas en carbohidratos
                optimized["harina_de_almendra"] = flour_amount * 0.2
                optimized["fibra_de_psyllium"] = flour_amount * 0.05
                optimized["gluten_vital_de_trigo"] = flour_amount * 0.15
                
                recommendations.append("Se reemplazó parte de la harina por harina de almendra, fibra de psyllium y gluten vital para reducir los carbohidratos.")
                recommendations.append("Esta receta tendrá una textura y sabor diferentes a la versión tradicional debido a la reducción de carbohidratos.")
        
        return optimized, recommendations
    
    def _get_food_nutrition(self, food_name: str) -> Dict[str, Any]:
        """
        Obtiene información nutricional de un alimento desde la API de USDA
        
        Args:
            food_name: Nombre del alimento
            
        Returns:
            Datos nutricionales
        """
        if not self.api_key:
            return {}
        
        try:
            # Buscar el alimento
            search_url = f"{self.BASE_URL}/foods/search"
            search_params = {
                "api_key": self.api_key,
                "query": food_name,
                "pageSize": 1
            }
            
            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            search_data = response.json()
            if not search_data.get("foods") or len(search_data["foods"]) == 0:
                return {}
            
            # Obtener el ID del primer resultado
            food_id = search_data["foods"][0]["fdcId"]
            
            # Obtener detalles nutricionales
            food_url = f"{self.BASE_URL}/food/{food_id}"
            food_params = {"api_key": self.api_key}
            
            response = requests.get(food_url, params=food_params, timeout=10)
            response.raise_for_status()
            
            # Procesar y normalizar los datos
            return self._process_nutrition_data(response.json())
            
        except Exception as e:
            logger.error(f"Error al obtener datos nutricionales para {food_name}: {str(e)}")
            return {}
    
    def _process_nutrition_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa y normaliza los datos nutricionales de la API de USDA
        
        Args:
            data: Datos crudos de la API
            
        Returns:
            Datos nutricionales procesados
        """
        result = {
            "name": data.get("description", ""),
            "macronutrients": {},
            "vitamins": {},
            "minerals": {},
            "fiber": 0,
            "calories": 0
        }
        
        # Mapeo de nombres de nutrientes de USDA a nuestras categorías
        nutrient_map = {
            "Protein": ("macronutrients", "protein"),
            "Total lipid (fat)": ("macronutrients", "fat"),
            "Carbohydrate, by difference": ("macronutrients", "carbohydrates"),
            "Fiber, total dietary": ("fiber", None),
            "Energy": ("calories", None),
            # Vitaminas
            "Vitamin A, RAE": ("vitamins", "A"),
            "Vitamin C, total ascorbic acid": ("vitamins", "C"),
            "Vitamin D": ("vitamins", "D"),
            "Vitamin E (alpha-tocopherol)": ("vitamins", "E"),
            "Vitamin K (phylloquinone)": ("vitamins", "K"),
            "Thiamin": ("vitamins", "B1"),
            "Riboflavin": ("vitamins", "B2"),
            "Niacin": ("vitamins", "B3"),
            "Vitamin B-6": ("vitamins", "B6"),
            "Folate, total": ("vitamins", "folate"),
            "Vitamin B-12": ("vitamins", "B12"),
            # Minerales
            "Calcium, Ca": ("minerals", "calcium"),
            "Iron, Fe": ("minerals", "iron"),
            "Magnesium, Mg": ("minerals", "magnesium"),
            "Phosphorus, P": ("minerals", "phosphorus"),
            "Potassium, K": ("minerals", "potassium"),
            "Sodium, Na": ("minerals", "sodium"),
            "Zinc, Zn": ("minerals", "zinc"),
            "Copper, Cu": ("minerals", "copper"),
            "Manganese, Mn": ("minerals", "manganese"),
            "Selenium, Se": ("minerals", "selenium")
        }
        
        # Extraer nutrientes
        if "foodNutrients" in data:
            for nutrient_data in data["foodNutrients"]:
                if "nutrient" in nutrient_data and "amount" in nutrient_data:
                    nutrient_name = nutrient_data["nutrient"].get("name", "")
                    amount = nutrient_data.get("amount", 0)
                    
                    if nutrient_name in nutrient_map:
                        category, subcategory = nutrient_map[nutrient_name]
                        
                        if subcategory:
                            result[category][subcategory] = amount
                        else:
                            result[category] = amount
        
        return result
    
    def _convert_ingredient_name(self, ingredient: str) -> str:
        """
        Convierte el nombre del ingrediente en un formato adecuado para la búsqueda
        
        Args:
            ingredient: Nombre del ingrediente en el formato interno
            
        Returns:
            Nombre del ingrediente adaptado para la búsqueda en la API
        """
        # Mapa de conversión de nombres internos a nombres para búsqueda
        name_map = {
            "harina": "wheat flour",
            "harina_integral": "whole wheat flour",
            "agua": "water",
            "sal": "salt",
            "levadura": "yeast",
            "aceite_de_oliva": "olive oil",
            "azucar": "sugar",
            "mantequilla": "butter",
            "huevo": "egg",
            "leche": "milk",
            "goma_xantana": "xanthan gum",
            "semillas_de_lino": "flaxseed",
            "semillas_de_chia": "chia seeds",
            "semillas_de_girasol": "sunflower seeds",
            "salvado": "wheat bran",
            "harina_de_almendra": "almond flour",
            "gluten_vital_de_trigo": "vital wheat gluten"
        }
        
        # Reemplazar guiones bajos con espacios
        clean_name = ingredient.replace("_", " ")
        
        # Buscar en el mapa de nombres
        if ingredient in name_map:
            return name_map[ingredient]
        
        # Buscar coincidencias parciales
        for internal_name, search_name in name_map.items():
            if internal_name in ingredient:
                return search_name
        
        return clean_name
    
    def _has_ingredient_like(self, recipe: Dict[str, float], partial_name: str) -> bool:
        """
        Verifica si la receta tiene algún ingrediente que contenga el nombre parcial
        
        Args:
            recipe: Receta a verificar
            partial_name: Parte del nombre a buscar
            
        Returns:
            True si encuentra algún ingrediente que contenga el nombre parcial
        """
        for ingredient in recipe.keys():
            if partial_name in ingredient.lower():
                return True
        return False
    
    def _find_ingredient_like(self, recipe: Dict[str, float], partial_name: str) -> str:
        """
        Encuentra el primer ingrediente que coincida con el nombre parcial
        
        Args:
            recipe: Receta a verificar
            partial_name: Parte del nombre a buscar
            
        Returns:
            Nombre completo del ingrediente o cadena vacía si no se encuentra
        """
        for ingredient in recipe.keys():
            if partial_name in ingredient.lower():
                return ingredient
        return "" 