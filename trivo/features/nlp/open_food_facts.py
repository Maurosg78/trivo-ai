#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para interactuar con la API de Open Food Facts.

Este módulo proporciona funciones para buscar y recuperar información 
de productos alimenticios en la base de datos de Open Food Facts.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Union, Tuple

# Configurar logging
logger = logging.getLogger("open_food_facts")

class OpenFoodFactsConnector:
    """Conector para la API de Open Food Facts."""
    
    def __init__(self):
        """Inicializa el conector."""
        self.base_url = "https://world.openfoodfacts.org/api/v0"
        self.search_url = f"{self.base_url}/search"
        self.product_url = f"{self.base_url}/product"
        
        # Referencia de tamaños estándar de productos comunes (datos recopilados de Open Food Facts)
        self.standard_sizes = {
            "pizza": {
                "individual": {"min": 180, "max": 280, "avg": 230, "unit": "g"},
                "mediana": {"min": 300, "max": 450, "avg": 380, "unit": "g"},
                "familiar": {"min": 480, "max": 650, "avg": 550, "unit": "g"},
                "grande": {"min": 700, "max": 1000, "avg": 850, "unit": "g"},
                "extra_grande": {"min": 1100, "max": 1500, "avg": 1300, "unit": "g"}
            },
            "masa_pizza": {
                "individual": {"min": 110, "max": 170, "avg": 140, "unit": "g"},
                "mediana": {"min": 180, "max": 250, "avg": 220, "unit": "g"},
                "familiar": {"min": 280, "max": 380, "avg": 330, "unit": "g"},
                "grande": {"min": 400, "max": 550, "avg": 480, "unit": "g"},
                "extra_grande": {"min": 600, "max": 800, "avg": 700, "unit": "g"}
            },
            "pan": {
                "pequeño": {"min": 200, "max": 300, "avg": 250, "unit": "g"},
                "mediano": {"min": 400, "max": 600, "avg": 500, "unit": "g"},
                "grande": {"min": 700, "max": 1000, "avg": 850, "unit": "g"},
                "hogaza": {"min": 800, "max": 1200, "avg": 1000, "unit": "g"}
            }
        }
        
        # Marcas populares y sus datos (códigos de barras, etc.)
        self.popular_brands = {
            "masa_pizza_hacendado": {
                "barcode": "8480000591241",
                "name": "Masa de pizza fresca redonda",
                "brand": "Hacendado",
                "market": "España",
                "size": "260g",
                "description": "Base de pizza redonda fresca"
            },
            "masa_pizza_buitoni": {
                "barcode": "8410076481466",
                "name": "Masa fresca pizza",
                "brand": "Buitoni",
                "market": "España",
                "size": "260g",
                "description": "Masa fresca de pizza"
            },
            "masa_pizza_tagliatella": {
                "barcode": "8480000059086",
                "name": "Masa de pizza",
                "brand": "La Tagliatella",
                "market": "España",
                "size": "350g",
                "description": "Masa de pizza estilo italiano"
            }
        }
    
    def get_product(self, barcode: str) -> Dict[str, Any]:
        """
        Obtiene información detallada de un producto por su código de barras.
        
        Args:
            barcode: Código de barras del producto
            
        Returns:
            Diccionario con la información del producto
        """
        url = f"{self.product_url}/{barcode}.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == 1:
                logger.info(f"Producto encontrado: {barcode}")
                return data.get("product", {})
            else:
                logger.warning(f"Producto no encontrado: {barcode}")
                return {}
        except Exception as e:
            logger.error(f"Error obteniendo producto {barcode}: {str(e)}")
            return {}
    
    def search_products(self, query: str, category: str = "pizzas", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca productos por nombre o categoría.
        
        Args:
            query: Texto a buscar
            category: Categoría de productos (ej: pizzas, breads)
            limit: Número máximo de resultados
            
        Returns:
            Lista de productos encontrados
        """
        params = {
            "search_terms": query,
            "tagtype_0": "categories",
            "tag_contains_0": "contains",
            "tag_0": category,
            "page_size": limit,
            "json": 1
        }
        
        try:
            response = requests.get(self.search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            products = data.get("products", [])
            if products:
                logger.info(f"Se encontraron {len(products)} productos para '{query}' en la categoría '{category}'")
            else:
                logger.warning(f"No se encontraron productos para '{query}' en la categoría '{category}'")
            
            return products
        except Exception as e:
            logger.error(f"Error buscando productos '{query}': {str(e)}")
            return []
    
    def get_standard_size(self, product_type: str, size_name: str) -> Dict[str, Union[float, str]]:
        """
        Obtiene el tamaño estándar de un producto por su nombre.
        
        Args:
            product_type: Tipo de producto (pizza, masa_pizza, pan)
            size_name: Nombre del tamaño (individual, mediana, familiar, etc.)
            
        Returns:
            Diccionario con información sobre el tamaño estándar
        """
        # Normalizar inputs
        product_type = product_type.lower()
        size_name = size_name.lower()
        
        # Mapeo de términos alternativos
        size_aliases = {
            "small": "individual",
            "personal": "individual",
            "pequeña": "individual",
            "pequeño": "individual",
            "medium": "mediana",
            "family": "familiar",
            "large": "grande",
            "extra large": "extra_grande",
            "xl": "extra_grande",
            "para 2": "mediana",
            "para 3-4": "familiar",
            "para 4": "familiar",
            "para 6": "grande",
            "para 8": "extra_grande"
        }
        
        # Convertir alias a término estándar
        if size_name in size_aliases:
            size_name = size_aliases[size_name]
        
        # Si el tipo de producto no está en nuestra base de datos, usar valores por defecto
        if product_type not in self.standard_sizes:
            if product_type in ["pizza", "focaccia", "flatbread"]:
                product_type = "pizza"
            elif product_type in ["pan", "bread", "baguette", "chapata"]:
                product_type = "pan"
            else:
                product_type = "masa_pizza"
        
        # Si el tamaño no está en nuestra base de datos, usar tamaño familiar por defecto
        if size_name not in self.standard_sizes[product_type]:
            logger.warning(f"Tamaño {size_name} no encontrado para {product_type}, usando 'familiar'")
            size_name = "familiar"
        
        logger.info(f"Tamaño estándar para {product_type} {size_name}: {self.standard_sizes[product_type][size_name]['avg']}{self.standard_sizes[product_type][size_name]['unit']}")
        return self.standard_sizes[product_type][size_name]
    
    def get_scale_multiplier(self, product_type: str, base_size: str, target_size: str) -> float:
        """
        Calcula el multiplicador para escalar una receta de un tamaño a otro.
        
        Args:
            product_type: Tipo de producto (pizza, masa_pizza, pan)
            base_size: Tamaño base de la receta
            target_size: Tamaño objetivo
            
        Returns:
            Multiplicador para escalar la receta
        """
        base = self.get_standard_size(product_type, base_size)
        target = self.get_standard_size(product_type, target_size)
        
        multiplier = target["avg"] / base["avg"]
        logger.info(f"Multiplicador para {product_type} de {base_size} a {target_size}: {multiplier:.2f}")
        return multiplier
    
    def get_commercial_product_info(self, product_name: str) -> Dict[str, Any]:
        """
        Obtiene información de un producto comercial conocido.
        
        Args:
            product_name: Nombre del producto en nuestra base de datos
            
        Returns:
            Información del producto
        """
        if product_name in self.popular_brands:
            info = self.popular_brands[product_name].copy()
            
            # Intentar enriquecer con datos actualizados de OFF
            if 'barcode' in info:
                off_data = self.get_product(info['barcode'])
                if off_data:
                    # Actualizar solo si encontramos datos
                    for key in ['ingredients_text', 'nutriments', 'nutrient_levels']:
                        if key in off_data:
                            info[key] = off_data[key]
            
            return info
        else:
            logger.warning(f"Producto comercial {product_name} no encontrado en la base de datos")
            return {}

# Crear una instancia del conector para uso simple
connector = OpenFoodFactsConnector()

def get_standard_size(product_type: str, size_name: str) -> Dict[str, Union[float, str]]:
    """
    Función auxiliar para obtener el tamaño estándar de un producto.
    
    Args:
        product_type: Tipo de producto (pizza, masa_pizza, pan)
        size_name: Nombre del tamaño (individual, mediana, familiar, etc.)
        
    Returns:
        Diccionario con información sobre el tamaño estándar
    """
    return connector.get_standard_size(product_type, size_name)

def get_scale_multiplier(product_type: str, base_size: str, target_size: str) -> float:
    """
    Función auxiliar para calcular el multiplicador para escalar una receta.
    
    Args:
        product_type: Tipo de producto (pizza, masa_pizza, pan)
        base_size: Tamaño base de la receta
        target_size: Tamaño objetivo
        
    Returns:
        Multiplicador para escalar la receta
    """
    return connector.get_scale_multiplier(product_type, base_size, target_size)

# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Obtener tamaño estándar de un producto
    print("Tamaño estándar de pizza familiar:", get_standard_size("pizza", "familiar"))
    
    # Calcular multiplicador para escalar una receta
    print("Multiplicador para escalar de individual a familiar:", 
          get_scale_multiplier("masa_pizza", "individual", "familiar"))
    
    # Buscar un producto en Open Food Facts
    product = connector.get_product("8480000591241")
    if product:
        print("Producto encontrado:", product.get("product_name", ""))
        print("Tamaño:", product.get("quantity", ""))
        print("Ingredientes:", product.get("ingredients_text", "")) 