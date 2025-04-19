"""
Asistente de procesamiento de lenguaje natural para TRIVO-AI
Optimiza la captura de información para generación de recetas
"""
import re
import json
from datetime import datetime

class RecipeAssistant:
    def __init__(self):
        """Inicializa el asistente de procesamiento de lenguaje natural"""
        # Variables que el sistema necesita identificar para una receta completa
        self.required_variables = {
            "tipo_masa": None,  # normal, integral, sin gluten, etc.
            "tamaño": None,     # personal, mediana, familiar, etc.
            "estilo": None,     # napolitana, americana, detroit, etc.
            "caracteristicas": [],  # crujiente, suave, fina, gruesa, etc.
            "ingredientes": [],  # topping específicos solicitados
            "restricciones": [], # sin gluten, vegana, sin lactosa, etc.
            "ocasion": None,    # cumpleaños, halloween, navidad, etc.
            "nivel_experiencia": None  # principiante, intermedio, experto
        }
        
        # Patrones de identificación de variables
        self.patterns = {
            "tipo_masa": r"(masa|base) (de |)(integral|sin gluten|trigo|tradicional|fina|gruesa)",
            "tamaño": r"(tamaño|tamaño de|formato) (personal|individual|mediana|familiar|grande|pequeña)",
            "estilo": r"(estilo|tipo|como|al estilo) (napolitana|italiana|americana|detroit|chicago|new york)",
            "restricciones": r"(sin|no|evitar) (gluten|lactosa|lácteos|huevo|carne|animal)",
        }
        
        # Preguntas para solicitar información adicional
        self.questions = {
            "tipo_masa": "¿Qué tipo de masa prefieres para tu pizza? (tradicional, integral, sin gluten...)",
            "tamaño": "¿De qué tamaño necesitas la pizza? (personal, mediana, familiar...)",
            "estilo": "¿Algún estilo particular de pizza? (napolitana, americana, detroit...)",
            "caracteristicas": "¿Cómo prefieres la textura de la masa? (crujiente, suave, fina, gruesa...)",
            "ingredientes": "¿Qué ingredientes principales quieres incluir?",
            "restricciones": "¿Tienes alguna restricción dietética? (sin gluten, vegana, sin lactosa...)",
            "ocasion": "¿Es para alguna ocasión especial?",
            "nivel_experiencia": "¿Cuál es tu nivel de experiencia en preparación de pizzas?"
        }
        
        # Historial de conversación
        self.conversation_history = []
    
    def analyze_input(self, user_text):
        """Analiza el texto del usuario para extraer variables clave"""
        # Registrar entrada del usuario en historial
        self.conversation_history.append({
            "role": "user",
            "text": user_text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Extraer tipo de masa
        masa_match = re.search(self.patterns["tipo_masa"], user_text.lower())
        if masa_match:
            self.required_variables["tipo_masa"] = masa_match.group(0)
        
        # Extraer tamaño
        tamaño_match = re.search(self.patterns["tamaño"], user_text.lower())
        if tamaño_match:
            self.required_variables["tamaño"] = tamaño_match.group(0)
            
        # Extraer estilo
        estilo_match = re.search(self.patterns["estilo"], user_text.lower())
        if estilo_match:
            self.required_variables["estilo"] = estilo_match.group(0)
        
        # Extraer restricciones
        restricciones_match = re.search(self.patterns["restricciones"], user_text.lower())
        if restricciones_match and restricciones_match.group(0) not in self.required_variables["restricciones"]:
            self.required_variables["restricciones"].append(restricciones_match.group(0))
        
        # Detectar palabras clave de características
        caracteristicas_keywords = ["crujiente", "suave", "fina", "gruesa", "aireada", "densa"]
        for keyword in caracteristicas_keywords:
            if keyword in user_text.lower() and keyword not in self.required_variables["caracteristicas"]:
                self.required_variables["caracteristicas"].append(keyword)
        
        # Detectar ocasiones especiales
        ocasiones_keywords = ["cumpleaños", "halloween", "navidad", "fiesta", "aniversario", "celebración"]
        for ocasion in ocasiones_keywords:
            if ocasion in user_text.lower():
                self.required_variables["ocasion"] = ocasion
                break
        
        # Detectar nivel de experiencia
        nivel_keywords = {
            "principiante": ["primera vez", "novato", "principiante", "simple", "fácil"],
            "intermedio": ["intermedio", "algo de experiencia"],
            "experto": ["experto", "chef", "profesional", "avanzado"]
        }
        
        for nivel, keywords in nivel_keywords.items():
            for keyword in keywords:
                if keyword in user_text.lower():
                    self.required_variables["nivel_experiencia"] = nivel
                    break
        
        # Detectar ingredientes mencionados
        ingredientes_comunes = ["queso", "mozzarella", "tomate", "jamón", "pepperoni", "champiñones", 
                                "pimiento", "cebolla", "aceitunas", "anchoas", "piña", "calabaza",
                                "espinacas", "berenjena", "calabacín", "bacon", "pollo"]
        
        for ingrediente in ingredientes_comunes:
            if ingrediente in user_text.lower() and ingrediente not in self.required_variables["ingredientes"]:
                self.required_variables["ingredientes"].append(ingrediente)
        
        return self.required_variables
    
    def get_next_question(self):
        """Determina la siguiente pregunta basada en la información faltante"""
        # Priorizar preguntas sobre información crítica faltante
        critical_variables = ["tipo_masa", "tamaño", "restricciones"]
        
        for var in critical_variables:
            if not self.required_variables[var]:
                return self.questions[var]
        
        # Si todas las variables críticas están presentes, verificar si faltan ingredientes
        if not self.required_variables["ingredientes"]:
            return self.questions["ingredientes"]
        
        # Si aún faltan variables no críticas, preguntar por ellas
        for var, value in self.required_variables.items():
            if not value and var not in ["caracteristicas"]:  # Características puede quedar vacío
                return self.questions[var]
        
        # Si tenemos toda la información necesaria
        return None
    
    def respond(self, user_text):
        """Responde al texto del usuario, extrayendo información o solicitando más detalles"""
        self.analyze_input(user_text)
        
        next_question = self.get_next_question()
        if next_question:
            # Registrar respuesta del asistente en historial
            self.conversation_history.append({
                "role": "assistant",
                "text": next_question,
                "timestamp": datetime.now().isoformat()
            })
            return next_question
        else:
            # Si tenemos toda la información, construir un resumen
            summary = self.build_recipe_request_summary()
            
            # Registrar resumen en historial
            self.conversation_history.append({
                "role": "assistant",
                "text": "¡Perfecto! Tengo toda la información necesaria.",
                "timestamp": datetime.now().isoformat()
            })
            
            self.conversation_history.append({
                "role": "system",
                "text": summary,
                "timestamp": datetime.now().isoformat()
            })
            
            return "¡Perfecto! Tengo toda la información necesaria para generar tu receta personalizada.\n\n" + summary
    
    def build_recipe_request_summary(self):
        """Construye un resumen estructurado de la solicitud de receta"""
        summary_parts = ["Resumen de tu solicitud:"]
        
        if self.required_variables["tipo_masa"]:
            summary_parts.append(f"- Tipo de masa: {self.required_variables['tipo_masa']}")
        
        if self.required_variables["tamaño"]:
            summary_parts.append(f"- Tamaño: {self.required_variables['tamaño']}")
        
        if self.required_variables["estilo"]:
            summary_parts.append(f"- Estilo: {self.required_variables['estilo']}")
        
        if self.required_variables["caracteristicas"]:
            summary_parts.append(f"- Características: {', '.join(self.required_variables['caracteristicas'])}")
        
        if self.required_variables["ingredientes"]:
            summary_parts.append(f"- Ingredientes principales: {', '.join(self.required_variables['ingredientes'])}")
        
        if self.required_variables["restricciones"]:
            summary_parts.append(f"- Restricciones dietéticas: {', '.join(self.required_variables['restricciones'])}")
        
        if self.required_variables["ocasion"]:
            summary_parts.append(f"- Ocasión especial: {self.required_variables['ocasion']}")
        
        if self.required_variables["nivel_experiencia"]:
            summary_parts.append(f"- Nivel de experiencia: {self.required_variables['nivel_experiencia']}")
        
        return "\n".join(summary_parts)
    
    def construct_recipe_prompt(self):
        """Construye un prompt optimizado para el generador de recetas"""
        # Aquí se construiría el prompt final para el generador de recetas
        prompt_parts = []
        
        # Tipo de masa
        if self.required_variables["tipo_masa"]:
            prompt_parts.append(f"Masa {self.required_variables['tipo_masa']}")
        
        # Tamaño
        if self.required_variables["tamaño"]:
            prompt_parts.append(f"de tamaño {self.required_variables['tamaño']}")
        
        # Estilo
        if self.required_variables["estilo"]:
            prompt_parts.append(f"al estilo {self.required_variables['estilo']}")
        
        # Características
        if self.required_variables["caracteristicas"]:
            prompt_parts.append(f"con textura {', '.join(self.required_variables['caracteristicas'])}")
        
        # Ingredientes
        if self.required_variables["ingredientes"]:
            prompt_parts.append(f"que incluya {', '.join(self.required_variables['ingredientes'])}")
        
        # Restricciones
        if self.required_variables["restricciones"]:
            prompt_parts.append(f"con restricciones: {', '.join(self.required_variables['restricciones'])}")
        
        # Ocasión
        if self.required_variables["ocasion"]:
            prompt_parts.append(f"para {self.required_variables['ocasion']}")
        
        # Nivel de experiencia
        if self.required_variables["nivel_experiencia"]:
            prompt_parts.append(f"para un nivel {self.required_variables['nivel_experiencia']}")
        
        prompt = "Quiero una pizza " + " ".join(prompt_parts)
        return prompt
    
    def save_conversation(self, filename=None):
        """Guarda el historial de conversación en un archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(self.conversation_history, f, indent=2)
        
        return filename

# Ejemplo de uso
if __name__ == "__main__":
    assistant = RecipeAssistant()
    print("¡Hola! Soy el asistente de TRIVO-AI. ¿Qué tipo de pizza quieres preparar hoy?")
    
    while True:
        user_input = input("> ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            break
        
        response = assistant.respond(user_input)
        print(response)
        
        # Si ya tenemos toda la información necesaria, podemos terminar
        if "Resumen de tu solicitud:" in response:
            prompt = assistant.construct_recipe_prompt()
            print("\nPrompt para generador de recetas:")
            print(prompt)
            break
    
    # Guardar la conversación
    filename = assistant.save_conversation()
    print(f"\nConversación guardada en: {filename}") 