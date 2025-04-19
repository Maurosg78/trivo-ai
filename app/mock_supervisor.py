import logging
import json
import os
import random
from datetime import datetime
from pathlib import Path
from config import DATA_DIR

class MockLLMSupervisor:
    """Versión simulada del supervisor LLM para ambientes sin acceso a OpenAI."""
    
    def __init__(self):
        """Inicializa el supervisor LLM simulado."""
        self.logger = logging.getLogger("mock-supervisor")
        self.model = "mock-gpt"
        
        # Definir rutas de archivos
        self.history_file = os.path.join(DATA_DIR, "mock_supervisor_history.json")
        self.feedback_db_file = os.path.join(DATA_DIR, "mock_supervisor_feedback.json")
        
        # Inicializar datos
        self.approval_history = []
        self.feedback_db = {"learned_rules": [], "feedback_entries": []}
        
        self.logger.info("Supervisor simulado inicializado (modo MOCK)")
    
    def review_recipe(self, recipe_data):
        """
        Simula la revisión de una receta.
        
        Args:
            recipe_data (dict): Datos de la receta a revisar
            
        Returns:
            dict: Resultado simulado de la revisión
        """
        self.logger.info(f"Revisando receta {recipe_data.get('id', 'sin_id')} (SIMULADO)")
        
        # 90% de probabilidad de aprobar la receta
        is_approved = random.random() < 0.9
        
        result = {
            "approved": is_approved,
            "feedback": "Esta es una revisión simulada generada por el supervisor en modo mock."
        }
        
        # Si no es aprobada, generar una versión corregida simulada
        if not is_approved:
            result["corrected_recipe"] = {
                "nombre": recipe_data.get("nombre", "") + " (versión corregida)",
                "ingredientes": recipe_data.get("ingredientes", ""),
                "instrucciones": recipe_data.get("instrucciones", "") + "\n(Paso adicional para corrección simulada)"
            }
        
        # Registrar en el historial
        self._record_review(recipe_data.get("id", "mock-id"), result)
        
        return result
    
    def provide_feedback(self, recipe_id, feedback_type, issue_description, correct_action, is_critical=False):
        """
        Simula el registro de retroalimentación.
        
        Args:
            recipe_id (str): ID de la receta
            feedback_type (str): Tipo de retroalimentación
            issue_description (str): Descripción del problema
            correct_action (str): Acción correctiva sugerida
            is_critical (bool): Si es un problema crítico
            
        Returns:
            bool: True simulando éxito
        """
        self.logger.info(f"Registrando retroalimentación para receta {recipe_id} (SIMULADO)")
        
        # Crear entrada de retroalimentación
        feedback_entry = {
            "recipe_id": recipe_id,
            "feedback_type": feedback_type,
            "issue_description": issue_description,
            "correct_action": correct_action,
            "is_critical": is_critical,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Guardar en el historial de retroalimentación simulado
        self.feedback_db["feedback_entries"].append(feedback_entry)
        
        # Simular creación de regla si es crítico
        if is_critical:
            new_rule = {
                "feedback_type": feedback_type,
                "issue_description": issue_description,
                "correct_action": correct_action,
                "is_critical": is_critical,
                "times_reinforced": 1,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.feedback_db["learned_rules"].append(new_rule)
        
        return True
    
    def _record_review(self, recipe_id, result):
        """Registra una revisión simulada en el historial."""
        review_entry = {
            "recipe_id": recipe_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "approved": result["approved"],
            "feedback": result["feedback"]
        }
        
        self.approval_history.append(review_entry)
    
    def get_approval_history(self):
        """Devuelve un historial de aprobaciones simulado."""
        return self.approval_history
    
    def get_learned_rules(self):
        """Devuelve reglas aprendidas simuladas."""
        return self.feedback_db.get("learned_rules", []) 