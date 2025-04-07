#!/usr/bin/env python
"""
Sistema de Validación Crítica para PizzaAI
------------------------------------------
Este módulo implementa un sistema de validación para recetas
basado en reglas científicas y técnicas que aseguran la viabilidad
de una receta en distintas escalas de producción.
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("validation_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ValidationSystem")

class ValidationError:
    """Representa un error de validación."""
    
    def __init__(self, 
                 error_code: str, 
                 severity: str, 
                 message: str, 
                 affected_parameters: List[str] = None,
                 recommendation: str = None):
        """
        Inicializa un error de validación.
        
        Args:
            error_code: Código único del error
            severity: Nivel de severidad ("CRITICAL" o "MEDIUM")
            message: Mensaje descriptivo del error
            affected_parameters: Lista de parámetros afectados
            recommendation: Recomendación para resolver el error
        """
        self.error_code = error_code
        self.severity = severity
        self.message = message
        self.affected_parameters = affected_parameters or []
        self.recommendation = recommendation
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convierte el error a un diccionario."""
        return {
            "error_code": self.error_code,
            "severity": self.severity,
            "message": self.message,
            "affected_parameters": self.affected_parameters,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        """Representación en cadena del error."""
        return f"[{self.error_code}] {self.severity}: {self.message}"


class RecipeValidator:
    """
    Implementa la lógica de validación de recetas según
    reglas predefinidas y parámetros de escala.
    """
    
    def __init__(self, 
                 rules_file: str = None,
                 ingredient_limits_file: str = None,
                 process_parameters_file: str = None):
        """
        Inicializa el validador de recetas.
        
        Args:
            rules_file: Ruta al archivo JSON de reglas
            ingredient_limits_file: Ruta al archivo JSON de límites de ingredientes
            process_parameters_file: Ruta al archivo JSON de parámetros de proceso
        """
        # Obtener directorio del script actual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Establecer rutas por defecto relativas al directorio actual
        self.rules_file = rules_file or os.path.join(current_dir, "validation_rules.json")
        self.ingredient_limits_file = ingredient_limits_file or os.path.join(current_dir, "ingredient_limits.json")
        self.process_parameters_file = process_parameters_file or os.path.join(current_dir, "process_parameters.json")
        
        # Cargar reglas y parámetros
        self.validation_rules = self._load_validation_rules()
        self.ingredient_limits = self._load_ingredient_limits()
        self.process_parameters = self._load_process_parameters()
        
        logger.info("Sistema de validación inicializado correctamente")
    
    def _load_validation_rules(self) -> Dict:
        """Carga las reglas de validación desde el archivo JSON."""
        try:
            with open(self.rules_file, "r", encoding="utf-8") as f:
                rules = json.load(f)
            logger.info(f"Reglas de validación cargadas: {len(rules.get('critical_rules', []))} críticas, {len(rules.get('medium_rules', []))} medias")
            return rules
        except FileNotFoundError:
            logger.warning(f"Archivo de reglas no encontrado: {self.rules_file}")
            # Valores por defecto básicos
            return {"critical_rules": [], "medium_rules": []}
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar JSON de reglas: {self.rules_file}")
            return {"critical_rules": [], "medium_rules": []}
    
    def _load_ingredient_limits(self) -> Dict:
        """Carga los límites de ingredientes desde el archivo JSON."""
        try:
            with open(self.ingredient_limits_file, "r", encoding="utf-8") as f:
                limits = json.load(f)
            logger.info(f"Límites de ingredientes cargados: {len(limits)} categorías")
            return limits
        except FileNotFoundError:
            logger.warning(f"Archivo de límites no encontrado: {self.ingredient_limits_file}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar JSON de límites: {self.ingredient_limits_file}")
            return {}
    
    def _load_process_parameters(self) -> Dict:
        """Carga los parámetros de proceso desde el archivo JSON."""
        try:
            with open(self.process_parameters_file, "r", encoding="utf-8") as f:
                parameters = json.load(f)
            logger.info(f"Parámetros de proceso cargados: {len(parameters.get('scales', {}))} escalas")
            return parameters
        except FileNotFoundError:
            logger.warning(f"Archivo de parámetros no encontrado: {self.process_parameters_file}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar JSON de parámetros: {self.process_parameters_file}")
            return {}
    
    def run_validation(self, recipe_data: Dict, scale: str) -> Tuple[bool, List[ValidationError]]:
        """
        Ejecuta la validación completa de una receta.
        
        Args:
            recipe_data: Datos de la receta a validar
            scale: Escala de producción ("individual", "small_business", "industrial")
            
        Returns:
            Tupla con (puede_proceder, lista_errores)
        """
        validation_errors = []
        
        # Validar escala
        if scale not in ["individual", "small_business", "industrial"]:
            validation_errors.append(ValidationError(
                "VE001", "CRITICAL", f"Escala no válida: {scale}",
                ["scale"], "Utilice una escala válida: individual, small_business o industrial"
            ))
            return False, validation_errors
        
        # Validar estructura básica de receta
        if not self._validate_recipe_structure(recipe_data, validation_errors):
            return False, validation_errors
        
        # Validar hidratación
        self._validate_hydration(recipe_data, scale, validation_errors)
        
        # Validar porcentaje de sal
        self._validate_salt_percentage(recipe_data, scale, validation_errors)
        
        # Validar proporción de levadura
        self._validate_yeast_proportion(recipe_data, scale, validation_errors)
        
        # Validar compatibilidad de ingredientes
        self._validate_ingredient_compatibility(recipe_data, scale, validation_errors)
        
        # Validar parámetros de proceso
        self._validate_process_parameters(recipe_data, scale, validation_errors)
        
        # Validar parámetros técnicos para escala industrial
        if scale == "industrial":
            self._validate_industrial_parameters(recipe_data, validation_errors)
        
        # Determinar si puede proceder (no hay errores críticos)
        can_proceed = not any(e.severity == "CRITICAL" for e in validation_errors)
        
        logger.info(f"Validación completada: {len(validation_errors)} errores, puede proceder: {can_proceed}")
        return can_proceed, validation_errors
    
    def _validate_recipe_structure(self, recipe_data: Dict, errors: List[ValidationError]) -> bool:
        """
        Valida la estructura básica de la receta.
        
        Args:
            recipe_data: Datos de la receta
            errors: Lista de errores a actualizar
            
        Returns:
            True si la estructura es válida, False en caso contrario
        """
        # Verificar campos obligatorios
        required_fields = ["id", "name", "type", "ingredients"]
        
        for field in required_fields:
            if field not in recipe_data:
                errors.append(ValidationError(
                    "VE002", "CRITICAL", f"Campo obligatorio faltante: {field}",
                    [field], f"Añadir el campo '{field}' a la receta"
                ))
                return False
        
        # Verificar que ingredients sea un diccionario
        if not isinstance(recipe_data.get("ingredients", {}), dict):
            errors.append(ValidationError(
                "VE003", "CRITICAL", "El campo 'ingredients' debe ser un objeto",
                ["ingredients"], "El campo 'ingredients' debe ser un objeto con pares clave-valor"
            ))
            return False
        
        # Verificar ingredientes básicos según tipo de receta
        basic_ingredients = ["flour", "water"]
        missing_ingredients = [ing for ing in basic_ingredients if ing not in recipe_data.get("ingredients", {})]
        
        if missing_ingredients:
            errors.append(ValidationError(
                "VE004", "CRITICAL", f"Ingredientes básicos faltantes: {', '.join(missing_ingredients)}",
                ["ingredients"], f"Añadir los ingredientes básicos faltantes: {', '.join(missing_ingredients)}"
            ))
            return False
        
        return True
    
    def _validate_hydration(self, recipe_data: Dict, scale: str, errors: List[ValidationError]):
        """
        Valida la hidratación de la masa.
        
        Args:
            recipe_data: Datos de la receta
            scale: Escala de producción
            errors: Lista de errores a actualizar
        """
        ingredients = recipe_data.get("ingredients", {})
        
        # Obtener cantidad de harina
        flour_amount = 0
        if "flour" in ingredients:
            flour_amount = ingredients["flour"].get("quantity", 0)
        
        # Obtener cantidad de agua
        water_amount = 0
        if "water" in ingredients:
            water_amount = ingredients["water"].get("quantity", 0)
        
        # Verificar si hay cantidades
        if flour_amount <= 0:
            errors.append(ValidationError(
                "VE005", "CRITICAL", "Cantidad de harina no especificada o inválida",
                ["ingredients.flour.quantity"], "Especificar una cantidad válida para la harina"
            ))
            return
        
        if water_amount <= 0:
            errors.append(ValidationError(
                "VE006", "CRITICAL", "Cantidad de agua no especificada o inválida",
                ["ingredients.water.quantity"], "Especificar una cantidad válida para el agua"
            ))
            return
        
        # Calcular hidratación
        hydration = water_amount / flour_amount
        
        # Obtener límites de hidratación según escala y tipo de receta
        min_hydration = 0.45
        max_hydration = 0.75
        
        recipe_type = recipe_data.get("type", "")
        if recipe_type in self.process_parameters.get("recipe_types", {}):
            type_params = self.process_parameters["recipe_types"][recipe_type]
            if "hydration_range" in type_params:
                min_hydration = type_params["hydration_range"].get("min", 45) / 100
                max_hydration = type_params["hydration_range"].get("max", 75) / 100
        
        # Ajustar tolerancias según escala
        if scale in self.process_parameters.get("scales", {}):
            tolerances = self.process_parameters["scales"][scale].get("tolerances", {})
            hydration_tolerance = tolerances.get("hydration", {}).get("range", 0) / 100
            min_hydration -= hydration_tolerance
            max_hydration += hydration_tolerance
        
        # Validar hidratación
        if hydration < min_hydration:
            errors.append(ValidationError(
                "VE007", "CRITICAL", f"Hidratación muy baja: {hydration:.2f}",
                ["ingredients.water.quantity", "ingredients.flour.quantity"],
                f"Aumentar la cantidad de agua o reducir la cantidad de harina para alcanzar al menos {min_hydration:.2f} de hidratación"
            ))
        elif hydration > max_hydration:
            errors.append(ValidationError(
                "VE008", "CRITICAL", f"Hidratación muy alta: {hydration:.2f}",
                ["ingredients.water.quantity", "ingredients.flour.quantity"],
                f"Reducir la cantidad de agua o aumentar la cantidad de harina para no superar {max_hydration:.2f} de hidratación"
            ))
        
        logger.debug(f"Hidratación calculada: {hydration:.2f}, límites: [{min_hydration:.2f}, {max_hydration:.2f}]")
    
    def _validate_salt_percentage(self, recipe_data: Dict, scale: str, errors: List[ValidationError]):
        """
        Valida el porcentaje de sal respecto a la harina.
        
        Args:
            recipe_data: Datos de la receta
            scale: Escala de producción
            errors: Lista de errores a actualizar
        """
        ingredients = recipe_data.get("ingredients", {})
        
        # Obtener cantidad de harina
        flour_amount = 0
        if "flour" in ingredients:
            flour_amount = ingredients["flour"].get("quantity", 0)
        
        # Obtener cantidad de sal
        salt_amount = 0
        if "salt" in ingredients:
            salt_amount = ingredients["salt"].get("quantity", 0)
        
        # Verificar si hay cantidades
        if flour_amount <= 0:
            return  # Ya se reportó el error en validación de hidratación
        
        # Si no hay sal, advertencia
        if salt_amount <= 0:
            errors.append(ValidationError(
                "VE009", "MEDIUM", "No se ha especificado sal en la receta",
                ["ingredients.salt"], "Considerar añadir sal para mejorar sabor y estructura (1-2% respecto a la harina)"
            ))
            return
        
        # Calcular porcentaje de sal
        salt_percentage = (salt_amount / flour_amount) * 100
        
        # Obtener límites de sal
        min_salt = 1.0
        max_salt = 2.5
        
        if "salt" in self.ingredient_limits.get("other", {}):
            salt_limits = self.ingredient_limits["other"]["salt"].get("usage_range", {})
            min_salt = salt_limits.get("min", 1.0)
            max_salt = salt_limits.get("max", 2.5)
        
        # Ajustar tolerancias según escala
        if scale in self.process_parameters.get("scales", {}):
            tolerances = self.process_parameters["scales"][scale].get("tolerances", {})
            salt_tolerance = tolerances.get("salt", {}).get("range", 0)
            min_salt -= salt_tolerance
            max_salt += salt_tolerance
        
        # Validar porcentaje de sal
        if salt_percentage < min_salt:
            errors.append(ValidationError(
                "VE010", "MEDIUM", f"Porcentaje de sal muy bajo: {salt_percentage:.2f}%",
                ["ingredients.salt.quantity"],
                f"Aumentar la cantidad de sal para alcanzar al menos {min_salt:.1f}% respecto a la harina"
            ))
        elif salt_percentage > max_salt:
            severity = "MEDIUM"
            if scale == "industrial":
                severity = "CRITICAL"  # Más estricto para escala industrial
            
            errors.append(ValidationError(
                "VE011", severity, f"Porcentaje de sal muy alto: {salt_percentage:.2f}%",
                ["ingredients.salt.quantity"],
                f"Reducir la cantidad de sal para no superar {max_salt:.1f}% respecto a la harina"
            ))
        
        logger.debug(f"Porcentaje de sal calculado: {salt_percentage:.2f}%, límites: [{min_salt:.1f}%, {max_salt:.1f}%]")
    
    def _validate_yeast_proportion(self, recipe_data: Dict, scale: str, errors: List[ValidationError]):
        """
        Valida la proporción de levadura respecto a la harina.
        
        Args:
            recipe_data: Datos de la receta
            scale: Escala de producción
            errors: Lista de errores a actualizar
        """
        ingredients = recipe_data.get("ingredients", {})
        
        # Verificar si hay levadura
        if "yeast" not in ingredients:
            # No es un error crítico, podría ser masa madre u otro método
            errors.append(ValidationError(
                "VE012", "MEDIUM", "No se ha especificado levadura en la receta",
                ["ingredients.yeast"], "Considerar añadir levadura si no se usa masa madre u otro método de fermentación"
            ))
            return
        
        # Obtener cantidad de harina
        flour_amount = 0
        if "flour" in ingredients:
            flour_amount = ingredients["flour"].get("quantity", 0)
        
        # Obtener cantidad de levadura
        yeast_amount = ingredients["yeast"].get("quantity", 0)
        
        # Verificar si hay cantidades
        if flour_amount <= 0:
            return  # Ya se reportó el error en validación de hidratación
        
        if yeast_amount <= 0:
            errors.append(ValidationError(
                "VE013", "MEDIUM", "Cantidad de levadura no especificada o inválida",
                ["ingredients.yeast.quantity"], "Especificar una cantidad válida para la levadura"
            ))
            return
        
        # Calcular porcentaje de levadura
        yeast_percentage = (yeast_amount / flour_amount) * 100
        
        # Obtener límites de levadura
        min_yeast = 0.5
        max_yeast = 3.0
        
        yeast_type = ingredients["yeast"].get("type", "dry")
        if yeast_type in self.ingredient_limits.get("leavening_agents", {}):
            yeast_limits = self.ingredient_limits["leavening_agents"][yeast_type].get("usage_range", {})
            min_yeast = yeast_limits.get("min", 0.5)
            max_yeast = yeast_limits.get("max", 3.0)
        
        # Validar porcentaje de levadura
        if yeast_percentage < min_yeast:
            errors.append(ValidationError(
                "VE014", "MEDIUM", f"Porcentaje de levadura muy bajo: {yeast_percentage:.2f}%",
                ["ingredients.yeast.quantity"],
                f"Aumentar la cantidad de levadura para alcanzar al menos {min_yeast:.1f}% respecto a la harina"
            ))
        elif yeast_percentage > max_yeast:
            severity = "MEDIUM"
            if scale == "industrial":
                severity = "CRITICAL"  # Más estricto para escala industrial
            
            errors.append(ValidationError(
                "VE015", severity, f"Porcentaje de levadura muy alto: {yeast_percentage:.2f}%",
                ["ingredients.yeast.quantity"],
                f"Reducir la cantidad de levadura para no superar {max_yeast:.1f}% respecto a la harina"
            ))
        
        logger.debug(f"Porcentaje de levadura calculado: {yeast_percentage:.2f}%, límites: [{min_yeast:.1f}%, {max_yeast:.1f}%]")
    
    def _validate_ingredient_compatibility(self, recipe_data: Dict, scale: str, errors: List[ValidationError]):
        """
        Valida la compatibilidad entre ingredientes.
        
        Args:
            recipe_data: Datos de la receta
            scale: Escala de producción
            errors: Lista de errores a actualizar
        """
        ingredients = recipe_data.get("ingredients", {})
        recipe_type = recipe_data.get("type", "")
        
        # Verificar compatibilidad para masas sin gluten
        is_gluten_free = recipe_data.get("gluten_free", False)
        
        if is_gluten_free:
            # Verificar si hay harina con gluten
            wheat_flours = ["wheat_flour", "bread_flour", "all_purpose_flour", "00_flour"]
            
            flour_type = ""
            if "flour" in ingredients:
                flour_type = ingredients["flour"].get("type", "")
            
            if flour_type in wheat_flours:
                errors.append(ValidationError(
                    "VE016", "CRITICAL", f"La receta está marcada como sin gluten pero usa harina de trigo ({flour_type})",
                    ["ingredients.flour.type", "gluten_free"],
                    "Sustituir la harina de trigo por harinas sin gluten (arroz, maíz, tapioca, etc.)"
                ))
            
            # Verificar si tiene agentes aglutinantes necesarios
            binding_agents = ["xanthan_gum", "psyllium_husk", "guar_gum"]
            has_binding_agent = False
            
            for ingredient in ingredients:
                if ingredient in binding_agents:
                    has_binding_agent = True
                    break
            
            if not has_binding_agent:
                errors.append(ValidationError(
                    "VE017", "CRITICAL", "Receta sin gluten sin agentes aglutinantes",
                    ["ingredients"],
                    "Añadir un agente aglutinante como xanthan gum, psyllium husk o guar gum para mejorar la estructura"
                ))
        
        # Verificar compatibilidad para recetas de color específico
        desired_color = recipe_data.get("desired_color", "")
        
        if desired_color and scale != "individual":
            color_ingredients = self.process_parameters.get("special_requirements", {}).get("colored_dough", {}).get("natural_colorants", {})
            
            if desired_color in color_ingredients:
                valid_colorants = color_ingredients[desired_color]
                has_valid_colorant = False
                
                for ingredient in ingredients:
                    if ingredient in valid_colorants:
                        has_valid_colorant = True
                        break
                
                if not has_valid_colorant:
                    errors.append(ValidationError(
                        "VE018", "MEDIUM", f"No se ha especificado un colorante natural para el color deseado ({desired_color})",
                        ["ingredients", "desired_color"],
                        f"Considerar añadir uno de estos ingredientes para el color {desired_color}: {', '.join(valid_colorants[:3])}"
                    ))
    
    def _validate_process_parameters(self, recipe_data: Dict, scale: str, errors: List[ValidationError]):
        """
        Valida los parámetros del proceso.
        
        Args:
            recipe_data: Datos de la receta
            scale: Escala de producción
            errors: Lista de errores a actualizar
        """
        process = recipe_data.get("process", {})
        
        # Verificar si hay información de proceso
        if not process and scale != "individual":
            errors.append(ValidationError(
                "VE019", "MEDIUM", "No se ha especificado información de proceso",
                ["process"], "Añadir información sobre el proceso de elaboración"
            ))
            return
        
        # Validar temperatura de la masa
        if "mixing" in process:
            target_temp = process["mixing"].get("target_temperature")
            
            if target_temp is not None:
                min_temp = 22
                max_temp = 26
                
                if scale in self.process_parameters.get("scales", {}):
                    dough_temp = self.process_parameters["scales"][scale].get("temperatures", {}).get("dough", {})
                    min_temp = dough_temp.get("min", 22)
                    max_temp = dough_temp.get("max", 26)
                
                # Ajustar tolerancias según escala
                if scale in self.process_parameters.get("scales", {}):
                    tolerances = self.process_parameters["scales"][scale].get("tolerances", {})
                    temp_tolerance = tolerances.get("temperature", {}).get("range", 0)
                    min_temp -= temp_tolerance
                    max_temp += temp_tolerance
                
                if target_temp < min_temp:
                    errors.append(ValidationError(
                        "VE020", "MEDIUM", f"Temperatura de masa muy baja: {target_temp}°C",
                        ["process.mixing.target_temperature"],
                        f"Aumentar la temperatura objetivo de la masa a al menos {min_temp}°C"
                    ))
                elif target_temp > max_temp:
                    errors.append(ValidationError(
                        "VE021", "MEDIUM", f"Temperatura de masa muy alta: {target_temp}°C",
                        ["process.mixing.target_temperature"],
                        f"Reducir la temperatura objetivo de la masa a máximo {max_temp}°C"
                    ))
        
        # Validar tiempo de amasado
        if "mixing" in process:
            mixing_time = process["mixing"].get("time")
            
            if mixing_time is not None:
                min_time = 5
                max_time = 15
                
                if scale in self.process_parameters.get("scales", {}):
                    mixing_params = self.process_parameters["scales"][scale].get("process_time", {}).get("mixing", {})
                    min_time = mixing_params.get("min", 5)
                    max_time = mixing_params.get("max", 15)
                
                if mixing_time < min_time:
                    errors.append(ValidationError(
                        "VE022", "MEDIUM", f"Tiempo de amasado muy corto: {mixing_time} min",
                        ["process.mixing.time"],
                        f"Aumentar el tiempo de amasado a al menos {min_time} min"
                    ))
                elif mixing_time > max_time:
                    errors.append(ValidationError(
                        "VE023", "MEDIUM", f"Tiempo de amasado muy largo: {mixing_time} min",
                        ["process.mixing.time"],
                        f"Reducir el tiempo de amasado a máximo {max_time} min"
                    ))
        
        # Validar temperatura de horneado
        if "baking" in process:
            baking_temp = process["baking"].get("temperature")
            
            if baking_temp is not None:
                min_temp = 180
                max_temp = 250
                
                recipe_type = recipe_data.get("type", "")
                if recipe_type in self.process_parameters.get("recipe_types", {}):
                    baking_params = self.process_parameters["recipe_types"][recipe_type].get("baking_temperature", {})
                    min_temp = baking_params.get("min", 180)
                    max_temp = baking_params.get("max", 250)
                
                if baking_temp < min_temp:
                    errors.append(ValidationError(
                        "VE024", "MEDIUM", f"Temperatura de horneado muy baja: {baking_temp}°C",
                        ["process.baking.temperature"],
                        f"Aumentar la temperatura de horneado a al menos {min_temp}°C"
                    ))
                elif baking_temp > max_temp:
                    errors.append(ValidationError(
                        "VE025", "MEDIUM", f"Temperatura de horneado muy alta: {baking_temp}°C",
                        ["process.baking.temperature"],
                        f"Reducir la temperatura de horneado a máximo {max_temp}°C"
                    ))
    
    def _validate_industrial_parameters(self, recipe_data: Dict, errors: List[ValidationError]):
        """
        Valida los parámetros específicos para escala industrial.
        
        Args:
            recipe_data: Datos de la receta
            errors: Lista de errores a actualizar
        """
        # Verificar tamaño de lote
        batch_size = recipe_data.get("batch_size")
        
        if batch_size is None:
            errors.append(ValidationError(
                "VE026", "CRITICAL", "No se ha especificado tamaño de lote para escala industrial",
                ["batch_size"], "Especificar tamaño de lote en kg"
            ))
        elif batch_size < 20:
            errors.append(ValidationError(
                "VE027", "CRITICAL", f"Tamaño de lote muy pequeño para escala industrial: {batch_size} kg",
                ["batch_size"], "Aumentar tamaño de lote a al menos 20 kg para escala industrial"
            ))
        elif batch_size > 500:
            errors.append(ValidationError(
                "VE028", "MEDIUM", f"Tamaño de lote muy grande: {batch_size} kg",
                ["batch_size"], "Considerar dividir la producción en lotes más pequeños"
            ))
        
        # Verificar especificaciones técnicas
        tech_specs = recipe_data.get("technical_specs", {})
        
        if not tech_specs:
            errors.append(ValidationError(
                "VE029", "CRITICAL", "No se han especificado parámetros técnicos para escala industrial",
                ["technical_specs"], "Añadir especificaciones técnicas de equipamiento, materias primas y ambiente"
            ))
            return
        
        # Verificar equipamiento
        equipment = tech_specs.get("equipment", {})
        
        if not equipment:
            errors.append(ValidationError(
                "VE030", "CRITICAL", "No se ha especificado equipamiento para escala industrial",
                ["technical_specs.equipment"], "Especificar equipamiento disponible (mezclador, laminadora, horno)"
            ))
        else:
            # Verificar mezclador
            mixer = equipment.get("mixer", {})
            
            if not mixer.get("available", False):
                errors.append(ValidationError(
                    "VE031", "CRITICAL", "No se dispone de mezclador industrial",
                    ["technical_specs.equipment.mixer"], "Es necesario disponer de un mezclador para escala industrial"
                ))
            elif "capacity" in mixer:
                mixer_capacity = mixer["capacity"]
                
                if mixer_capacity < batch_size:
                    errors.append(ValidationError(
                        "VE032", "CRITICAL", f"Capacidad del mezclador ({mixer_capacity} kg) menor que el tamaño de lote ({batch_size} kg)",
                        ["technical_specs.equipment.mixer.capacity", "batch_size"],
                        "Reducir tamaño de lote o utilizar un mezclador de mayor capacidad"
                    ))
            
            # Verificar horno
            oven = equipment.get("oven", {})
            
            if not oven:
                errors.append(ValidationError(
                    "VE033", "CRITICAL", "No se ha especificado información sobre el horno",
                    ["technical_specs.equipment.oven"], "Especificar tipo y características del horno"
                ))
        
        # Verificar materias primas
        raw_materials = tech_specs.get("raw_materials", {})
        
        if not raw_materials:
            errors.append(ValidationError(
                "VE034", "CRITICAL", "No se han especificado detalles de materias primas",
                ["technical_specs.raw_materials"], "Especificar características de las materias primas (harina, etc.)"
            ))
        else:
            # Verificar harina
            flour = raw_materials.get("flour", {})
            
            if not flour:
                errors.append(ValidationError(
                    "VE035", "CRITICAL", "No se han especificado características de la harina",
                    ["technical_specs.raw_materials.flour"], "Especificar contenido proteico y humedad de la harina"
                ))
            else:
                # Verificar contenido proteico
                protein_content = flour.get("protein_content")
                
                if protein_content is None:
                    errors.append(ValidationError(
                        "VE036", "CRITICAL", "No se ha especificado contenido proteico de la harina",
                        ["technical_specs.raw_materials.flour.protein_content"], "Especificar contenido proteico de la harina (%)"
                    ))
                elif protein_content < 9.0 or protein_content > 14.0:
                    errors.append(ValidationError(
                        "VE037", "CRITICAL", f"Contenido proteico de harina fuera de rango: {protein_content}%",
                        ["technical_specs.raw_materials.flour.protein_content"],
                        "El contenido proteico debe estar entre 9.0% y 14.0%"
                    ))
                
                # Verificar humedad
                moisture = flour.get("moisture")
                
                if moisture is None:
                    errors.append(ValidationError(
                        "VE038", "CRITICAL", "No se ha especificado humedad de la harina",
                        ["technical_specs.raw_materials.flour.moisture"], "Especificar humedad de la harina (%)"
                    ))
                elif moisture < 12.0 or moisture > 14.5:
                    errors.append(ValidationError(
                        "VE039", "CRITICAL", f"Humedad de harina fuera de rango: {moisture}%",
                        ["technical_specs.raw_materials.flour.moisture"],
                        "La humedad debe estar entre 12.0% y 14.5%"
                    ))


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Validador de Recetas PizzaAI")
    parser.add_argument("recipe_file", help="Archivo JSON con la receta a validar")
    parser.add_argument("--scale", choices=["individual", "small_business", "industrial"], 
                        default="individual", help="Escala de producción")
    parser.add_argument("--output", help="Archivo para guardar resultado de validación")
    
    args = parser.parse_args()
    
    try:
        # Cargar datos de receta
        with open(args.recipe_file, "r", encoding="utf-8") as f:
            recipe_data = json.load(f)
        
        # Inicializar validador
        validator = RecipeValidator()
        
        # Realizar validación
        can_proceed, validation_errors = validator.run_validation(recipe_data, args.scale)
        
        # Organizar resultado
        result = {
            "timestamp": datetime.now().isoformat(),
            "recipe_id": recipe_data.get("id", "unknown"),
            "recipe_name": recipe_data.get("name", "Unknown Recipe"),
            "scale": args.scale,
            "valid": can_proceed,
            "errors": [error.to_dict() for error in validation_errors],
            "critical_errors": sum(1 for e in validation_errors if e.severity == "CRITICAL"),
            "medium_errors": sum(1 for e in validation_errors if e.severity == "MEDIUM")
        }
        
        # Guardar resultado si se especificó archivo de salida
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Resultado de validación guardado en: {args.output}")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Imprimir resumen
        print(f"\nResumen de Validación para '{result['recipe_name']}' (Escala: {args.scale}):")
        print(f"  Estado: {'VÁLIDO' if result['valid'] else 'INVÁLIDO'}")
        print(f"  Errores críticos: {result['critical_errors']}")
        print(f"  Errores medios: {result['medium_errors']}")
        
        if not result['valid']:
            print("\nErrores críticos:")
            for error in [e for e in result['errors'] if e['severity'] == 'CRITICAL']:
                print(f"  - [{error['error_code']}] {error['message']}")
                if error['recommendation']:
                    print(f"    Recomendación: {error['recommendation']}")
        
        # Establecer código de salida según resultado
        sys.exit(0 if can_proceed else 1)
    
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado: {args.recipe_file}")
        sys.exit(2)
    except json.JSONDecodeError:
        print(f"Error: Formato JSON inválido en archivo: {args.recipe_file}")
        sys.exit(3)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(4) 