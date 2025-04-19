import os
import json
import logging
import time
from datetime import datetime
import openai
from config import OPENAI_API_KEY, BASE_DIR, DATA_DIR

class LLMSupervisor:
    """Supervisor de LLM para revisión y corrección de recetas generadas por IA."""
    
    def __init__(self):
        """Inicializa el supervisor LLM."""
        # Configurar cliente de OpenAI
        openai.api_key = OPENAI_API_KEY
        self.model = "gpt-4-turbo"
        
        # Definir rutas de archivos
        self.history_file = os.path.join(DATA_DIR, "supervisor_history.json")
        self.feedback_db_file = os.path.join(DATA_DIR, "supervisor_feedback.json")
        
        # Cargar datos
        self.approval_history = self._load_history()
        self.feedback_db = self._load_feedback_db()
        
        # Asegurar que existan las estructuras de datos necesarias
        if "learned_rules" not in self.feedback_db:
            self.feedback_db["learned_rules"] = []
        if "feedback_entries" not in self.feedback_db:
            self.feedback_db["feedback_entries"] = []
    
    def _load_history(self):
        """Carga el historial de aprobaciones del archivo JSON."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.error("Archivo de historial de supervisor corrupto. Creando uno nuevo.")
                return []
        return []
    
    def _save_history(self):
        """Guarda el historial de aprobaciones en el archivo JSON."""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.approval_history, f, indent=2, ensure_ascii=False)
    
    def _load_feedback_db(self):
        """Carga la base de datos de retroalimentación del archivo JSON."""
        if os.path.exists(self.feedback_db_file):
            try:
                with open(self.feedback_db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.error("Archivo de retroalimentación corrupto. Creando uno nuevo.")
                return {"learned_rules": [], "feedback_entries": []}
        return {"learned_rules": [], "feedback_entries": []}
    
    def _save_feedback_db(self):
        """Guarda la base de datos de retroalimentación en el archivo JSON."""
        with open(self.feedback_db_file, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_db, f, indent=2, ensure_ascii=False)
    
    def review_recipe(self, recipe_data):
        """
        Revisa una receta generada por IA y decide si es aceptable o necesita corrección.
        
        Args:
            recipe_data (dict): Datos de la receta a revisar
            
        Returns:
            dict: Resultado de la revisión con los siguientes campos:
                - approved (bool): Si la receta fue aprobada
                - feedback (str): Comentarios sobre la revisión
                - corrected_recipe (dict, opcional): Versión corregida si fue rechazada
        """
        recipe_id = recipe_data.get("id", "sin_id")
        recipe_text = f"Nombre: {recipe_data.get('nombre', '')}\n"
        recipe_text += f"Ingredientes: {recipe_data.get('ingredientes', '')}\n"
        recipe_text += f"Instrucciones: {recipe_data.get('instrucciones', '')}\n"
        
        # Aplicar reglas aprendidas para una pre-evaluación
        pre_evaluation = self._apply_learned_rules(recipe_data)
        
        # Si hay problemas críticos identificados en las reglas aprendidas, rechazar inmediatamente
        if pre_evaluation["has_critical_issues"]:
            result = {
                "approved": False,
                "feedback": pre_evaluation["feedback"],
                "corrected_recipe": self._generate_corrected_recipe(recipe_data, pre_evaluation["feedback"])
            }
            self._record_review(recipe_id, result)
            return result
        
        # Criterios de evaluación
        prompt = f"""Como supervisor de calidad para recetas de pizza, evalúa la siguiente receta:

{recipe_text}

Criterios de evaluación:
1. Seguridad alimentaria: Sin instrucciones peligrosas o ingredientes crudos incorrectamente tratados
2. Completitud: Contiene todos los pasos necesarios para hacer la pizza
3. Claridad: Instrucciones fáciles de seguir
4. Factibilidad: La receta es realista y se puede hacer con equipo doméstico
5. Calidad culinaria: Combinaciones apropiadas de ingredientes y técnicas culinarias

Si encuentras problemas en la receta basados en estos criterios:
1. Describe específicamente qué está mal
2. Explica cómo debería corregirse
3. Da una versión corregida de la receta completa

También considera estas reglas específicas identificadas en revisiones anteriores:
{self._format_learned_rules_for_prompt()}

Responde con JSON en este formato:
{{
    "approved": true/false,
    "feedback": "Explicación detallada de la evaluación",
    "corrected_recipe": {{receta corregida completa}} (solo si approved=false)
}}
"""

        try:
            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un chef experto que supervisa la calidad de recetas de pizza."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            # Extraer y parsear la respuesta
            response_text = completion.choices[0].message.content.strip()
            result = json.loads(response_text)
            
            # Asegurar que el resultado contiene los campos esperados
            if "approved" not in result:
                raise ValueError("La respuesta del LLM no contiene el campo 'approved'")
            
            # Registrar esta revisión en el historial
            self._record_review(recipe_id, result)
            
            return result
            
        except Exception as e:
            logging.error(f"Error durante la revisión de la receta: {str(e)}")
            # En caso de error, aprobar por defecto para no bloquear al usuario
            default_result = {
                "approved": True,
                "feedback": "Error en la revisión automática. Aprobado por defecto."
            }
            self._record_review(recipe_id, default_result)
            return default_result
    
    def _record_review(self, recipe_id, result):
        """Registra una revisión en el historial."""
        review_entry = {
            "recipe_id": recipe_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "approved": result["approved"],
            "feedback": result["feedback"]
        }
        
        self.approval_history.append(review_entry)
        self._save_history()
    
    def _apply_learned_rules(self, recipe_data):
        """
        Aplica las reglas aprendidas a la receta para identificar problemas conocidos.
        
        Args:
            recipe_data (dict): Datos de la receta
            
        Returns:
            dict: Resultado de la pre-evaluación con feedback y si hay problemas críticos
        """
        issues = []
        has_critical_issues = False
        
        # Convertir la receta a texto para buscar problemas
        recipe_text = f"{recipe_data.get('nombre', '')}\n"
        recipe_text += f"{recipe_data.get('ingredientes', '')}\n"
        recipe_text += f"{recipe_data.get('instrucciones', '')}\n"
        recipe_text = recipe_text.lower()
        
        # Aplicar cada regla aprendida
        for rule in self.feedback_db.get("learned_rules", []):
            # Palabras clave para buscar en la descripción del problema
            keywords = rule.get("issue_description", "").lower().split()
            
            # Verificar si las palabras clave están presentes en la receta
            if any(keyword in recipe_text for keyword in keywords if len(keyword) > 3):
                issues.append(f"• {rule.get('issue_description')}: {rule.get('correct_action')}")
                
                # Marcar como crítico si alguna regla lo es
                if rule.get("is_critical", False):
                    has_critical_issues = True
        
        return {
            "has_critical_issues": has_critical_issues,
            "feedback": "\n".join(issues) if issues else "No se encontraron problemas conocidos."
        }
    
    def _generate_corrected_recipe(self, recipe_data, feedback):
        """
        Genera una versión corregida de la receta basada en el feedback.
        
        Args:
            recipe_data (dict): Datos originales de la receta
            feedback (str): Feedback detallando los problemas
            
        Returns:
            dict: Versión corregida de la receta
        """
        try:
            recipe_text = f"Nombre: {recipe_data.get('nombre', '')}\n"
            recipe_text += f"Ingredientes: {recipe_data.get('ingredientes', '')}\n"
            recipe_text += f"Instrucciones: {recipe_data.get('instrucciones', '')}\n"
            
            prompt = f"""Como chef experto, corrige esta receta de pizza:

{recipe_text}

Los problemas identificados son:
{feedback}

Proporciona una versión corregida de la receta completa en formato JSON:
{{
    "nombre": "nombre corregido",
    "ingredientes": "ingredientes corregidos",
    "instrucciones": "instrucciones corregidas"
}}
"""

            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un chef experto que corrige recetas de pizza."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            # Extraer y parsear la respuesta
            response_text = completion.choices[0].message.content.strip()
            return json.loads(response_text)
            
        except Exception as e:
            logging.error(f"Error al generar corrección: {str(e)}")
            # En caso de error, devolver la receta original
            return recipe_data
    
    def provide_feedback(self, recipe_id, feedback_type, issue_description, correct_action, is_critical=False):
        """
        Registra retroalimentación para mejorar el supervisor.
        
        Args:
            recipe_id (str): ID de la receta
            feedback_type (str): Tipo de retroalimentación (seguridad, completitud, etc.)
            issue_description (str): Descripción del problema
            correct_action (str): Acción correctiva recomendada
            is_critical (bool): Si es un problema crítico
            
        Returns:
            bool: True si se registró correctamente
        """
        try:
            # Crear entrada de retroalimentación
            feedback_entry = {
                "recipe_id": recipe_id,
                "feedback_type": feedback_type,
                "issue_description": issue_description,
                "correct_action": correct_action,
                "is_critical": is_critical,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Guardar en el historial de retroalimentación
            self.feedback_db["feedback_entries"].append(feedback_entry)
            
            # Comprobar si ya existe una regla similar
            existing_rule = None
            for rule in self.feedback_db["learned_rules"]:
                if (rule["feedback_type"] == feedback_type and 
                    self._similarity_score(rule["issue_description"], issue_description) > 0.7):
                    existing_rule = rule
                    break
            
            # Actualizar regla existente o crear nueva
            if existing_rule:
                existing_rule["times_reinforced"] = existing_rule.get("times_reinforced", 0) + 1
                # Actualizar is_critical si ahora es crítico
                if is_critical:
                    existing_rule["is_critical"] = True
            else:
                # Crear nueva regla aprendida
                new_rule = {
                    "feedback_type": feedback_type,
                    "issue_description": issue_description,
                    "correct_action": correct_action,
                    "is_critical": is_critical,
                    "times_reinforced": 1,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.feedback_db["learned_rules"].append(new_rule)
            
            # Guardar cambios
            self._save_feedback_db()
            return True
            
        except Exception as e:
            logging.error(f"Error al registrar retroalimentación: {str(e)}")
            return False
    
    def _similarity_score(self, text1, text2):
        """
        Calcula un puntaje de similitud simple entre dos textos.
        
        Args:
            text1 (str): Primer texto
            text2 (str): Segundo texto
            
        Returns:
            float: Puntaje de similitud entre 0 y 1
        """
        # Convertir a minúsculas y dividir en palabras
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calcular intersección y unión
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        # Puntaje Jaccard de similitud
        if len(union) == 0:
            return 0
        return len(intersection) / len(union)
    
    def _format_learned_rules_for_prompt(self):
        """
        Formatea las reglas aprendidas para incluirlas en el prompt del LLM.
        
        Returns:
            str: Texto formateado con las reglas aprendidas
        """
        if not self.feedback_db.get("learned_rules"):
            return "No hay reglas específicas adicionales."
        
        # Ordenar reglas por relevancia (críticas primero, luego por refuerzos)
        sorted_rules = sorted(
            self.feedback_db["learned_rules"], 
            key=lambda x: (not x.get("is_critical", False), -x.get("times_reinforced", 0))
        )
        
        # Limitar a las 10 reglas más relevantes para evitar un prompt demasiado largo
        top_rules = sorted_rules[:10]
        
        rules_text = ""
        for i, rule in enumerate(top_rules, 1):
            critical_marker = " [CRÍTICO]" if rule.get("is_critical", False) else ""
            rules_text += f"{i}. {rule.get('issue_description')}: {rule.get('correct_action')}{critical_marker}\n"
        
        return rules_text
    
    def get_approval_history(self):
        """
        Obtiene el historial de aprobaciones.
        
        Returns:
            list: Lista de revisiones realizadas
        """
        return self.approval_history
    
    def get_learned_rules(self):
        """
        Obtiene las reglas aprendidas.
        
        Returns:
            list: Lista de reglas aprendidas
        """
        return self.feedback_db.get("learned_rules", []) 