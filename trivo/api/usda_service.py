#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para acceder a la API de USDA (United States Department of Agriculture)
y obtener información nutricional de alimentos.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any, Union
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

class USDAFoodDataService:
    """
    Servicio para acceder a la API de USDA FoodData Central
    y obtener información nutricional de alimentos.
    """
    
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
    
    def __init__(self, api_key: str = None):
        """
        Inicializa el servicio con la clave de API proporcionada o la busca en 
        variables de entorno.
        
        Args:
            api_key: Clave de API para acceder a USDA FoodData Central.
                     Si no se proporciona, se intenta obtener de USDA_API_KEY.
        """
        self.api_key = api_key or os.environ.get("USDA_API_KEY")
        if not self.api_key:
            logger.warning("No se ha proporcionado clave de API para USDA. Algunas funcionalidades estarán limitadas.")
        
        # Crear directorio de caché si no existe
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        
        # Cargar caché existente
        self.cache = self._load_cache()
        
        # Configuración de reintentos para solicitudes API
        self.max_retries = 3
        self.retry_delay = 2  # segundos
        
        # Mapeo de ingredientes en español a inglés
        self.ingredient_translation = {
            # Harinas y granos
            "harina": "wheat flour",
            "harina de trigo": "wheat flour",
            "harina integral": "whole wheat flour",
            "harina de maíz": "corn flour",
            "harina de arroz": "rice flour",
            "almidón de maíz": "corn starch",
            "avena": "oats",
            "salvado": "wheat bran",
            # Lácteos
            "leche": "milk",
            "yogur": "yogurt",
            "queso": "cheese",
            # Grasas
            "aceite": "oil",
            "aceite de oliva": "olive oil",
            "manteca": "lard",
            "mantequilla": "butter",
            # Vegetales
            "espinaca": "spinach",
            "remolacha": "beetroot",
            "zanahoria": "carrot",
            "tomate": "tomato",
            "calabaza": "pumpkin",
            "cebolla": "onion",
            "ajo": "garlic",
            # Semillas
            "semillas de lino": "flaxseed",
            "semillas de chía": "chia seeds",
            "semillas de girasol": "sunflower seeds",
            "semillas de calabaza": "pumpkin seeds",
            # Otros
            "sal": "salt",
            "azúcar": "sugar",
            "levadura": "yeast",
            "agua": "water",
            "miel": "honey",
            "goma xantana": "xanthan gum",
            "carbón activado": "activated charcoal"
        }
    
    def get_food_nutrition(self, food_name: str) -> Dict[str, Any]:
        """
        Obtiene información nutricional para un alimento.
        
        Args:
            food_name: Nombre del alimento a buscar
            
        Returns:
            Diccionario con información nutricional o diccionario vacío si no se encuentra
        """
        # Intentar traducir si está en español
        search_term = self._translate_ingredient(food_name)
        
        # Revisar caché primero
        cache_key = search_term.lower().replace(" ", "_")
        if cache_key in self.cache:
            logger.debug(f"Usando datos en caché para {search_term}")
            return self.cache[cache_key]
        
        # Si no está en caché, consultar la API
        try:
            # Verificar que tenemos clave API
            if not self.api_key:
                logger.warning("No se puede consultar la API USDA sin una clave API")
                return self._get_fallback_data(search_term)
                
            # Buscar el alimento
            food_id = self._search_food(search_term)
            if not food_id:
                logger.warning(f"No se encontró {search_term} en la base de datos USDA")
                return self._get_fallback_data(search_term)
            
            # Obtener detalles del alimento
            food_data = self._get_food_details(food_id)
            
            # Guardar en caché
            if food_data:
                self.cache[cache_key] = food_data
                self._save_cache()
                return food_data
            else:
                return self._get_fallback_data(search_term)
        
        except Exception as e:
            logger.error(f"Error al obtener información nutricional para {food_name}: {str(e)}")
            return self._get_fallback_data(search_term)
    
    def _translate_ingredient(self, ingredient_name: str) -> str:
        """Traduce nombres de ingredientes de español a inglés para la API USDA"""
        lower_name = ingredient_name.lower()
        
        # Buscar coincidencias exactas
        if lower_name in self.ingredient_translation:
            return self.ingredient_translation[lower_name]
        
        # Buscar coincidencias parciales
        for spanish, english in self.ingredient_translation.items():
            if spanish in lower_name:
                return english
        
        # Si no hay coincidencia, devolver el nombre original
        return ingredient_name
    
    def _search_food(self, query: str) -> Optional[str]:
        """
        Busca un alimento en la base de datos de USDA y devuelve su ID.
        
        Args:
            query: Término de búsqueda
            
        Returns:
            ID del primer resultado de búsqueda o None si no hay resultados
        """
        url = f"{self.BASE_URL}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "dataType": ["Foundation", "SR Legacy"],
            "pageSize": 1
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data.get("foods") and len(data["foods"]) > 0:
                    return data["foods"][0]["fdcId"]
                return None
            
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                logger.warning(f"Intento {attempt+1}/{self.max_retries} fallido al buscar alimento '{query}': {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Backoff exponencial
                else:
                    logger.error(f"Error al buscar alimento '{query}' después de {self.max_retries} intentos")
        
        return None
    
    def _get_food_details(self, food_id: str) -> Dict[str, Any]:
        """
        Obtiene detalles nutricionales para un alimento por su ID.
        
        Args:
            food_id: ID del alimento en USDA
            
        Returns:
            Diccionario con información nutricional
        """
        url = f"{self.BASE_URL}/food/{food_id}"
        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return self._parse_food_data(response.json())
        
        except Exception as e:
            logger.error(f"Error al obtener detalles de alimento ID {food_id}: {str(e)}")
            # Si hay un error de API, esperar un momento antes de reintentar
            time.sleep(1)
            return {}
    
    def _parse_food_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza los datos de alimentos de USDA y los convierte al formato interno.
        
        Args:
            data: Datos crudos de la API de USDA
            
        Returns:
            Diccionario con datos nutricionales en formato interno
        """
        result = {
            "name": data.get("description", ""),
            "serving_size": data.get("servingSizeAmount", 100),
            "serving_unit": data.get("servingSizeUnit", "g"),
            "macronutrients": {},
            "micronutrients": {},
            "vitamins": {},
            "minerals": {},
            "fiber": 0.0,
            "calories": 0.0
        }
        
        # Mapeo de nutrientes USDA a categorías internas
        nutrient_map = {
            # Macronutrientes
            "Protein": ("macronutrients", "protein"),
            "Total lipid (fat)": ("macronutrients", "fat"),
            "Carbohydrate, by difference": ("macronutrients", "carbohydrates"),
            "Fiber, total dietary": ("fiber", None),
            "Energy": ("calories", None),
            
            # Vitaminas
            "Vitamin A, RAE": ("vitamins", "vitamin_a"),
            "Vitamin E (alpha-tocopherol)": ("vitamins", "vitamin_e"),
            "Vitamin D (D2 + D3)": ("vitamins", "vitamin_d"),
            "Vitamin C, total ascorbic acid": ("vitamins", "vitamin_c"),
            "Vitamin B-6": ("vitamins", "vitamin_b6"),
            "Vitamin B-12": ("vitamins", "vitamin_b12"),
            "Folate, total": ("vitamins", "folate"),
            "Vitamin K (phylloquinone)": ("vitamins", "vitamin_k"),
            
            # Minerales
            "Calcium, Ca": ("minerals", "calcium"),
            "Iron, Fe": ("minerals", "iron"),
            "Magnesium, Mg": ("minerals", "magnesium"),
            "Phosphorus, P": ("minerals", "phosphorus"),
            "Potassium, K": ("minerals", "potassium"),
            "Sodium, Na": ("minerals", "sodium"),
            "Zinc, Zn": ("minerals", "zinc"),
            "Copper, Cu": ("minerals", "copper"),
            "Selenium, Se": ("minerals", "selenium")
        }
        
        # Procesar nutrientes
        for nutrient in data.get("foodNutrients", []):
            if not nutrient.get("nutrient"):
                continue
                
            nutrient_name = nutrient["nutrient"].get("name", "")
            amount = nutrient.get("amount", 0)
            unit = nutrient["nutrient"].get("unitName", "")
            
            if nutrient_name in nutrient_map:
                category, key = nutrient_map[nutrient_name]
                
                if category in ["fiber", "calories"]:
                    result[category] = amount
                elif category in result and key:
                    result[category][key] = {
                        "amount": amount,
                        "unit": unit
                    }
        
        return result
    
    def _load_cache(self) -> Dict[str, Any]:
        """Carga la caché desde el archivo"""
        cache_path = os.path.join(self.CACHE_DIR, "usda_cache.json")
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error al cargar caché: {str(e)}")
        return {}
    
    def _save_cache(self) -> None:
        """Guarda la caché en un archivo"""
        cache_path = os.path.join(self.CACHE_DIR, "usda_cache.json")
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Error al guardar caché: {str(e)}")
    
    def clear_cache(self) -> None:
        """Limpia la caché"""
        self.cache = {}
        self._save_cache()
    
    def _get_fallback_data(self, food_name: str) -> Dict[str, Any]:
        """
        Proporciona datos nutricionales básicos de respaldo cuando la API falla.
        
        Args:
            food_name: Nombre del alimento
            
        Returns:
            Diccionario con datos nutricionales básicos estimados
        """
        # Datos de respaldo básicos para ingredientes comunes
        fallback_data = {
            "wheat flour": {
                "name": "Wheat flour",
                "serving_size": 100,
                "serving_unit": "g",
                "macronutrients": {"protein": 10.0, "fat": 1.0, "carbohydrates": 76.0},
                "calories": 364.0,
                "fiber": 2.7
            },
            "water": {
                "name": "Water",
                "serving_size": 100,
                "serving_unit": "g",
                "macronutrients": {"protein": 0.0, "fat": 0.0, "carbohydrates": 0.0},
                "calories": 0.0,
                "fiber": 0.0
            },
            "salt": {
                "name": "Salt",
                "serving_size": 100,
                "serving_unit": "g",
                "macronutrients": {"protein": 0.0, "fat": 0.0, "carbohydrates": 0.0},
                "calories": 0.0,
                "fiber": 0.0
            },
            "yeast": {
                "name": "Yeast",
                "serving_size": 100,
                "serving_unit": "g",
                "macronutrients": {"protein": 40.0, "fat": 7.6, "carbohydrates": 41.0},
                "calories": 325.0,
                "fiber": 26.9
            },
            "olive oil": {
                "name": "Olive oil",
                "serving_size": 100,
                "serving_unit": "g",
                "macronutrients": {"protein": 0.0, "fat": 100.0, "carbohydrates": 0.0},
                "calories": 884.0,
                "fiber": 0.0
            }
        }
        
        # Buscar el alimento en datos de respaldo
        for key, data in fallback_data.items():
            if key in food_name.lower():
                logger.info(f"Usando datos de respaldo para {food_name}")
                return data
        
        # Si no hay datos específicos, devolver plantilla genérica
        return {
            "name": food_name,
            "serving_size": 100,
            "serving_unit": "g",
            "macronutrients": {"protein": 0.0, "fat": 0.0, "carbohydrates": 0.0},
            "micronutrients": {},
            "vitamins": {},
            "minerals": {},
            "fiber": 0.0,
            "calories": 0.0
        } 