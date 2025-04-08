#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de validación de recetas para TRIVO-AI.

Este módulo proporciona herramientas para validar recetas de masas
según reglas predefinidas y estándares de producción.
"""

from src.features.validation.validation_engine import (
    ValidationEngine,
    ValidationResult,
    quick_validate_recipe,
    check_system_integrity
)

from src.features.validation.validation_rules import (
    ValidationRule,
    get_validation_rules,
    get_rule_by_code,
    SEVERITY
)

__all__ = [
    'ValidationEngine',
    'ValidationResult',
    'ValidationRule',
    'quick_validate_recipe',
    'check_system_integrity',
    'get_validation_rules',
    'get_rule_by_code',
    'SEVERITY'
]

__version__ = '1.0.0'
__author__ = 'TRIVO-AI'

class ValidationSystem:
    """
    Clase temporal de validación para permitir que la aplicación funcione.
    Será reemplazada por una implementación completa durante el Sprint 4.
    """
    
    def __init__(self):
        """Inicializa el sistema de validación."""
        self.ready = True
        
    def validate_recipe(self, recipe, scale="individual"):
        """
        Método temporal para validar recetas.
        
        Args:
            recipe (dict): Receta a validar
            scale (str): Escala de producción ('individual', 'small_business', 'industrial')
            
        Returns:
            dict: Resultado de la validación
        """
        return {
            "valid": True,
            "errors": [],
            "critical_errors": 0,
            "medium_errors": 0,
            "issues": []
        } 