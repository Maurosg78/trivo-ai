#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para ejecutar el sistema de validación de recetas.

Este script permite validar recetas y verificar la integridad del sistema
de validación desde la línea de comandos.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Añadir el directorio raíz al PYTHONPATH para poder importar los módulos
root_dir = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, root_dir)

# Importar el motor de validación
from src.features.validation.validation_engine import (
    ValidationEngine, check_system_integrity, quick_validate_recipe
)

# Crear directorios necesarios para logs
logs_dir = os.path.join(root_dir, "logs")
reports_dir = os.path.join(root_dir, "reports")
data_dir = os.path.join(root_dir, "data")

for dir_path in [logs_dir, reports_dir, data_dir]:
    os.makedirs(dir_path, exist_ok=True)

# Configurar logging
log_file = os.path.join(logs_dir, f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("validation_script")

def validate_recipe(args):
    """Valida una receta usando el motor de validación."""
    try:
        # Verificar que el archivo existe
        if not os.path.exists(args.recipe_file):
            logger.error(f"El archivo de receta {args.recipe_file} no existe")
            return 1
        
        # Determinar el archivo de salida si no se especificó
        if args.output_file is None:
            base_name = os.path.basename(args.recipe_file)
            name_without_ext = os.path.splitext(base_name)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output_file = os.path.join(reports_dir, f"validation_{name_without_ext}_{timestamp}.json")
        
        # Validar la receta
        logger.info(f"Validando receta desde {args.recipe_file}")
        logger.info(f"Tipo de receta: {args.recipe_type}")
        logger.info(f"Escala de producción: {args.production_scale}")
        
        summary = quick_validate_recipe(
            recipe_file=args.recipe_file,
            recipe_type=args.recipe_type,
            production_scale=args.production_scale,
            output_file=args.output_file
        )
        
        # Imprimir resumen
        print("\n=== Resumen de Validación ===")
        print(f"Es viable: {'Sí' if summary['is_viable'] else 'No'}")
        print(f"Total reglas verificadas: {summary['total_rules_checked']}")
        print(f"Total problemas: {summary['total_issues']}")
        print("\nProblemas por severidad:")
        print(f"  Críticos: {summary['issues_by_severity']['critical']}")
        print(f"  Medios: {summary['issues_by_severity']['medium']}")
        print(f"  Bajos: {summary['issues_by_severity']['low']}")
        
        print("\nRecomendaciones:")
        if summary['recommendations']:
            for i, rec in enumerate(summary['recommendations'], 1):
                print(f"{i}. {rec}")
        else:
            print("No hay recomendaciones")
        
        print(f"\nResultados detallados guardados en: {args.output_file}")
        
        # Devolver código de salida según viabilidad
        return 0 if summary['is_viable'] else 2
        
    except Exception as e:
        logger.error(f"Error al validar receta: {str(e)}")
        return 1

def check_integrity(args):
    """Verifica la integridad del sistema de validación."""
    try:
        # Ejecutar verificación
        logger.info("Verificando integridad del sistema de validación")
        result = check_system_integrity()
        
        # Imprimir resultados
        print("\n=== Verificación de Integridad ===")
        if result["status"] == "OK":
            print("Estado: OK")
            print(f"Reglas de validación cargadas: {result['rules_count']}")
            print("\nReglas por severidad:")
            print(f"  Críticas: {result['rules_by_severity']['critical']}")
            print(f"  Medias: {result['rules_by_severity']['medium']}")
            print(f"  Bajas: {result['rules_by_severity']['low']}")
            
            print(f"\nCategorías de límites de ingredientes: {result['ingredient_limits_count']}")
            print(f"Parámetros de proceso: {result['process_params_count']}")
            
            print("\nDirectorios necesarios:")
            for dir_name, exists in result["directories_ready"].items():
                status = "✓" if exists else "✗"
                print(f"  {dir_name}: {status}")
        else:
            print(f"Estado: ERROR")
            print(f"Mensaje de error: {result['error_message']}")
        
        return 0 if result["status"] == "OK" else 1
        
    except Exception as e:
        logger.error(f"Error al verificar integridad: {str(e)}")
        return 1

def create_sample_recipe(args):
    """Crea una receta de ejemplo para probar el sistema."""
    try:
        # Definir recetas de ejemplo
        recipes = {
            "pizza": {
                "harina": 1000,
                "agua": 620,
                "sal": 20,
                "levadura": 5,
                "aceite_oliva": 30,
                "recipe_type": "pizza",
                "production_scale": "individual",
                "tipo_napolitana": True
            },
            "pan": {
                "harina": 1000,
                "agua": 700,
                "sal": 20,
                "levadura": 10,
                "recipe_type": "pan",
                "production_scale": "individual"
            },
            "brioche": {
                "harina": 1000,
                "huevo": 200,
                "mantequilla": 200,
                "azucar": 100,
                "leche": 300,
                "sal": 18,
                "levadura": 20,
                "recipe_type": "brioche",
                "production_scale": "individual"
            }
        }
        
        # Seleccionar tipo de receta
        recipe_type = args.recipe_type.lower() if args.recipe_type else "pizza"
        if recipe_type not in recipes:
            logger.warning(f"Tipo de receta {recipe_type} no reconocido, usando pizza")
            recipe_type = "pizza"
        
        # Seleccionar receta
        recipe = recipes[recipe_type]
        
        # Actualizar escala si se especificó
        if args.production_scale:
            recipe["production_scale"] = args.production_scale
        
        # Definir archivo de salida
        if args.output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output_file = os.path.join(data_dir, f"sample_{recipe_type}_{timestamp}.json")
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
        
        # Guardar receta
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Receta de ejemplo {recipe_type} creada en {args.output_file}")
        print(f"Receta de ejemplo {recipe_type} creada en {args.output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error al crear receta de ejemplo: {str(e)}")
        return 1

def main():
    """Función principal del script."""
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description="Sistema de validación de recetas para masas",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")
    
    # Subcomando para validar receta
    validate_parser = subparsers.add_parser("validate", help="Validar una receta")
    validate_parser.add_argument("recipe_file", help="Archivo JSON con la receta a validar")
    validate_parser.add_argument("--recipe-type", help="Tipo de receta (pizza, pan, etc.)")
    validate_parser.add_argument("--production-scale", help="Escala de producción (individual, small_business, industrial)")
    validate_parser.add_argument("--output-file", help="Archivo para guardar resultados detallados")
    
    # Subcomando para verificar integridad
    check_parser = subparsers.add_parser("check", help="Verificar integridad del sistema")
    
    # Subcomando para crear receta de ejemplo
    sample_parser = subparsers.add_parser("sample", help="Crear receta de ejemplo")
    sample_parser.add_argument("--recipe-type", help="Tipo de receta (pizza, pan, brioche)")
    sample_parser.add_argument("--production-scale", help="Escala de producción (individual, small_business, industrial)")
    sample_parser.add_argument("--output-file", help="Archivo para guardar la receta")
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Ejecutar comando
    if args.command == "validate":
        return validate_recipe(args)
    elif args.command == "check":
        return check_integrity(args)
    elif args.command == "sample":
        return create_sample_recipe(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    # Añadir manejo de señales para CTRL+C
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Operación cancelada por el usuario")
        sys.exit(130) 