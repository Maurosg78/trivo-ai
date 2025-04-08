#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Regla de validación para la hidratación de la masa.
"""

import logging
from typing import Tuple, Dict, Any, List, Optional

# Obtener logger
logger = logging.getLogger("validation_rules")

class HydrationRule:
    """Regla que valida la hidratación de la masa."""
    
    def __init__(self):
        """Inicializa la regla de hidratación."""
        self.code = "HYDRATION"
        self.description = "Validación de hidratación de la masa"
        self.severity = "critical"
    
    def validate(self, recipe: Dict[str, Any], recipe_type: str = "pizza", 
                production_scale: str = "individual") -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Valida que la hidratación de la masa sea adecuada.
        
        Args:
            recipe: Diccionario con los ingredientes y sus cantidades
            recipe_type: Tipo de receta (pizza, pan, etc.)
            production_scale: Escala de producción
            
        Returns:
            Tupla (is_valid, message, recommendation)
        """
        # PARTE 1: DETECTAR RECETA SIN GLUTEN
        is_gluten_free = False
        
        # Paso 1: Verificar flag explícito
        if recipe.get('es_sin_gluten') is True:
            is_gluten_free = True
            logger.info(f"HydrationRule: Detectada receta sin gluten por flag explícito")
        
        # Paso 2: Si no hay flag, verificar ingredientes
        if not is_gluten_free:
            gluten_free_keywords = ['arroz', 'maiz', 'patata', 'xantana', 'quinoa', 'sorgo', 'mijo', 'amaranto', 
                                  'alforfon', 'garbanzo', 'psyllium', 'chia']
            
            for ingredient in recipe.keys():
                if not isinstance(ingredient, str):
                    continue
                
                ingredient_lower = ingredient.lower()
                for keyword in gluten_free_keywords:
                    if keyword in ingredient_lower:
                        is_gluten_free = True
                        logger.info(f"HydrationRule: Detectada receta sin gluten por ingrediente: {ingredient}")
                        break
                if is_gluten_free:
                    break
        
        # PARTE 2: CALCULAR HIDRATACIÓN
        total_flour = 0.0
        total_water = 0.0
        
        # Calcular totales
        for ingredient, amount in recipe.items():
            if not isinstance(ingredient, str) or ingredient == 'es_sin_gluten':
                continue
                
            try:
                amount_float = float(amount)
            except (ValueError, TypeError):
                logger.warning(f"HydrationRule: No se pudo convertir {amount} a número para {ingredient}")
                continue
                
            ingredient_lower = ingredient.lower()
            
            # Ingredientes de harina
            if any(flour_type in ingredient_lower for flour_type in [
                'harina', 'flour', 'almidon', 'fecula', 'starch'
            ]):
                total_flour += amount_float
            
            # Ingredientes líquidos
            elif any(liquid_type in ingredient_lower for liquid_type in [
                'agua', 'water', 'leche', 'milk', 'suero', 'whey'
            ]):
                # El agua y líquidos similares cuentan al 100%
                total_water += amount_float
            elif any(liquid_type in ingredient_lower for liquid_type in [
                'huevo', 'egg', 'yema', 'clara', 'yolk', 'white'
            ]):
                # Los huevos son aproximadamente 75% agua
                total_water += amount_float * 0.75
            elif any(liquid_type in ingredient_lower for liquid_type in [
                'yogur', 'yogurt', 'yoghurt', 'kefir'
            ]):
                # El yogur es aproximadamente 85% agua
                total_water += amount_float * 0.85
            elif any(liquid_type in ingredient_lower for liquid_type in [
                'miel', 'honey', 'jarabe', 'syrup'
            ]):
                # La miel y similares son aproximadamente 17% agua
                total_water += amount_float * 0.17
        
        # Evitar divisiones por cero
        if total_flour == 0:
            return (False, "No se detectaron ingredientes de harina en la receta", 
                  "Añade harina a la receta, es un ingrediente esencial")
        
        # Calcular hidratación como porcentaje
        hydration_percentage = (total_water / total_flour) * 100
        logger.info(f"HydrationRule: Hidratación calculada: {hydration_percentage:.1f}%")
        
        # PARTE 3: DETERMINAR LÍMITES DE HIDRATACIÓN
        # Parámetros base para la hidratación
        min_hydration = 50.0  # 50% mínimo para cualquier masa
        max_hydration = 65.0  # 65% máximo para masas estándar
        
        # Ajustar parámetros según tipo de receta y si es sin gluten
        if is_gluten_free:
            # Las masas sin gluten necesitan más hidratación
            logger.info("HydrationRule: Aplicando límites de hidratación para masa sin gluten")
            min_hydration = 45.0  # Pueden ser más secas
            max_hydration = 85.0  # Masas sin gluten necesitan más hidratación
        elif recipe_type == "pizza":
            if "napo" in str(recipe.get("estilo", "")).lower():
                # Pizza napolitana tiene mayor hidratación
                max_hydration = 70.0
        elif recipe_type == "pan":
            # Los panes suelen tener mayor hidratación
            max_hydration = 75.0
            if "sourdough" in str(recipe.get("estilo", "")).lower() or "masa_madre" in str(recipe.get("estilo", "")).lower():
                # Panes de masa madre tienen mayor hidratación
                max_hydration = 85.0
        
        logger.info(f"HydrationRule: Límites de hidratación: min={min_hydration:.1f}%, max={max_hydration:.1f}%")
        
        # PARTE 4: VALIDAR HIDRATACIÓN
        if hydration_percentage > max_hydration:
            message = f"Hidratación demasiado alta ({hydration_percentage:.1f}%). Máximo recomendado: {max_hydration:.1f}%"
            recommendation = f"Reduce la cantidad de líquidos o aumenta la harina. El ratio ideal es {((min_hydration + max_hydration) / 2):.1f}%"
            return (False, message, recommendation)
        
        if hydration_percentage < min_hydration:
            message = f"Hidratación demasiado baja ({hydration_percentage:.1f}%). Mínimo recomendado: {min_hydration:.1f}%"
            recommendation = f"Aumenta la cantidad de agua a aproximadamente {(min_hydration * total_flour / 100):.0f} g"
            return (False, message, recommendation)
        
        return (True, None, None) 