"""
Interfaz de chat para el asistente de recetas TRIVO-AI
"""
from recipe_assistant import RecipeAssistant
from app import mock_language_processing
import os
import json
from datetime import datetime
import colorama
from colorama import Fore, Style

# Inicializar colorama
colorama.init()

class RecipeChat:
    def __init__(self):
        """Inicializa la interfaz de chat para el asistente de recetas"""
        self.assistant = RecipeAssistant()
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_dir = "conversations"
        os.makedirs(self.save_dir, exist_ok=True)
    
    def display_welcome(self):
        """Muestra un mensaje de bienvenida"""
        print(Fore.GREEN + "\n" + "="*60)
        print(Fore.GREEN + " "*10 + "TRIVO-AI - ASISTENTE DE RECETAS DE PIZZA" + " "*10)
        print(Fore.GREEN + "="*60 + Style.RESET_ALL)
        print(f"\n{Fore.CYAN}El asistente te ayudará a definir una receta de pizza perfecta.")
        print(f"Responde a las preguntas o escribe tu idea para una pizza.{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Puedes escribir '{Fore.RED}salir{Fore.YELLOW}' en cualquier momento para terminar la conversación.{Style.RESET_ALL}")
        print("\n" + "-"*60)
    
    def run(self):
        """Ejecuta el chat interactivo"""
        self.display_welcome()
        
        print(f"\n{Fore.GREEN}Asistente:{Style.RESET_ALL} ¡Hola! Soy el asistente de TRIVO-AI. ¿Qué tipo de pizza quieres preparar hoy?")
        
        while True:
            print(f"\n{Fore.BLUE}Tú:{Style.RESET_ALL}", end=" ")
            user_input = input()
            
            if user_input.lower() in ["salir", "exit", "quit", "terminar"]:
                print(f"\n{Fore.GREEN}Asistente:{Style.RESET_ALL} Gracias por usar el asistente de TRIVO-AI. ¡Hasta pronto!")
                break
            
            # Obtener respuesta del asistente
            response = self.assistant.respond(user_input)
            print(f"\n{Fore.GREEN}Asistente:{Style.RESET_ALL} {response}")
            
            # Si ya tenemos toda la información necesaria, generar la receta
            if "Resumen de tu solicitud:" in response:
                self.generate_recipe()
                break
    
    def generate_recipe(self):
        """Genera y muestra una receta basada en la conversación"""
        # Construir el prompt para el generador de recetas
        prompt = self.assistant.construct_recipe_prompt()
        print(f"\n{Fore.YELLOW}Generando receta basada en tu solicitud...{Style.RESET_ALL}")
        
        # Llamar al generador de recetas
        recipe = mock_language_processing(prompt)
        
        # Mostrar la receta generada
        print(f"\n{Fore.GREEN}¡Receta generada con éxito!{Style.RESET_ALL}")
        print("\n" + "="*60)
        print(f"{Fore.CYAN}RECETA: {recipe['nombre']}{Style.RESET_ALL}")
        print("-"*60)
        print(f"{Fore.YELLOW}Descripción:{Style.RESET_ALL} {recipe['descripcion']}")
        
        print(f"\n{Fore.YELLOW}Ingredientes:{Style.RESET_ALL}")
        for ingrediente in recipe['ingredientes']:
            print(f"  • {ingrediente['name']}: {ingrediente['amount']} {ingrediente['unit']}")
        
        print(f"\n{Fore.YELLOW}Preparación:{Style.RESET_ALL}")
        for i, paso in enumerate(recipe['metodo']):
            print(f"  {i+1}. {paso}")
        
        print(f"\n{Fore.YELLOW}Información adicional:{Style.RESET_ALL}")
        print(f"  • Dificultad: {recipe['dificultad']}")
        print(f"  • Tiempo de preparación: {recipe['tiempo_preparacion']} min")
        print(f"  • Tiempo de cocción: {recipe['tiempo_coccion']} min")
        print(f"  • Porciones: {recipe['porciones']}")
        
        print("\n" + "="*60)
        
        # Guardar la conversación y la receta
        self.save_session(recipe)
    
    def save_session(self, recipe):
        """Guarda la conversación y la receta generada"""
        # Crear el archivo de la sesión
        session_file = os.path.join(self.save_dir, f"session_{self.conversation_id}.json")
        
        # Preparar los datos de la sesión
        session_data = {
            "conversation": self.assistant.conversation_history,
            "prompt": self.assistant.construct_recipe_prompt(),
            "recipe": recipe,
            "timestamp": datetime.now().isoformat()
        }
        
        # Guardar la sesión
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Fore.CYAN}Sesión guardada en: {session_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    chat = RecipeChat()
    chat.run() 