"""
Módulo de supervisión de LLM para TRIVO-AI

Este módulo implementa un supervisor basado en LLM que revisa, valida y aprueba
las salidas generadas por el sistema especializado TRIVO-AI antes de presentarlas
al usuario final.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class LLMSupervisor:
    """
    Supervisor basado en LLM que verifica la calidad, coherencia y precisión
    de las salidas generadas por TRIVO-AI antes de presentarlas al usuario.
    """
    
    def __init__(self, feedback_file_path="data/supervisor_feedback.json"):
        """
        Inicializa el supervisor LLM
        
        Args:
            feedback_file_path: Ruta al archivo donde se almacena la retroalimentación
        """
        self.logger = logging.getLogger('trivo.llm_supervisor')
        self.logger.info("Supervisor LLM inicializado correctamente")
        self.approval_history = []
        
        # Base de conocimiento para retroalimentación
        self.feedback_file_path = feedback_file_path
        self.feedback_db = self._load_feedback_database()
        
        # Umbral de aprendizaje (cuántas veces debe verse un patrón para incluirlo en reglas)
        self.learning_threshold = 3
        
        # Reglas aprendidas
        self.learned_rules = self.feedback_db.get("learned_rules", [])
    
    def review_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Revisa una receta generada por TRIVO-AI y verifica su coherencia,
        calidad y factibilidad técnica.
        
        Args:
            recipe_data: Datos completos de la receta generada por TRIVO-AI
            
        Returns:
            Receta revisada con anotaciones del supervisor y estado de aprobación
        """
        self.logger.info(f"Revisando receta: {recipe_data.get('name', 'Sin nombre')}")
        
        # Copiar la receta para no modificar la original
        reviewed_recipe = recipe_data.copy()
        
        # Realizar verificaciones
        validation_results = {
            "approved": True,
            "review_timestamp": datetime.now().isoformat(),
            "review_notes": [],
            "critical_issues": [],
            "improvement_suggestions": []
        }
        
        # Verificar coherencia de ingredientes
        self._validate_ingredients_coherence(reviewed_recipe, validation_results)
        
        # Verificar factibilidad técnica
        self._validate_technical_feasibility(reviewed_recipe, validation_results)
        
        # Verificar coherencia entre propiedades e ingredientes
        self._validate_properties_coherence(reviewed_recipe, validation_results)
        
        # Verificar instrucciones
        self._validate_instructions(reviewed_recipe, validation_results)
        
        # Aplicar reglas aprendidas
        self._apply_learned_rules(reviewed_recipe, validation_results)
        
        # Determinar aprobación final
        validation_results["approved"] = len(validation_results["critical_issues"]) == 0
        
        # Agregar resultados de validación a la receta
        reviewed_recipe["supervisor_review"] = validation_results
        
        # Registrar en historial
        self._record_review(reviewed_recipe["id"] if "id" in reviewed_recipe else "unknown", 
                          validation_results["approved"])
        
        return reviewed_recipe
    
    def review_lifecycle_analysis(self, lifecycle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Revisa un análisis de ciclo de vida generado por TRIVO-AI.
        
        Args:
            lifecycle_data: Datos del análisis de ciclo de vida
            
        Returns:
            Análisis revisado con anotaciones del supervisor
        """
        self.logger.info("Revisando análisis de ciclo de vida")
        
        # Copiar los datos para no modificar los originales
        reviewed_data = lifecycle_data.copy()
        
        validation_results = {
            "approved": True,
            "review_timestamp": datetime.now().isoformat(),
            "review_notes": [],
            "critical_issues": [],
            "improvement_suggestions": []
        }
        
        # Verificar proyecciones de tiempo
        self._validate_timeline_projections(reviewed_data, validation_results)
        
        # Verificar estimaciones de costos
        self._validate_cost_estimates(reviewed_data, validation_results)
        
        # Verificar análisis de viabilidad
        self._validate_feasibility_analysis(reviewed_data, validation_results)
        
        # Aplicar reglas aprendidas
        self._apply_learned_rules(reviewed_data, validation_results)
        
        # Determinar aprobación final
        validation_results["approved"] = len(validation_results["critical_issues"]) == 0
        
        # Agregar resultados de validación
        reviewed_data["supervisor_review"] = validation_results
        
        return reviewed_data
    
    def provide_feedback(self, recipe_id: str, feedback_type: str, issue_description: str, 
                        correct_action: str, is_critical: bool = False) -> bool:
        """
        Registra retroalimentación manual para mejorar el sistema de supervisión
        
        Args:
            recipe_id: Identificador de la receta revisada
            feedback_type: Tipo de retroalimentación (ingredients, instructions, etc.)
            issue_description: Descripción del problema detectado o no detectado
            correct_action: Acción correcta que debería haberse tomado
            is_critical: Si el problema es crítico y debería bloquear la aprobación
            
        Returns:
            True si se registró correctamente, False en caso contrario
        """
        try:
            # Crear nueva entrada de retroalimentación
            feedback_entry = {
                "recipe_id": recipe_id,
                "timestamp": datetime.now().isoformat(),
                "feedback_type": feedback_type,
                "issue_description": issue_description,
                "correct_action": correct_action,
                "is_critical": is_critical
            }
            
            # Agregar a la base de datos
            self.feedback_db["feedback"].append(feedback_entry)
            
            # Verificar si se supera el umbral para generar una nueva regla
            similar_feedback = [
                fb for fb in self.feedback_db["feedback"] 
                if fb["feedback_type"] == feedback_type and 
                fb["issue_description"].lower() == issue_description.lower()
            ]
            
            if len(similar_feedback) >= self.learning_threshold:
                self._generate_new_rule(feedback_type, issue_description, correct_action, is_critical)
            
            # Guardar base de datos actualizada
            self._save_feedback_database()
            
            self.logger.info(f"Retroalimentación registrada para receta {recipe_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al registrar retroalimentación: {str(e)}")
            return False
    
    def suggest_improvement(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sugiere mejoras específicas basadas en el análisis de la receta y
        el conocimiento acumulado del supervisor
        
        Args:
            recipe_data: Datos de la receta a mejorar
            
        Returns:
            Diccionario con sugerencias específicas para mejorar la receta
        """
        # Inicializar respuesta
        improvements = {
            "ingredients_adjustments": [],
            "instructions_improvements": [],
            "general_suggestions": []
        }
        
        # Analizar ingredientes para posibles mejoras
        ingredients = recipe_data.get("ingredients", {})
        properties = recipe_data.get("properties", {})
        
        # Sugerencias para hidratación
        if "harina" in "".join(ingredients.keys()).lower() and "agua" in "".join(ingredients.keys()).lower():
            flour_amount = sum(amount for ingredient, amount in ingredients.items() 
                             if "harina" in ingredient.lower())
            water_amount = sum(amount for ingredient, amount in ingredients.items() 
                             if "agua" in ingredient.lower())
            
            hydration = (water_amount / flour_amount) * 100 if flour_amount > 0 else 0
            
            # Sugerir ajustes de hidratación para diferentes tipos de masa
            if "tipo" in properties:
                product_type = properties.get("tipo", "").lower()
                
                if "pizza" in product_type and hydration < 60:
                    improvements["ingredients_adjustments"].append({
                        "ingredient": "agua",
                        "current": water_amount,
                        "suggested": round(flour_amount * 0.65, 1),  # 65% hidratación
                        "reason": "Una mayor hidratación (65%) mejora la extensibilidad de la masa de pizza"
                    })
                elif "pan" in product_type and hydration < 70:
                    improvements["ingredients_adjustments"].append({
                        "ingredient": "agua",
                        "current": water_amount,
                        "suggested": round(flour_amount * 0.72, 1),  # 72% hidratación
                        "reason": "Una hidratación del 70-75% es ideal para panes artesanales con buena miga"
                    })
        
        # Sugerencias para instrucciones
        instructions = recipe_data.get("instructions", [])
        
        # Verificar si hay instrucciones de temperatura
        has_temp = any("°c" in instruction.lower() or "grados" in instruction.lower() 
                      for instruction in instructions)
        
        if not has_temp:
            recipe_type = properties.get("type", "").lower()
            if "pizza" in recipe_type:
                improvements["instructions_improvements"].append({
                    "type": "add_temp",
                    "suggestion": "Precalentar el horno a 250°C (480°F) durante al menos 30 minutos antes de hornear para lograr una mejor cocción"
                })
            elif "pan" in recipe_type:
                improvements["instructions_improvements"].append({
                    "type": "add_temp",
                    "suggestion": "Hornear a 220°C (425°F) durante los primeros 15 minutos, luego reducir a 190°C (375°F) para completar la cocción"
                })
        
        # Analizar reglas aprendidas para generar sugerencias
        for rule in self.learned_rules:
            if not rule.get("is_critical", False):  # Solo usar reglas no críticas para sugerencias
                if rule["feedback_type"] == "general":
                    improvements["general_suggestions"].append(rule["correct_action"])
        
        return improvements
    
    def _validate_ingredients_coherence(self, recipe: Dict[str, Any], 
                                      validation: Dict[str, Any]) -> None:
        """
        Verifica la coherencia entre los ingredientes de la receta.
        """
        ingredients = recipe.get("ingredients", {})
        
        # Verificar proporción harina/agua para masas
        if "harina" in "".join(ingredients.keys()).lower() and "agua" in "".join(ingredients.keys()).lower():
            # Obtener cantidades (aproximadas si hay varios tipos)
            flour_amount = sum(amount for ingredient, amount in ingredients.items() 
                              if "harina" in ingredient.lower())
            water_amount = sum(amount for ingredient, amount in ingredients.items() 
                              if "agua" in ingredient.lower())
            
            hydration = (water_amount / flour_amount) * 100 if flour_amount > 0 else 0
            
            # Verificar si está dentro de rangos razonables para pizza (50%-75%)
            if hydration < 50:
                validation["review_notes"].append(f"Nivel de hidratación bajo: {hydration:.1f}%")
                validation["improvement_suggestions"].append("Considerar aumentar el agua para mejorar elasticidad")
            elif hydration > 75:
                validation["review_notes"].append(f"Nivel de hidratación alto: {hydration:.1f}%")
                if hydration > 85:
                    validation["critical_issues"].append(f"Hidratación excesiva ({hydration:.1f}%) puede hacer la masa inmanejable")
                else:
                    validation["improvement_suggestions"].append("Nivel de hidratación alto, asegurar técnica adecuada")
            else:
                validation["review_notes"].append(f"Hidratación óptima: {hydration:.1f}%")
        
        # Verificar presencia de levadura o fermento
        if not any("levadura" in ingredient.lower() or "fermento" in ingredient.lower() 
                  for ingredient in ingredients.keys()):
            validation["critical_issues"].append("No se detectó levadura o agente fermentativo")
    
    def _validate_technical_feasibility(self, recipe: Dict[str, Any], 
                                       validation: Dict[str, Any]) -> None:
        """
        Verifica la factibilidad técnica de la receta.
        """
        # Verificar restricciones dietéticas
        properties = recipe.get("properties", {})
        ingredients = recipe.get("ingredients", {})
        
        dietary_restrictions = properties.get("dietary_restrictions", [])
        
        # Verificar coherencia sin gluten
        if "gluten-free" in dietary_restrictions:
            gluten_ingredients = ["harina de trigo", "sémola", "harina de centeno"]
            for gluten_ing in gluten_ingredients:
                if any(gluten_ing in ingredient.lower() for ingredient in ingredients.keys()):
                    validation["critical_issues"].append(
                        f"Receta marcada sin gluten pero contiene {gluten_ing}"
                    )
            
            # Verificar si tiene agentes estructurantes para sin gluten
            has_binding_agent = any(binding in "".join(ingredients.keys()).lower() 
                                   for binding in ["xantana", "guar", "psyllium", "almidón", "fécula"])
            
            if not has_binding_agent:
                validation["improvement_suggestions"].append(
                    "Receta sin gluten debe incluir agentes de unión como goma xantana"
                )
        
        # Verificar coherencia vegana
        if "vegan" in dietary_restrictions:
            non_vegan = ["huevo", "leche", "mantequilla", "miel", "yogur"]
            for non_vegan_ing in non_vegan:
                if any(non_vegan_ing in ingredient.lower() for ingredient in ingredients.keys()):
                    validation["critical_issues"].append(
                        f"Receta marcada vegana pero contiene {non_vegan_ing}"
                    )
    
    def _validate_properties_coherence(self, recipe: Dict[str, Any], 
                                      validation: Dict[str, Any]) -> None:
        """
        Verifica la coherencia entre las propiedades declaradas y los ingredientes.
        """
        properties = recipe.get("properties", {})
        ingredients = recipe.get("ingredients", {})
        
        # Verificar coherencia de color
        color = properties.get("color")
        if color:
            if color == "red" or color == "danger":
                color_agents = ["tomate", "remolacha", "pimentón", "pimiento rojo"]
                if not any(agent in "".join(ingredients.keys()).lower() for agent in color_agents):
                    validation["improvement_suggestions"].append(
                        "Receta marcada como roja pero no se detectan agentes colorantes naturales"
                    )
            elif color == "green" or color == "success":
                color_agents = ["espinaca", "moringa", "matcha", "albahaca", "perejil"]
                if not any(agent in "".join(ingredients.keys()).lower() for agent in color_agents):
                    validation["improvement_suggestions"].append(
                        "Receta marcada como verde pero no se detectan agentes colorantes naturales"
                    )
    
    def _validate_instructions(self, recipe: Dict[str, Any], 
                             validation: Dict[str, Any]) -> None:
        """
        Verifica la calidad y completitud de las instrucciones.
        """
        instructions = recipe.get("instructions", [])
        
        # Verificar longitud mínima de instrucciones
        if len(instructions) < 3:
            validation["critical_issues"].append("Instrucciones insuficientes para preparar la receta")
        
        # Verificar menciones de tiempo y temperatura
        has_temp = any("°c" in instruction.lower() or "grados" in instruction.lower() 
                      for instruction in instructions)
        has_time = any(("minuto" in instruction.lower() or "hora" in instruction.lower()) 
                      for instruction in instructions)
        
        if not has_temp:
            validation["improvement_suggestions"].append("No se mencionan temperaturas de cocción")
        
        if not has_time:
            validation["improvement_suggestions"].append("No se especifican tiempos de preparación o cocción")
    
    def _validate_timeline_projections(self, lifecycle_data: Dict[str, Any], 
                                      validation: Dict[str, Any]) -> None:
        """
        Verifica las proyecciones de tiempo en el análisis de ciclo de vida.
        """
        stages = lifecycle_data.get("stages", [])
        
        # Verificar si hay etapas con duraciones poco realistas
        if stages:
            for stage in stages:
                if "duration" in stage:
                    # Verificar etapas demasiado cortas para su tipo
                    if stage.get("name", "").lower() == "desarrollo" and stage["duration"] < 14:
                        validation["improvement_suggestions"].append(
                            f"Etapa de desarrollo con duración de {stage['duration']} días parece optimista"
                        )
                    
                    if stage.get("name", "").lower() == "pruebas" and stage["duration"] < 7:
                        validation["improvement_suggestions"].append(
                            f"Etapa de pruebas con duración de {stage['duration']} días parece insuficiente"
                        )
    
    def _validate_cost_estimates(self, lifecycle_data: Dict[str, Any], 
                               validation: Dict[str, Any]) -> None:
        """
        Verifica las estimaciones de costos en el análisis de ciclo de vida.
        """
        costs = lifecycle_data.get("costs", {})
        
        # Verificar si hay categorías de costos omitidas
        essential_categories = ["materias_primas", "mano_obra", "equipamiento"]
        missing = [cat for cat in essential_categories if cat not in costs]
        
        if missing:
            validation["improvement_suggestions"].append(
                f"Análisis de costos incompleto: faltan categorías {', '.join(missing)}"
            )
        
        # Verificar margen de beneficio
        if "costo_total" in costs and "precio_venta" in costs:
            margin = (costs["precio_venta"] - costs["costo_total"]) / costs["precio_venta"] * 100
            
            if margin < 15:
                validation["critical_issues"].append(
                    f"Margen de beneficio muy bajo: {margin:.1f}%"
                )
            elif margin > 70:
                validation["review_notes"].append(
                    f"Margen de beneficio inusualmente alto: {margin:.1f}%"
                )
    
    def _validate_feasibility_analysis(self, lifecycle_data: Dict[str, Any], 
                                     validation: Dict[str, Any]) -> None:
        """
        Verifica el análisis de viabilidad en el ciclo de vida.
        """
        feasibility = lifecycle_data.get("feasibility", {})
        
        # Verificar campos esenciales
        essential_fields = ["technical_score", "market_score", "economic_score"]
        missing = [field for field in essential_fields if field not in feasibility]
        
        if missing:
            validation["improvement_suggestions"].append(
                f"Análisis de viabilidad incompleto: faltan métricas {', '.join(missing)}"
            )
        
        # Verificar coherencia entre puntuaciones y recomendación final
        if all(field in feasibility for field in essential_fields):
            avg_score = sum(feasibility[field] for field in essential_fields) / len(essential_fields)
            
            if avg_score < 5 and feasibility.get("recommendation") == "proceed":
                validation["critical_issues"].append(
                    f"Recomendación inconsistente: promedio de puntuación bajo ({avg_score:.1f}) pero se recomienda proceder"
                )
            elif avg_score > 7 and feasibility.get("recommendation") == "cancel":
                validation["critical_issues"].append(
                    f"Recomendación inconsistente: promedio de puntuación alto ({avg_score:.1f}) pero se recomienda cancelar"
                )
    
    def _record_review(self, recipe_id: str, approved: bool) -> None:
        """
        Registra una revisión en el historial de aprobaciones.
        
        Args:
            recipe_id: Identificador de la receta
            approved: Si fue aprobada o no
        """
        self.approval_history.append({
            "recipe_id": recipe_id,
            "timestamp": datetime.now().isoformat(),
            "approved": approved
        })
        
        self.logger.info(f"Receta {recipe_id}: {'aprobada' if approved else 'rechazada'}")
    
    def get_approval_history(self) -> List[Dict[str, Any]]:
        """
        Devuelve el historial de aprobaciones.
        
        Returns:
            Lista de registros de aprobación
        """
        return self.approval_history
    
    def get_supervisor_metrics(self) -> Dict[str, Any]:
        """
        Devuelve métricas del supervisor.
        
        Returns:
            Diccionario con métricas de rendimiento del supervisor
        """
        total_reviews = len(self.approval_history)
        
        if total_reviews == 0:
            return {
                "total_reviews": 0,
                "approval_rate": 0,
                "avg_reviews_per_day": 0,
                "learned_rules_count": len(self.learned_rules),
                "feedback_count": len(self.feedback_db.get("feedback", []))
            }
        
        approved = sum(1 for review in self.approval_history if review["approved"])
        
        # Calcular tasa de aprobación
        approval_rate = (approved / total_reviews) * 100
        
        # Calcular revisiones por día (simplificado)
        current_date = datetime.now().date()
        first_review_date = datetime.fromisoformat(self.approval_history[0]["timestamp"]).date()
        days_active = (current_date - first_review_date).days + 1  # Evitar división por cero
        reviews_per_day = total_reviews / days_active
        
        return {
            "total_reviews": total_reviews,
            "approved_reviews": approved,
            "rejected_reviews": total_reviews - approved,
            "approval_rate": approval_rate,
            "days_active": days_active,
            "avg_reviews_per_day": reviews_per_day,
            "learned_rules_count": len(self.learned_rules),
            "feedback_count": len(self.feedback_db.get("feedback", []))
        }
    
    def get_learned_rules(self) -> List[Dict[str, Any]]:
        """
        Devuelve las reglas aprendidas por el supervisor.
        
        Returns:
            Lista de reglas aprendidas
        """
        return self.learned_rules
    
    def _load_feedback_database(self) -> Dict[str, Any]:
        """
        Carga la base de datos de retroalimentación desde un archivo JSON.
        Si no existe, crea una estructura vacía.
        
        Returns:
            Diccionario con la base de datos de retroalimentación
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.feedback_file_path), exist_ok=True)
            
            # Intentar cargar el archivo si existe
            if os.path.exists(self.feedback_file_path):
                with open(self.feedback_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Crear estructura vacía
                empty_db = {
                    "feedback": [],
                    "learned_rules": []
                }
                
                # Guardar estructura vacía
                with open(self.feedback_file_path, 'w', encoding='utf-8') as f:
                    json.dump(empty_db, f, indent=2, ensure_ascii=False)
                
                return empty_db
                
        except Exception as e:
            self.logger.error(f"Error al cargar base de datos de retroalimentación: {str(e)}")
            # Devolver estructura vacía en caso de error
            return {
                "feedback": [],
                "learned_rules": []
            }
    
    def _save_feedback_database(self) -> bool:
        """
        Guarda la base de datos de retroalimentación en un archivo JSON.
        
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.feedback_file_path), exist_ok=True)
            
            # Actualizar reglas aprendidas en la base de datos
            self.feedback_db["learned_rules"] = self.learned_rules
            
            # Guardar base de datos
            with open(self.feedback_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_db, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar base de datos de retroalimentación: {str(e)}")
            return False
    
    def _generate_new_rule(self, feedback_type: str, issue_description: str, 
                          correct_action: str, is_critical: bool) -> bool:
        """
        Genera una nueva regla basada en retroalimentación recurrente.
        
        Args:
            feedback_type: Tipo de retroalimentación
            issue_description: Descripción del problema
            correct_action: Acción correcta a tomar
            is_critical: Si el problema es crítico
            
        Returns:
            True si se generó correctamente, False en caso contrario
        """
        try:
            # Verificar si ya existe una regla similar
            similar_rule = next((
                rule for rule in self.learned_rules
                if rule["feedback_type"] == feedback_type and 
                rule["issue_description"].lower() == issue_description.lower()
            ), None)
            
            # Si ya existe, actualizar la regla
            if similar_rule:
                similar_rule["correct_action"] = correct_action
                similar_rule["is_critical"] = is_critical
                similar_rule["updated_at"] = datetime.now().isoformat()
                similar_rule["times_reinforced"] = similar_rule.get("times_reinforced", 1) + 1
            else:
                # Crear nueva regla
                new_rule = {
                    "feedback_type": feedback_type,
                    "issue_description": issue_description,
                    "correct_action": correct_action,
                    "is_critical": is_critical,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "times_reinforced": 1
                }
                
                # Agregar a la lista de reglas
                self.learned_rules.append(new_rule)
            
            self.logger.info(f"Nueva regla generada: {issue_description}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al generar nueva regla: {str(e)}")
            return False
    
    def _apply_learned_rules(self, data: Dict[str, Any], validation: Dict[str, Any]) -> None:
        """
        Aplica las reglas aprendidas a la validación actual.
        
        Args:
            data: Datos a validar (receta o análisis de ciclo de vida)
            validation: Resultados de validación a actualizar
        """
        # Aplicar cada regla aprendida
        for rule in self.learned_rules:
            # Verificar si la regla aplica a estos datos
            if self._rule_applies_to_data(rule, data):
                # Agregar a las listas correspondientes según la criticidad
                if rule["is_critical"]:
                    validation["critical_issues"].append(rule["correct_action"])
                else:
                    validation["improvement_suggestions"].append(rule["correct_action"])
    
    def _rule_applies_to_data(self, rule: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """
        Verifica si una regla aprendida aplica a los datos actuales.
        
        Args:
            rule: Regla aprendida
            data: Datos a validar
            
        Returns:
            True si la regla aplica, False en caso contrario
        """
        # Reglas específicas por tipo
        feedback_type = rule["feedback_type"]
        
        # Reglas para ingredientes
        if feedback_type == "ingredients":
            ingredients = data.get("ingredients", {})
            ingredient_list = "".join(ingredients.keys()).lower()
            
            # Verificar si la descripción del problema está en los ingredientes
            return rule["issue_description"].lower() in ingredient_list
        
        # Reglas para instrucciones
        elif feedback_type == "instructions":
            instructions = data.get("instructions", [])
            instructions_text = " ".join(instructions).lower()
            
            # Verificar si la descripción del problema está en las instrucciones
            return rule["issue_description"].lower() in instructions_text
        
        # Reglas para restricciones dietéticas
        elif feedback_type == "dietary":
            properties = data.get("properties", {})
            dietary_restrictions = properties.get("dietary_restrictions", [])
            
            # Verificar si la descripción del problema está en las restricciones
            return rule["issue_description"].lower() in " ".join(dietary_restrictions).lower()
        
        # Reglas generales (siempre se aplican)
        elif feedback_type == "general":
            return True
        
        # Por defecto, no aplicar
        return False 