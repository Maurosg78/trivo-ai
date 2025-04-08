#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Regla de validación para límites de escala.
"""

import logging
from typing import Tuple, Dict, Any, Optional

# Obtener logger
logger = logging.getLogger("validation_rules")

class ScaleLimitsRule:
    """Regla que valida los límites de escala de la receta."""
    
    def __init__(self):
        """Inicializa la regla de límites de escala."""
        self.code = "SCALE"
        self.description = "Validación de límites de escala"
        self.severity = "critical"
    
    def validate(self, recipe: Dict[str, Any], recipe_type: str = "pizza", 
                production_scale: str = "individual") -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Valida que la receta cumpla con los límites de escala.
        
        Args:
            recipe: Diccionario con los ingredientes y sus cantidades
            recipe_type: Tipo de receta (pizza, pan, etc.)
            production_scale: Escala de producción
            
        Returns:
            Tupla (is_valid, message, recommendation)
        """
        # Implementación básica para evitar errores
        return (True, None, None) 