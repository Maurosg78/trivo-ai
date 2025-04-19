#!/usr/bin/env python
"""
Interfaz de línea de comandos para PizzaAI

Este script permite interactuar con el sistema PizzaAI desde la línea de comandos,
facilitando pruebas rápidas y generación de recetas sin necesidad de la interfaz web.
"""

import sys
import json
import argparse
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar configuración y componentes
from config import DATA_DIR, DEBUG

# Importar los módulos correctos con fallback a mock
try:
    from app.llm_supervisor import LLMSupervisor
except ImportError:
    from app.mock_supervisor import MockLLMSupervisor as LLMSupervisor

try:
    from trivo.features.nlp.language_processor import LanguageProcessor
except ImportError:
    try:
        from src.features.nlp.language_processor import LanguageProcessor
    except ImportError:
        from app.mock_language_processor import MockLanguageProcessor as LanguageProcessor

def create_recipe(input_text):
    """Crea una receta basada en el texto proporcionado"""
    processor = LanguageProcessor()
    return processor.process_request(input_text)

def analyze_description(description):
    """Analiza una descripción de pizza"""
    processor = LanguageProcessor()
    return processor.analyze_pizza_description(description)

def review_recipe(recipe_file):
    """Revisa una receta existente usando el supervisor"""
    supervisor = LLMSupervisor()
    
    try:
        with open(recipe_file, 'r', encoding='utf-8') as f:
            recipe_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return {"error": f"Error al leer el archivo de receta: {e}"}
    
    return supervisor.review_recipe(recipe_data)

def save_recipe(recipe_data, output_file=None):
    """Guarda una receta en un archivo JSON"""
    if output_file is None:
        recipe_id = recipe_data.get("id", "unknown")
        output_file = f"{DATA_DIR}/recipe_{recipe_id}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recipe_data, f, indent=2, ensure_ascii=False)
    
    return output_file

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Interfaz de línea de comandos para PizzaAI")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando: crear
    create_parser = subparsers.add_parser("crear", help="Crear una nueva receta")
    create_parser.add_argument("descripcion", help="Descripción en lenguaje natural de la receta deseada")
    create_parser.add_argument("-o", "--output", help="Archivo de salida para guardar la receta")
    
    # Comando: analizar
    analyze_parser = subparsers.add_parser("analizar", help="Analizar una descripción de pizza")
    analyze_parser.add_argument("descripcion", help="Descripción en lenguaje natural de la pizza")
    
    # Comando: revisar
    review_parser = subparsers.add_parser("revisar", help="Revisar una receta existente")
    review_parser.add_argument("archivo", help="Archivo JSON con la receta a revisar")
    
    # Comando: reglas
    rules_parser = subparsers.add_parser("reglas", help="Mostrar reglas aprendidas")
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Ejecutar el comando correspondiente
    if args.command == "crear":
        print(f"Creando receta basada en: '{args.descripcion}'")
        recipe_data = create_recipe(args.descripcion)
        
        if recipe_data.get("success", False):
            output_file = save_recipe(recipe_data, args.output)
            print(f"Receta creada con éxito: {recipe_data.get('nombre', 'Sin nombre')}")
            print(f"Guardada en: {output_file}")
            print("\nResumen:")
            print(f"- ID: {recipe_data.get('id', 'N/A')}")
            print(f"- Ingredientes: {recipe_data.get('ingredientes', 'N/A')[:100]}...")
        else:
            print(f"Error al crear la receta: {recipe_data.get('message', 'Error desconocido')}")
    
    elif args.command == "analizar":
        print(f"Analizando descripción: '{args.descripcion}'")
        analysis = analyze_description(args.descripcion)
        print("\nResultado del análisis:")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    elif args.command == "revisar":
        print(f"Revisando receta en: '{args.archivo}'")
        result = review_recipe(args.archivo)
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Resultado: {'Aprobada' if result['approved'] else 'Rechazada'}")
            print(f"Feedback: {result['feedback']}")
            
            if not result['approved'] and 'corrected_recipe' in result:
                print("\nSugerencias de corrección disponibles.")
                corrected_file = save_recipe(result['corrected_recipe'], 
                                           f"{args.archivo.rsplit('.', 1)[0]}_corregida.json")
                print(f"Versión corregida guardada en: {corrected_file}")
    
    elif args.command == "reglas":
        supervisor = LLMSupervisor()
        rules = supervisor.get_learned_rules()
        print(f"Reglas aprendidas ({len(rules)}):")
        for i, rule in enumerate(rules, 1):
            print(f"\n[{i}] {rule.get('feedback_type', 'N/A')} {'[CRÍTICA]' if rule.get('is_critical') else ''}")
            print(f"Problema: {rule.get('issue_description', 'N/A')}")
            print(f"Acción correctiva: {rule.get('correct_action', 'N/A')}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 