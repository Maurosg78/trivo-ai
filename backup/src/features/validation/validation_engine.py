#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Motor de validación para recetas de masas.

Este módulo implementa el motor principal de validación que utiliza las reglas
definidas en validation_rules.py para validar recetas según su tipo y escala.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Importar reglas de validación
from src.features.validation.validation_rules import (
    get_validation_rules, get_rule_by_code, ValidationRule
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("validation_engine")

# Definir estructura para resultados de validación
class ValidationResult:
    """Clase para almacenar resultados de validación."""
    
    def __init__(self, rule_code: str, rule_description: str, 
                 is_valid: bool, severity: str,
                 error_message: Optional[str] = None, 
                 recommendation: Optional[str] = None):
        """
        Inicializa un resultado de validación.
        
        Args:
            rule_code: Código único de la regla que generó este resultado
            rule_description: Descripción de la regla
            is_valid: True si la validación pasó, False si falló
            severity: Nivel de severidad (critical, medium, low)
            error_message: Mensaje de error si la validación falló
            recommendation: Recomendación para solucionar el problema
        """
        self.rule_code = rule_code
        self.rule_description = rule_description
        self.is_valid = is_valid
        self.severity = severity
        self.error_message = error_message
        self.recommendation = recommendation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a un diccionario."""
        return {
            "rule_code": self.rule_code,
            "rule_description": self.rule_description,
            "is_valid": self.is_valid,
            "severity": self.severity,
            "error_message": self.error_message,
            "recommendation": self.recommendation
        }


class ValidationEngine:
    """Motor de validación para recetas."""
    
    def __init__(self, rules: Optional[List[ValidationRule]] = None):
        """
        Inicializa el motor de validación.
        
        Args:
            rules: Lista de reglas de validación a utilizar. Si es None, se cargarán todas.
        """
        self.rules = rules if rules else get_validation_rules()
        logger.info(f"Motor de validación inicializado con {len(self.rules)} reglas")
    
    def validate_recipe(self, recipe: Dict[str, Any], recipe_type: str, 
                        production_scale: str) -> List[ValidationResult]:
        """
        Valida una receta según su tipo y escala de producción.
        
        Args:
            recipe: Diccionario con la receta a validar
            recipe_type: Tipo de receta (pizza, pan, etc.)
            production_scale: Escala de producción (individual, small_business, industrial)
            
        Returns:
            Lista de resultados de validación
        """
        logger.info(f"Validando receta de tipo {recipe_type} para escala {production_scale}")
        results = []
        
        for rule in self.rules:
            try:
                is_valid, error_message, recommendation = rule.validate(
                    recipe, recipe_type, production_scale
                )
                
                result = ValidationResult(
                    rule_code=rule.code,
                    rule_description=rule.description,
                    is_valid=is_valid,
                    severity=rule.severity,
                    error_message=error_message,
                    recommendation=recommendation
                )
                
                results.append(result)
                
                if not is_valid:
                    log_level = logging.ERROR if rule.severity == "critical" else logging.WARNING
                    logger.log(log_level, f"Regla {rule.code} fallida: {error_message}")
            
            except Exception as e:
                logger.error(f"Error al aplicar regla {rule.code}: {str(e)}")
                # Añadir un resultado de error
                results.append(ValidationResult(
                    rule_code=rule.code,
                    rule_description=rule.description,
                    is_valid=False,
                    severity="critical",
                    error_message=f"Error interno: {str(e)}",
                    recommendation="Contacte al equipo de soporte técnico"
                ))
        
        return results
    
    def validate_recipe_from_file(self, file_path: str, recipe_type: str = None,
                                production_scale: str = None) -> Tuple[Dict[str, Any], List[ValidationResult]]:
        """
        Valida una receta desde un archivo.
        
        Args:
            file_path: Ruta al archivo JSON con la receta
            recipe_type: Tipo de receta (opcional, si no está en el archivo)
            production_scale: Escala de producción (opcional, si no está en el archivo)
            
        Returns:
            Tupla con (receta, resultados de validación)
        """
        try:
            # Cargar receta desde archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                recipe_data = json.load(f)
            
            # Extraer información
            recipe = recipe_data.get("ingredients", recipe_data)  # Compatible con diferentes formatos
            
            # Si no se especificó el tipo, intentar obtenerlo del archivo
            if recipe_type is None:
                recipe_type = recipe_data.get("recipe_type", "default")
            
            # Si no se especificó la escala, intentar obtenerla del archivo
            if production_scale is None:
                production_scale = recipe_data.get("production_scale", "individual")
            
            # Validar receta
            results = self.validate_recipe(recipe, recipe_type, production_scale)
            
            return recipe, results
            
        except Exception as e:
            logger.error(f"Error al cargar o validar receta desde archivo: {str(e)}")
            # Crear un resultado de error
            error_result = ValidationResult(
                rule_code="FILE_ERROR",
                rule_description="Error al procesar archivo de receta",
                is_valid=False,
                severity="critical",
                error_message=f"Error al procesar el archivo: {str(e)}",
                recommendation="Verifique que el archivo está en formato JSON válido"
            )
            return {}, [error_result]
    
    def summarize_results(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Genera un resumen de los resultados de validación.
        
        Args:
            results: Lista de resultados de validación
            
        Returns:
            Diccionario con el resumen
        """
        # Contar resultados por severidad
        total_critical_issues = sum(1 for r in results if not r.is_valid and r.severity == "critical")
        total_medium_issues = sum(1 for r in results if not r.is_valid and r.severity == "medium")
        total_low_issues = sum(1 for r in results if not r.is_valid and r.severity == "low")
        
        # Determinar si la receta es viable
        is_viable = total_critical_issues == 0
        
        # Crear reporte
        summary = {
            "is_viable": is_viable,
            "total_rules_checked": len(results),
            "total_issues": sum(1 for r in results if not r.is_valid),
            "issues_by_severity": {
                "critical": total_critical_issues,
                "medium": total_medium_issues,
                "low": total_low_issues
            },
            "recommendations": [r.recommendation for r in results if not r.is_valid and r.recommendation]
        }
        
        return summary
    
    def export_results(self, results: List[ValidationResult], output_file: str) -> bool:
        """
        Exporta los resultados de validación a un archivo JSON.
        
        Args:
            results: Lista de resultados de validación
            output_file: Ruta donde guardar el archivo JSON
            
        Returns:
            True si se pudo guardar correctamente, False en caso contrario
        """
        try:
            results_dict = {
                "validation_results": [r.to_dict() for r in results],
                "summary": self.summarize_results(results)
            }
            
            output_path = Path(output_file)
            output_path.parent.mkdir(exist_ok=True, parents=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Resultados exportados a {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error al exportar resultados: {str(e)}")
            return False


# Función de utilidad para validar rápidamente
def quick_validate_recipe(recipe_file: str, recipe_type: str = None, 
                         production_scale: str = None, 
                         output_file: str = None) -> Dict[str, Any]:
    """
    Función rápida para validar una receta y obtener un resumen.
    
    Args:
        recipe_file: Ruta al archivo JSON con la receta
        recipe_type: Tipo de receta (opcional, si no está en el archivo)
        production_scale: Escala de producción (opcional)
        output_file: Ruta para guardar resultados detallados (opcional)
        
    Returns:
        Diccionario con el resumen de validación
    """
    engine = ValidationEngine()
    recipe, results = engine.validate_recipe_from_file(
        recipe_file, recipe_type, production_scale
    )
    
    summary = engine.summarize_results(results)
    
    # Si se especificó un archivo de salida, exportar resultados detallados
    if output_file:
        engine.export_results(results, output_file)
    
    return summary


# Función para verificar la integridad del motor de validación
def check_system_integrity() -> Dict[str, Any]:
    """
    Verifica que el sistema de validación esté configurado correctamente.
    
    Returns:
        Diccionario con el resultado de la verificación
    """
    try:
        # Verificar que se puedan cargar las reglas
        rules = get_validation_rules()
        
        # Contar reglas por severidad
        critical_rules = sum(1 for r in rules if r.severity == "critical")
        medium_rules = sum(1 for r in rules if r.severity == "medium")
        low_rules = sum(1 for r in rules if r.severity == "low")
        
        # Verificar que existan los directorios necesarios
        data_dir = Path("data")
        reports_dir = Path("reports")
        data_dir.mkdir(exist_ok=True)
        reports_dir.mkdir(exist_ok=True)
        
        # Cargar límites de ingredientes si existen (para ScaleLimitsRule)
        ingredient_limits_count = 0
        for rule in rules:
            if hasattr(rule, "hydration_ranges"):
                ingredient_limits_count = len(rule.hydration_ranges)
        
        # Cargar parámetros de procesos si existen
        process_params_count = 0
        for rule in rules:
            if hasattr(rule, "scale_adjustments"):
                process_params_count = len(rule.scale_adjustments)
        
        return {
            "status": "OK",
            "rules_count": len(rules),
            "rules_by_severity": {
                "critical": critical_rules,
                "medium": medium_rules,
                "low": low_rules
            },
            "ingredient_limits_count": ingredient_limits_count,
            "process_params_count": process_params_count,
            "directories_ready": {
                "data": data_dir.exists(),
                "reports": reports_dir.exists()
            }
        }
        
    except Exception as e:
        logger.error(f"Error en verificación de integridad: {str(e)}")
        return {
            "status": "ERROR",
            "error_message": str(e)
        } 