#!/usr/bin/env python3
"""
TRIVO-AI - Sistema Inteligente para Optimización de Recetas

Este script es el punto de entrada principal para el sistema TRIVO-AI,
permitiendo a los usuarios interactuar con el optimizador de recetas y
el validador de formulaciones sin gluten.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from scripts.data_collection import get_nutritional_data, save_to_csv
from scripts.training import formulations, optimize_recipe
from scripts.genetic_optimizer import optimize_genetic

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("trivoai.log"),
    ],
)
logger = logging.getLogger("TRIVO-AI")

def validate_recipe(recipe_file, scale="individual", output_file=None):
    """Valida una receta usando el sistema de validación crítica."""
    try:
        # Importar el módulo de validación desde scripts/validation_system
        sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))
        from validation_system.validation_system import RecipeValidator
        
        logger.info(f"Validando receta: {recipe_file} (Escala: {scale})")
        
        # Cargar receta
        with open(recipe_file, "r", encoding="utf-8") as f:
            recipe_data = json.load(f)
        
        # Inicializar validador
        validator = RecipeValidator()
        
        # Ejecutar validación
        can_proceed, validation_errors = validator.run_validation(recipe_data, scale)
        
        # Organizar resultado
        result = {
            "timestamp": datetime.now().isoformat(),
            "recipe_id": recipe_data.get("id", "unknown"),
            "recipe_name": recipe_data.get("name", "Unknown Recipe"),
            "scale": scale,
            "valid": can_proceed,
            "errors": [error.to_dict() for error in validation_errors],
            "critical_errors": sum(1 for e in validation_errors if e.severity == "CRITICAL"),
            "medium_errors": sum(1 for e in validation_errors if e.severity == "MEDIUM")
        }
        
        # Guardar resultado si se especificó archivo de salida
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Resultado guardado en: {output_file}")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Imprimir resumen
        print(f"\nResumen de Validación para '{result['recipe_name']}' (Escala: {scale}):")
        print(f"  Estado: {'VÁLIDO' if result['valid'] else 'INVÁLIDO'}")
        print(f"  Errores críticos: {result['critical_errors']}")
        print(f"  Errores medios: {result['medium_errors']}")
        
        if not result['valid']:
            print("\nErrores críticos detectados:")
            for error in [e for e in result['errors'] if e['severity'] == 'CRITICAL']:
                print(f"  - [{error['error_code']}] {error['message']}")
                if error['recommendation']:
                    print(f"    Recomendación: {error['recommendation']}")
        
        return can_proceed
    
    except Exception as e:
        logger.error(f"Error al validar receta: {str(e)}")
        print(f"Error: {str(e)}")
        return False

def check_validation_system(output_file=None):
    """Verifica la integridad del sistema de validación."""
    try:
        # Importar el módulo de verificación
        sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))
        from validation_system.check_system import check_system_integrity, save_check_result
        
        logger.info("Verificando integridad del sistema de validación")
        
        # Ejecutar verificación
        result = check_system_integrity()
        
        # Guardar y mostrar resultado
        save_check_result(result, output_file)
        
        return result["status"] == "OK"
    
    except Exception as e:
        logger.error(f"Error al verificar sistema: {str(e)}")
        print(f"Error: {str(e)}")
        return False

def collect_nutritional_data(ingredients_list):
    """Recolecta datos nutricionales y los guarda en CSV."""
    print("Recolectando datos nutricionales...")
    nutritional_data = []
    for ingredient in ingredients_list:
        data = get_nutritional_data(ingredient)
        if data:
            nutritional_data.append(data)
    if nutritional_data:
        os.makedirs('./data/processed', exist_ok=True)
        save_to_csv(nutritional_data, './data/processed/nutritional_data.csv')

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="TRIVO-AI - Sistema Inteligente para Optimización de Recetas")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando para validar receta
    validate_parser = subparsers.add_parser("validate", help="Valida una receta")
    validate_parser.add_argument("recipe_file", help="Archivo JSON con la receta a validar")
    validate_parser.add_argument("--scale", choices=["individual", "small_business", "industrial"], 
                               default="individual", help="Escala de producción")
    validate_parser.add_argument("--output", help="Archivo para guardar resultado de validación")
    
    # Comando para verificar sistema
    check_parser = subparsers.add_parser("check-system", help="Verifica la integridad del sistema de validación")
    check_parser.add_argument("--output", help="Archivo para guardar resultado de verificación")
    
    # Comando para recolectar datos nutricionales
    collect_parser = subparsers.add_parser("collect-data", help="Recolecta datos nutricionales")
    collect_parser.add_argument("--ingredients", nargs="+", help="Lista de ingredientes")
    
    # Comando para optimizar receta genéticamente
    optimize_parser = subparsers.add_parser("optimize-genetic", help="Optimiza una receta usando algoritmo genético")
    optimize_parser.add_argument("masa_name", help="Nombre de la masa a optimizar")
    
    args = parser.parse_args()
    
    if args.command == "validate":
        validate_recipe(args.recipe_file, args.scale, args.output)
    elif args.command == "check-system":
        check_validation_system(args.output)
    elif args.command == "collect-data":
        ingredients = args.ingredients or [
            'cauliflower', 'chickpea', 'rice flour', 'potato flour', 'corn starch',
            'olive oil', 'xanthan gum', 'sugar', 'salt'
        ]
        collect_nutritional_data(ingredients)
    elif args.command == "optimize-genetic":
        optimize_genetic(args.masa_name)
    else:
        # Comportamiento por defecto (retrocompatibilidad)
        os.makedirs('./data/processed', exist_ok=True)
        ingredients_list = [
            'cauliflower', 'chickpea', 'rice flour', 'potato flour', 'corn starch',
            'olive oil', 'xanthan gum', 'sugar', 'salt'
        ]
        collect_nutritional_data(ingredients_list)
        
        for masa_name in ['C12', 'G12']:
            optimize_genetic(masa_name)

if __name__ == "__main__":
    main()