#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo que define las reglas de validación para diferentes tipos de masa.

Este módulo contiene reglas específicas para validar recetas según el tipo
de masa, escala de producción y restricciones especiales.
"""

import os
from typing import Dict, List, Any, Tuple, Callable, Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Categorías de severidad para errores de validación
SEVERITY = {
    "CRITICAL": "critical",  # Errores que hacen la receta inviable
    "MEDIUM": "medium",      # Problemas importantes pero no críticos
    "LOW": "low"             # Sugerencias o mejoras menores
}

# Estructura base para reglas de validación
# Cada regla es una función que recibe la receta y devuelve (es_válido, mensaje, recomendación)
class ValidationRule:
    """Clase base para las reglas de validación."""
    
    def __init__(self, code: str, description: str, severity: str = SEVERITY["MEDIUM"]):
        """
        Inicializa una regla de validación.
        
        Args:
            code: Código único identificador de la regla
            description: Descripción breve de lo que valida la regla
            severity: Nivel de severidad si la regla falla (critical, medium, low)
        """
        self.code = code
        self.description = description
        self.severity = severity
    
    def validate(self, recipe: Dict[str, float], recipe_type: str, 
                production_scale: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Valida una receta según la regla.
        
        Args:
            recipe: Diccionario con ingredientes y cantidades
            recipe_type: Tipo de receta (pizza, pan, etc.)
            production_scale: Escala de producción (individual, small_business, industrial)
            
        Returns:
            Tupla con (es_válido, mensaje_de_error, recomendación)
        """
        # Esta es una implementación base que debe ser sobreescrita por las clases hijas
        return True, None, None


# Reglas de validación específicas

class HydrationRatioRule(ValidationRule):
    """Valida que la hidratación esté dentro de los rangos aceptables según el tipo de masa."""
    
    def __init__(self):
        super().__init__(
            code="HYDRATION_01",
            description="Validar ratio de hidratación para este tipo de masa",
            severity=SEVERITY["CRITICAL"]
        )
        
        # Rangos de hidratación óptimos por tipo de receta y escala
        self.hydration_ranges = {
            "pizza": {
                "napolitana": {"min": 60.0, "max": 65.0, "ideal": 62.0},
                "new_york": {"min": 55.0, "max": 60.0, "ideal": 58.0},
                "chicago": {"min": 50.0, "max": 58.0, "ideal": 55.0},
                "default": {"min": 55.0, "max": 65.0, "ideal": 60.0}
            },
            "pan": {
                "chapata": {"min": 75.0, "max": 90.0, "ideal": 80.0},
                "baguette": {"min": 65.0, "max": 75.0, "ideal": 70.0},
                "masa_madre": {"min": 70.0, "max": 85.0, "ideal": 75.0},
                "default": {"min": 65.0, "max": 75.0, "ideal": 68.0}
            },
            "flatbread": {
                "focaccia": {"min": 70.0, "max": 80.0, "ideal": 75.0},
                "default": {"min": 55.0, "max": 70.0, "ideal": 65.0}
            },
            "brioche": {
                "default": {"min": 50.0, "max": 60.0, "ideal": 55.0}
            },
            "croissant": {
                "default": {"min": 45.0, "max": 55.0, "ideal": 50.0}
            },
            "pasta_fresca": {
                "default": {"min": 30.0, "max": 40.0, "ideal": 35.0}
            },
            "default": {"min": 55.0, "max": 70.0, "ideal": 65.0}
        }
        
        # Ajustes por escala
        self.scale_adjustments = {
            "individual": {"min": 0.0, "max": 0.0},  # No ajuste
            "small_business": {"min": -2.0, "max": 2.0},  # ±2% para negocios pequeños
            "industrial": {"min": -5.0, "max": 0.0}  # Industrial tiende a menos hidratación
        }
    
    def validate(self, recipe: Dict[str, float], recipe_type: str, 
                production_scale: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Valida la hidratación de la receta."""
        # Determinar subcategoría si está presente en la receta
        # Por ejemplo, "pizza_napolitana" -> "napolitana"
        subcategory = None
        for key in recipe:
            if key.startswith("tipo_") and recipe[key]:
                subcategory = key.replace("tipo_", "")
                break
        
        # Calcular hidratación
        flour_amount = sum(recipe.get(key, 0) for key in recipe if "harina" in key.lower())
        liquid_amount = sum(recipe.get(key, 0) for key in ["agua", "leche", "yogur", "huevo", "aceite_oliva", "aceite"])
        
        if flour_amount == 0:
            return False, "No se encontró harina en la receta", "Añade al menos un tipo de harina a la receta"
        
        hydration_ratio = (liquid_amount / flour_amount) * 100.0
        
        # Obtener rangos según tipo y subcategoría
        if recipe_type in self.hydration_ranges:
            type_ranges = self.hydration_ranges[recipe_type]
            if subcategory and subcategory in type_ranges:
                ranges = type_ranges[subcategory]
            else:
                ranges = type_ranges.get("default", self.hydration_ranges["default"])
        else:
            ranges = self.hydration_ranges["default"]
        
        # Ajustar por escala
        scale_adj = self.scale_adjustments.get(production_scale, {"min": 0.0, "max": 0.0})
        min_hydration = ranges["min"] + scale_adj["min"]
        max_hydration = ranges["max"] + scale_adj["max"]
        ideal_hydration = ranges["ideal"]
        
        # Validar
        if hydration_ratio < min_hydration:
            return False, f"Hidratación demasiado baja ({hydration_ratio:.1f}%). Mínimo recomendado: {min_hydration:.1f}%", \
                   f"Aumenta la cantidad de líquidos o reduce la harina. El ratio ideal es {ideal_hydration:.1f}%"
        
        if hydration_ratio > max_hydration:
            return False, f"Hidratación demasiado alta ({hydration_ratio:.1f}%). Máximo recomendado: {max_hydration:.1f}%", \
                   f"Reduce la cantidad de líquidos o aumenta la harina. El ratio ideal es {ideal_hydration:.1f}%"
        
        return True, None, None


class SaltRatioRule(ValidationRule):
    """Valida que la proporción de sal esté dentro de los límites adecuados."""
    
    def __init__(self):
        super().__init__(
            code="SALT_01",
            description="Validar porcentaje de sal respecto a la harina",
            severity=SEVERITY["MEDIUM"]
        )
        
        # Rangos de sal óptimos por tipo de receta (porcentaje sobre peso de harina)
        self.salt_ranges = {
            "pizza": {"min": 1.5, "max": 3.0, "ideal": 2.0},
            "pan": {"min": 1.8, "max": 2.2, "ideal": 2.0},
            "flatbread": {"min": 1.5, "max": 2.5, "ideal": 2.0},
            "brioche": {"min": 1.5, "max": 2.2, "ideal": 1.8},
            "croissant": {"min": 1.5, "max": 2.5, "ideal": 2.0},
            "pasta_fresca": {"min": 0.5, "max": 1.5, "ideal": 1.0},
            "default": {"min": 1.5, "max": 2.5, "ideal": 2.0}
        }
    
    def validate(self, recipe: Dict[str, float], recipe_type: str, 
                production_scale: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Valida la proporción de sal en la receta."""
        flour_amount = sum(recipe.get(key, 0) for key in recipe if "harina" in key.lower())
        salt_amount = recipe.get("sal", 0)
        
        if flour_amount == 0:
            return False, "No se encontró harina en la receta", "Añade al menos un tipo de harina a la receta"
        
        if salt_amount == 0:
            return False, "No se encontró sal en la receta", "La sal es importante para el sabor y el control de la fermentación"
        
        salt_ratio = (salt_amount / flour_amount) * 100.0
        
        # Obtener rangos según tipo
        ranges = self.salt_ranges.get(recipe_type, self.salt_ranges["default"])
        min_salt = ranges["min"]
        max_salt = ranges["max"]
        ideal_salt = ranges["ideal"]
        
        # Ajuste para escala industrial (mayor control)
        if production_scale == "industrial":
            min_salt = ranges["ideal"] - 0.2
            max_salt = ranges["ideal"] + 0.2
        
        # Validar
        if salt_ratio < min_salt:
            return False, f"Proporción de sal demasiado baja ({salt_ratio:.2f}%). Mínimo recomendado: {min_salt:.2f}%", \
                   f"Aumenta la cantidad de sal. La proporción ideal es {ideal_salt:.2f}%"
        
        if salt_ratio > max_salt:
            return False, f"Proporción de sal demasiado alta ({salt_ratio:.2f}%). Máximo recomendado: {max_salt:.2f}%", \
                   f"Reduce la cantidad de sal. La proporción ideal es {ideal_salt:.2f}%"
        
        return True, None, None


class YeastRatioRule(ValidationRule):
    """Valida que la cantidad de levadura sea adecuada según el tipo de masa y tiempo de fermentación."""
    
    def __init__(self):
        super().__init__(
            code="YEAST_01",
            description="Validar proporción de levadura",
            severity=SEVERITY["MEDIUM"]
        )
        
        # Rangos de levadura óptimos por tipo (porcentaje sobre peso de harina)
        self.yeast_ranges = {
            "pizza": {
                "napolitana": {"min": 0.1, "max": 0.5, "ideal": 0.2},  # Fermentación larga
                "new_york": {"min": 0.5, "max": 1.5, "ideal": 1.0},
                "default": {"min": 0.5, "max": 2.0, "ideal": 1.0}
            },
            "pan": {
                "masa_madre": {"min": 0.0, "max": 0.5, "ideal": 0.0},  # Solo starter
                "default": {"min": 1.0, "max": 2.5, "ideal": 1.5}
            },
            "flatbread": {"min": 0.5, "max": 2.0, "ideal": 1.0},
            "brioche": {"min": 1.5, "max": 3.0, "ideal": 2.0},
            "croissant": {"min": 1.5, "max": 2.5, "ideal": 2.0},
            "default": {"min": 0.5, "max": 2.0, "ideal": 1.0}
        }
        
        # Ajustes por escala
        self.scale_adjustments = {
            "individual": {"factor": 1.0},
            "small_business": {"factor": 0.9},  # 10% menos
            "industrial": {"factor": 0.7}  # 30% menos, mayor control
        }
    
    def validate(self, recipe: Dict[str, float], recipe_type: str, 
                production_scale: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Valida la proporción de levadura en la receta."""
        flour_amount = sum(recipe.get(key, 0) for key in recipe if "harina" in key.lower())
        yeast_amount = recipe.get("levadura", 0) + recipe.get("levadura_seca", 0) + recipe.get("levadura_fresca", 0)
        has_starter = "masa_madre" in recipe and recipe["masa_madre"] > 0
        
        if flour_amount == 0:
            return False, "No se encontró harina en la receta", "Añade al menos un tipo de harina a la receta"
        
        # Si usa masa madre pero no levadura comercial, es válido
        if yeast_amount == 0 and has_starter:
            return True, None, None
        
        # Si no tiene levadura ni masa madre, error
        if yeast_amount == 0 and not has_starter:
            return False, "No se encontró levadura ni masa madre en la receta", \
                   "Añade levadura o masa madre para permitir la fermentación"
        
        yeast_ratio = (yeast_amount / flour_amount) * 100.0
        
        # Determinar subcategoría
        subcategory = None
        for key in recipe:
            if key.startswith("tipo_") and recipe[key]:
                subcategory = key.replace("tipo_", "")
                break
        
        # Obtener rangos según tipo y subcategoría
        if recipe_type in self.yeast_ranges:
            type_ranges = self.yeast_ranges[recipe_type]
            if isinstance(type_ranges, dict) and "min" in type_ranges:
                ranges = type_ranges
            elif subcategory and subcategory in type_ranges:
                ranges = type_ranges[subcategory]
            else:
                ranges = type_ranges.get("default", self.yeast_ranges["default"])
        else:
            ranges = self.yeast_ranges["default"]
        
        # Ajustar por escala
        scale_factor = self.scale_adjustments.get(production_scale, {"factor": 1.0})["factor"]
        min_yeast = ranges["min"] * scale_factor
        max_yeast = ranges["max"] * scale_factor
        ideal_yeast = ranges["ideal"] * scale_factor
        
        # Validar
        if yeast_ratio < min_yeast:
            return False, f"Proporción de levadura demasiado baja ({yeast_ratio:.2f}%). Mínimo recomendado: {min_yeast:.2f}%", \
                   f"Aumenta la cantidad de levadura o considera un tiempo de fermentación más largo"
        
        if yeast_ratio > max_yeast:
            return False, f"Proporción de levadura demasiado alta ({yeast_ratio:.2f}%). Máximo recomendado: {max_yeast:.2f}%", \
                   f"Reduce la cantidad de levadura o acorta el tiempo de fermentación"
        
        return True, None, None


class SpecialtyDoughIngredientsRule(ValidationRule):
    """Valida que las masas especiales incluyan los ingredientes esenciales."""
    
    def __init__(self):
        super().__init__(
            code="SPECIALTY_01",
            description="Validar ingredientes esenciales para masas especiales",
            severity=SEVERITY["CRITICAL"]
        )
        
        # Ingredientes esenciales por tipo de masa especial
        self.essential_ingredients = {
            "brioche": {
                "required": ["harina", "huevo", "mantequilla", "azucar"],
                "alternative_groups": [
                    [["leche", "agua"]]  # Debe tener leche o agua
                ]
            },
            "croissant": {
                "required": ["harina_fuerza", "mantequilla_laminado"],
                "alternative_groups": [
                    [["agua", "leche"]]  # Debe tener agua o leche
                ]
            },
            "kouign_amann": {
                "required": ["harina", "mantequilla_laminado", "azucar", "azucar_laminado"],
                "alternative_groups": []
            },
            "pasta_fresca": {
                "required": ["harina"],
                "alternative_groups": [
                    [["huevo", "agua"]]  # Pasta al huevo o pasta de agua
                ]
            },
            "masa_filo": {
                "required": ["harina", "agua"],
                "alternative_groups": [
                    [["aceite", "aceite_oliva", "mantequilla"]]  # Algún tipo de grasa
                ]
            }
        }
    
    def validate(self, recipe: Dict[str, float], recipe_type: str, 
                production_scale: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Valida que la receta incluya los ingredientes esenciales según su tipo."""
        # Solo aplicar a masas especiales
        if recipe_type not in self.essential_ingredients:
            return True, None, None
        
        requirements = self.essential_ingredients[recipe_type]
        
        # Verificar ingredientes requeridos
        missing_ingredients = []
        for ingredient in requirements["required"]:
            # Buscar variantes del ingrediente (ej: harina también incluye harina_integral)
            found = False
            for key in recipe:
                if ingredient in key and recipe[key] > 0:
                    found = True
                    break
            
            if not found:
                missing_ingredients.append(ingredient)
        
        # Verificar grupos alternativos (al menos uno del grupo debe estar presente)
        missing_alternative_groups = []
        for alt_group in requirements["alternative_groups"]:
            group_satisfied = False
            for alternatives in alt_group:
                for alt in alternatives:
                    for key in recipe:
                        if alt in key and recipe[key] > 0:
                            group_satisfied = True
                            break
                    if group_satisfied:
                        break
                if group_satisfied:
                    break
            
            if not group_satisfied:
                missing_alternative_groups.append(" o ".join([", ".join(alts) for alts in alt_group]))
        
        # Construir mensaje de error
        if missing_ingredients or missing_alternative_groups:
            error_msg = "Faltan ingredientes esenciales para este tipo de masa:"
            recommendation = "Para una masa de " + recipe_type + " correcta, debes incluir:"
            
            if missing_ingredients:
                ingredients_str = ", ".join(missing_ingredients)
                error_msg += f" {ingredients_str}"
                recommendation += f" {ingredients_str}"
            
            if missing_alternative_groups:
                alternatives_str = "; ".join(missing_alternative_groups)
                error_msg += f" y al menos uno de: {alternatives_str}"
                recommendation += f" y al menos uno de: {alternatives_str}"
            
            return False, error_msg, recommendation
        
        return True, None, None


class ScaleLimitsRule(ValidationRule):
    """Valida que la receta cumpla con los límites de escala de producción."""
    
    def __init__(self):
        super().__init__(
            code="SCALE_01",
            description="Validar límites para la escala de producción",
            severity=SEVERITY["CRITICAL"]
        )
        
        # Límites de cantidad total por escala
        self.scale_limits = {
            "individual": {"min": 0.1, "max": 5.0, "unit": "kg"},
            "small_business": {"min": 2.0, "max": 50.0, "unit": "kg"},
            "industrial": {"min": 20.0, "max": 1000.0, "unit": "kg"}
        }
    
    def validate(self, recipe: Dict[str, float], recipe_type: str, 
                production_scale: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Valida que la receta cumpla con los límites de la escala de producción."""
        # Calcular peso total de la receta (suma de todos los ingredientes)
        total_weight = sum(amount for key, amount in recipe.items() 
                          if isinstance(amount, (int, float)) and key not in ["recipe_id", "recipe_name"])
        
        # Convertir a kilogramos si está en gramos
        weight_kg = total_weight / 1000.0
        
        # Obtener límites según escala
        limits = self.scale_limits.get(production_scale, {"min": 0.0, "max": float('inf'), "unit": "kg"})
        
        if weight_kg < limits["min"]:
            return False, f"La cantidad total ({weight_kg:.2f} kg) es inferior al mínimo para escala {production_scale} ({limits['min']:.2f} kg)", \
                   f"Aumenta las cantidades para alcanzar al menos {limits['min']:.2f} kg de masa total"
        
        if weight_kg > limits["max"]:
            return False, f"La cantidad total ({weight_kg:.2f} kg) excede el máximo para escala {production_scale} ({limits['max']:.2f} kg)", \
                   f"Reduce las cantidades para no exceder {limits['max']:.2f} kg de masa total"
        
        return True, None, None


class FermentationParametersRule(ValidationRule):
    """Valida que los parámetros de fermentación sean adecuados para el tipo de masa."""
    
    def __init__(self):
        super().__init__(
            code="FERMENT_01",
            description="Validar parámetros de fermentación",
            severity=SEVERITY["MEDIUM"]
        )
        
        # Rangos de temperatura óptimos por tipo de masa (en °C)
        self.temp_ranges = {
            "pizza": {
                "napolitana": {"min": 18.0, "max": 24.0, "ideal": 20.0},
                "new_york": {"min": 20.0, "max": 25.0, "ideal": 22.0},
                "default": {"min": 20.0, "max": 24.0, "ideal": 22.0}
            },
            "pan": {
                "masa_madre": {"min": 18.0, "max": 22.0, "ideal": 20.0},
                "default": {"min": 22.0, "max": 26.0, "ideal": 24.0}
            },
            "brioche": {"min": 25.0, "max": 28.0, "ideal": 26.0},
            "default": {"min": 20.0, "max": 25.0, "ideal": 22.0}
        }
        
        # Rangos de tiempo óptimos por tipo de masa (en horas)
        self.time_ranges = {
            "pizza": {
                "napolitana": {"min": 8.0, "max": 72.0, "ideal": 24.0},
                "new_york": {"min": 4.0, "max": 48.0, "ideal": 24.0},
                "default": {"min": 2.0, "max": 24.0, "ideal": 8.0}
            },
            "pan": {
                "masa_madre": {"min": 4.0, "max": 36.0, "ideal": 12.0},
                "default": {"min": 1.0, "max": 24.0, "ideal": 4.0}
            },
            "brioche": {"min": 2.0, "max": 12.0, "ideal": 4.0},
            "default": {"min": 1.0, "max": 24.0, "ideal": 4.0}
        }
        
        # Cargar rangos de temperatura desde variables de entorno si están disponibles
        for recipe_type in ["PIZZA", "PAN", "BRIOCHE"]:
            env_var = f"FERMENTATION_TEMP_{recipe_type}"
            if env_var in os.environ:
                try:
                    min_temp, max_temp = os.environ[env_var].split("-")
                    min_temp, max_temp = float(min_temp), float(max_temp)
                    
                    # Actualizar el rango por defecto para este tipo
                    type_lower = recipe_type.lower()
                    if type_lower in self.temp_ranges and "default" in self.temp_ranges[type_lower]:
                        self.temp_ranges[type_lower]["default"] = {
                            "min": min_temp,
                            "max": max_temp,
                            "ideal": (min_temp + max_temp) / 2
                        }
                except Exception:
                    pass
    
    def validate(self, recipe: Dict[str, float], recipe_type: str, 
                production_scale: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Valida los parámetros de fermentación de la receta."""
        # Extraer parámetros de fermentación
        ferment_temp = recipe.get("temperatura_fermentacion", None)
        ferment_time = recipe.get("tiempo_fermentacion", None)  # En horas
        
        # Si no hay parámetros de fermentación, no podemos validar
        if ferment_temp is None and ferment_time is None:
            return True, None, None
        
        # Determinar subcategoría si está presente
        subcategory = None
        for key in recipe:
            if key.startswith("tipo_") and recipe[key]:
                subcategory = key.replace("tipo_", "")
                break
        
        errors = []
        recommendations = []
        
        # Validar temperatura
        if ferment_temp is not None:
            # Obtener rangos según tipo y subcategoría
            if recipe_type in self.temp_ranges:
                type_ranges = self.temp_ranges[recipe_type]
                if subcategory and subcategory in type_ranges:
                    temp_range = type_ranges[subcategory]
                else:
                    temp_range = type_ranges.get("default", self.temp_ranges["default"])
            else:
                temp_range = self.temp_ranges["default"]
            
            # Validar
            if ferment_temp < temp_range["min"]:
                errors.append(
                    f"Temperatura de fermentación demasiado baja ({ferment_temp:.1f}°C). " +
                    f"Mínimo recomendado: {temp_range['min']:.1f}°C"
                )
                recommendations.append(
                    f"Aumenta la temperatura de fermentación a al menos {temp_range['min']:.1f}°C. " +
                    f"La temperatura ideal es {temp_range['ideal']:.1f}°C"
                )
            elif ferment_temp > temp_range["max"]:
                errors.append(
                    f"Temperatura de fermentación demasiado alta ({ferment_temp:.1f}°C). " +
                    f"Máximo recomendado: {temp_range['max']:.1f}°C"
                )
                recommendations.append(
                    f"Reduce la temperatura de fermentación a máximo {temp_range['max']:.1f}°C. " +
                    f"La temperatura ideal es {temp_range['ideal']:.1f}°C"
                )
        
        # Validar tiempo
        if ferment_time is not None:
            # Obtener rangos según tipo y subcategoría
            if recipe_type in self.time_ranges:
                type_ranges = self.time_ranges[recipe_type]
                if subcategory and subcategory in type_ranges:
                    time_range = type_ranges[subcategory]
                else:
                    time_range = type_ranges.get("default", self.time_ranges["default"])
            else:
                time_range = self.time_ranges["default"]
            
            # Validar
            if ferment_time < time_range["min"]:
                errors.append(
                    f"Tiempo de fermentación demasiado corto ({ferment_time:.1f} horas). " +
                    f"Mínimo recomendado: {time_range['min']:.1f} horas"
                )
                recommendations.append(
                    f"Aumenta el tiempo de fermentación a al menos {time_range['min']:.1f} horas. " +
                    f"El tiempo ideal es {time_range['ideal']:.1f} horas"
                )
            elif ferment_time > time_range["max"]:
                errors.append(
                    f"Tiempo de fermentación demasiado largo ({ferment_time:.1f} horas). " +
                    f"Máximo recomendado: {time_range['max']:.1f} horas"
                )
                recommendations.append(
                    f"Reduce el tiempo de fermentación a máximo {time_range['max']:.1f} horas. " +
                    f"El tiempo ideal es {time_range['ideal']:.1f} horas"
                )
        
        # Construir resultado
        if errors:
            return False, " ".join(errors), " ".join(recommendations)
        
        return True, None, None


# Lista global de reglas de validación disponibles
VALIDATION_RULES = [
    HydrationRatioRule(),
    SaltRatioRule(),
    YeastRatioRule(),
    SpecialtyDoughIngredientsRule(),
    ScaleLimitsRule(),
    FermentationParametersRule()
]

def get_validation_rules() -> List[ValidationRule]:
    """Devuelve la lista de reglas de validación disponibles."""
    return VALIDATION_RULES

def get_rule_by_code(code: str) -> Optional[ValidationRule]:
    """Obtiene una regla específica por su código."""
    for rule in VALIDATION_RULES:
        if rule.code == code:
            return rule
    return None 