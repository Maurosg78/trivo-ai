#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Servicio de recomendaciones para integración con el sistema de validación.

Este servicio conecta las recomendaciones contextuales con los resultados
de validación, proporcionando sugerencias específicas según el contexto
de la receta y los problemas detectados.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Importar solo lo necesario del módulo de recomendaciones
from src.features.recommendations.knowledge_base import (
    RecommendationCache, 
    get_contextual_recommendation,
    verify_recommendation_coherence
)

# Configuración de logging
logger = logging.getLogger("recommendation_service")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Mapa de códigos de validación a problemas para recomendaciones
VALIDATION_CODE_TO_ISSUE = {
    # Hidratación
    "HYDRATION_01_LOW": {
        "issue": "hidratacion_baja", 
        "pattern": "demasiado baja",
        "context": {"key": "hydration_level", "value": "low"}
    },
    "HYDRATION_01_HIGH": {
        "issue": "hidratacion_alta", 
        "pattern": "demasiado alta",
        "context": {"key": "hydration_level", "value": "high"}
    },
    
    # Sal
    "SALT_01_LOW": {
        "issue": "sal_baja", 
        "pattern": "demasiado baja",
        "context": {"key": "salt_level", "value": "low"}
    },
    "SALT_01_HIGH": {
        "issue": "sal_alta", 
        "pattern": "demasiado alta",
        "context": {"key": "salt_level", "value": "high"}
    },
    
    # Levadura
    "YEAST_01_MISSING": {
        "issue": "falta_levadura", 
        "pattern": "No se encontró levadura",
        "context": {"key": "has_yeast", "value": False}
    },
    "YEAST_01_HIGH": {
        "issue": "exceso_levadura", 
        "pattern": "demasiado alta",
        "context": {"key": "yeast_level", "value": "high"}
    },
    
    # Fermentación
    "FERMENTATION_01_HIGH": {
        "issue": "fermentacion_alta", 
        "pattern": "Temperatura de fermentación demasiado alta",
        "context": {"key": "fermentation_temp", "value": "high"}
    },
    "FERMENTATION_01_LOW": {
        "issue": "fermentacion_baja", 
        "pattern": "Temperatura de fermentación demasiado baja",
        "context": {"key": "fermentation_temp", "value": "low"}
    },
    "FERMENTATION_01_SHORT": {
        "issue": "tiempo_fermentacion_corto", 
        "pattern": "Tiempo de fermentación demasiado corto",
        "context": {"key": "fermentation_time", "value": "short"}
    },
    
    # Generalidades
    "DENSITY_ISSUE": {
        "issue": "densidad_alta",
        "pattern": "densidad",
        "context": {"key": "density", "value": "high"}
    },
    "COOKING_ISSUE": {
        "issue": "coccion_inadecuada",
        "pattern": "cocción",
        "context": {"key": "cooking", "value": "inadequate"}
    }
}

class RecommendationService:
    """Servicio para generar recomendaciones basadas en resultados de validación."""
    
    def __init__(self, cache_dir=None):
        """
        Inicializa el servicio de recomendaciones.
        
        Args:
            cache_dir: Directorio para almacenar la caché de recomendaciones.
        """
        self.cache_file = None
        if cache_dir:
            try:
                os.makedirs(cache_dir, exist_ok=True)
                self.cache_file = os.path.join(cache_dir, "recommendations_cache.json")
            except Exception as e:
                logger.error(f"Error al crear directorio de caché: {str(e)}")
        
        try:
            self.cache = RecommendationCache(cache_file=self.cache_file)
            logger.info(f"Servicio de recomendaciones inicializado, caché: {self.cache_file}")
        except Exception as e:
            logger.error(f"Error al inicializar caché: {str(e)}")
            self.cache = None
    
    def get_recipe_context(self, recipe: Dict[str, Any], recipe_type: str, scale: str) -> Dict[str, Any]:
        """
        Extrae el contexto de una receta para generar recomendaciones.
        
        Args:
            recipe: Diccionario con datos de la receta
            recipe_type: Tipo de receta (pizza, pan, etc.)
            scale: Escala de producción
            
        Returns:
            Diccionario con contexto extraído
        """
        context = {
            "recipe_type": recipe_type,
            "scale": scale,
            "has_gluten": True,
            "has_yeast": False,
            "dietary_restrictions": [],
            "oven_type": "horno_convencional"
        }
        
        try:
            # Detectar gluten
            gluten_free_flours = [
                "harina de arroz", "harina arroz", "almidón de maíz", "almidon maiz",
                "fécula de patata", "fecula patata", "harina sin gluten", "tapioca",
                "harina de quinoa", "harina quinoa", "harina de almendra", "harina almendra"
            ]
            
            # Comprobar si es sin gluten
            has_wheat_flour = "harina" in recipe or "harina de trigo" in recipe
            has_gluten_free_flour = any(flour in str(recipe).lower() for flour in gluten_free_flours)
            
            if has_gluten_free_flour and not (has_wheat_flour and not has_gluten_free_flour):
                context["has_gluten"] = False
                context["dietary_restrictions"].append("sin_gluten")
            
            # Detectar levadura
            yeast_terms = ["levadura", "masa madre", "sourdough", "starter"]
            if any(term in str(recipe).lower() for term in yeast_terms):
                context["has_yeast"] = True
            
            # Detectar restricciones dietéticas
            if "vegano" in str(recipe).lower() or "vegan" in str(recipe).lower():
                context["dietary_restrictions"].append("vegano")
            
            if "sin_lactosa" in str(recipe).lower() or "sin lactosa" in str(recipe).lower():
                context["dietary_restrictions"].append("sin_lactosa")
            
            # Detectar tipo de horno si está especificado
            if "piedra" in str(recipe).lower() or "pizza horno" in str(recipe).lower():
                context["oven_type"] = "horno_pizza"
            elif "conveccion" in str(recipe).lower() or "convección" in str(recipe).lower():
                context["oven_type"] = "horno_conveccion"
            elif "sarten" in str(recipe).lower() or "sartén" in str(recipe).lower():
                context["oven_type"] = "sarten_horno"
        except Exception as e:
            logger.error(f"Error al extraer contexto de receta: {str(e)}")
        
        return context
    
    def identify_issues_from_validation(
        self, 
        validation_results: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Identifica problemas a partir de resultados de validación.
        
        Args:
            validation_results: Lista de resultados de validación 
                                (deben tener atributos rule_code, is_valid, error_message)
            
        Returns:
            Lista de problemas identificados con contexto
        """
        issues = []
        
        try:
            # Verificar que son objetos de resultado de validación
            valid_results = []
            for result in validation_results:
                if hasattr(result, 'rule_code') and hasattr(result, 'is_valid') and hasattr(result, 'error_message'):
                    valid_results.append(result)
                else:
                    logger.warning(f"Objeto de validación no válido: {type(result)}")
            
            # Filtrar resultados fallidos primero
            failed_results = [r for r in valid_results if not r.is_valid]
            
            # Buscar coincidencias en el mapa de códigos
            for result in failed_results:
                # Crear claves específicas para búsqueda
                search_keys = [
                    result.rule_code,  # Código exacto
                    f"{result.rule_code}_LOW",  # Variantes
                    f"{result.rule_code}_HIGH",
                    f"{result.rule_code}_MISSING",
                    f"{result.rule_code}_SHORT"
                ]
                
                # Buscar en cada clave
                matched = False
                for search_key in search_keys:
                    if search_key in VALIDATION_CODE_TO_ISSUE:
                        issue_map = VALIDATION_CODE_TO_ISSUE[search_key]
                        # Verificar patrón para determinar subtipo del problema
                        if issue_map["pattern"] in result.error_message:
                            issues.append({
                                "issue": issue_map["issue"],
                                "context": issue_map["context"],
                                "validation_result": result
                            })
                            matched = True
                            break
                
                # Si no hay coincidencia por código, buscar por patrones generales
                if not matched:
                    for code, issue_map in VALIDATION_CODE_TO_ISSUE.items():
                        if issue_map["pattern"] in result.error_message.lower():
                            issues.append({
                                "issue": issue_map["issue"],
                                "context": issue_map["context"],
                                "validation_result": result
                            })
                            matched = True
                            break
            
            # Detectar problemas generales
            has_density_issue = any("densidad" in r.error_message.lower() for r in failed_results)
            if has_density_issue:
                issues.append({
                    "issue": "densidad_alta",
                    "context": {"key": "density", "value": "high"},
                    "validation_result": None
                })
            
            has_cooking_issue = any("cocción" in r.error_message.lower() or "temperatura" in r.error_message.lower() for r in failed_results)
            if has_cooking_issue:
                issues.append({
                    "issue": "coccion_inadecuada",
                    "context": {"key": "cooking", "value": "inadequate"},
                    "validation_result": None
                })
        except Exception as e:
            logger.error(f"Error al identificar problemas: {str(e)}")
        
        return issues
    
    def generate_recommendations_for_validation(
        self,
        validation_results: List[Any],
        recipe: Dict[str, Any],
        recipe_type: str,
        scale: str
    ) -> Dict[str, Any]:
        """
        Genera recomendaciones contextuales basadas en resultados de validación.
        
        Args:
            validation_results: Lista de resultados de validación
            recipe: Receta validada
            recipe_type: Tipo de receta
            scale: Escala de producción
            
        Returns:
            Recomendaciones contextuales generadas
        """
        try:
            # Extraer contexto de la receta
            recipe_context = self.get_recipe_context(recipe, recipe_type, scale)
            
            # Identificar problemas
            issues = self.identify_issues_from_validation(validation_results)
            
            # Si no hay problemas detectados, devolver mensaje genérico
            if not issues:
                return {
                    "issues_found": False,
                    "message": "No se detectaron problemas que requieran recomendaciones específicas.",
                    "recommendations": []
                }
            
            # Generar recomendaciones para cada problema
            all_recommendations = []
            
            for issue in issues:
                try:
                    recs = get_contextual_recommendation(
                        issue=issue["issue"],
                        recipe_type=recipe_type,
                        has_gluten=recipe_context["has_gluten"],
                        has_yeast=recipe_context["has_yeast"],
                        dietary_restrictions=recipe_context["dietary_restrictions"],
                        oven_type=recipe_context["oven_type"],
                        cache=self.cache
                    )
                    
                    # Verificar coherencia
                    coherent, coherence_issues = verify_recommendation_coherence(recs, recipe_context)
                    
                    if not coherent:
                        logger.warning(f"Detectadas recomendaciones incoherentes: {coherence_issues}")
                        # Intentar generar nuevas recomendaciones si son incoherentes
                        # Aquí podríamos implementar un mecanismo de corrección o feedback
                    
                    all_recommendations.append({
                        "issue": issue["issue"],
                        "recommendations": recs,
                        "coherent": coherent,
                        "coherence_issues": coherence_issues
                    })
                except Exception as e:
                    logger.error(f"Error al generar recomendaciones para problema {issue['issue']}: {str(e)}")
            
            # Consolidar resultados
            consolidated = {
                "issues_found": True,
                "recipe_context": recipe_context,
                "timestamp": datetime.now().isoformat(),
                "issues": [i["issue"] for i in issues],
                "all_recommendations": all_recommendations,
                "combined_recommendations": self._consolidate_recommendations(all_recommendations, recipe_context)
            }
            
            return consolidated
        except Exception as e:
            logger.error(f"Error general al generar recomendaciones: {str(e)}")
            return {
                "issues_found": False,
                "error": str(e),
                "message": "Error al generar recomendaciones.",
                "recommendations": []
            }
    
    def _consolidate_recommendations(
        self, 
        all_recommendations: List[Dict[str, Any]],
        recipe_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Consolida múltiples recomendaciones, eliminando duplicados y agrupando por tipo.
        
        Args:
            all_recommendations: Lista de recomendaciones por problema
            recipe_context: Contexto de la receta
            
        Returns:
            Recomendaciones consolidadas
        """
        result = {
            "general": [],
            "techniques": [],
            "substitutions": [],
            "equipment": []
        }
        
        try:
            # Conjuntos para evitar duplicados
            seen_general = set()
            seen_techniques = set()
            seen_substitutions = set()
            seen_equipment = set()
            
            for rec_set in all_recommendations:
                recs = rec_set["recommendations"]
                
                # Procesar recomendaciones generales
                for rec in recs["recommendations"]:
                    if rec not in seen_general:
                        result["general"].append(rec)
                        seen_general.add(rec)
                
                # Procesar técnicas
                for technique in recs["techniques"]:
                    if technique not in seen_techniques:
                        result["techniques"].append(technique)
                        seen_techniques.add(technique)
                
                # Procesar sustituciones
                for sub in recs["substitutions"]:
                    # Crear clave única para la sustitución
                    sub_key = f"{sub['original']}:{','.join(sub['alternatives'])}"
                    if sub_key not in seen_substitutions:
                        result["substitutions"].append(sub)
                        seen_substitutions.add(sub_key)
                
                # Procesar equipamiento
                for equip in recs["equipment"]:
                    if equip not in seen_equipment:
                        result["equipment"].append(equip)
                        seen_equipment.add(equip)
        except Exception as e:
            logger.error(f"Error al consolidar recomendaciones: {str(e)}")
        
        return result


# Ejemplo de uso del servicio
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Crear servicio
    service = RecommendationService(cache_dir="./cache")
    
    # Crear resultados simulados de validación
    class MockValidationResult:
        def __init__(self, rule_code, is_valid, error_message=""):
            self.rule_code = rule_code
            self.is_valid = is_valid
            self.error_message = error_message
    
    mock_results = [
        MockValidationResult("HYDRATION_01", False, "Hidratación demasiado baja (45.0%). Mínimo recomendado: 55.0%"),
        MockValidationResult("YEAST_01", False, "No se encontró levadura ni masa madre en la receta")
    ]
    
    # Ejemplo de receta sin gluten
    recipe = {
        "harina de arroz": 400,
        "almidon de tapioca": 100,
        "agua": 350,
        "sal": 10,
        "goma xantana": 5,
        "aceite_oliva": 20
    }
    
    # Generar recomendaciones
    recommendations = service.generate_recommendations_for_validation(
        mock_results,
        recipe,
        "pizza",
        "individual"
    )
    
    # Mostrar resultados
    print(json.dumps(recommendations, indent=2, ensure_ascii=False)) 