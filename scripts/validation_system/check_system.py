#!/usr/bin/env python
"""
Script para verificar la integridad del Sistema de Validación PizzaAI
---------------------------------------------------------------------
Comprueba que todos los componentes están presentes y funcionando correctamente.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system_check.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SystemCheck")

# Definición de los archivos requeridos
REQUIRED_FILES = [
    {"name": "validation_system.py", "type": "code"},
    {"name": "validation_rules.json", "type": "config"},
    {"name": "ingredient_limits.json", "type": "config"},
    {"name": "process_parameters.json", "type": "config"},
    {"name": "example_recipe.json", "type": "example"}
]

def check_system_integrity():
    """
    Verifica la integridad del sistema de validación.
    
    Returns:
        Dict: Resultado de la verificación
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    integrity_result = {
        "timestamp": datetime.now().isoformat(),
        "status": "OK",
        "components": {},
        "issues": []
    }
    
    # Verificar archivos
    for file_info in REQUIRED_FILES:
        file_name = file_info["name"]
        file_path = os.path.join(current_dir, file_name)
        file_exists = os.path.exists(file_path)
        
        integrity_result["components"][file_name] = {
            "exists": file_exists,
            "type": file_info["type"],
            "path": file_path
        }
        
        if not file_exists:
            integrity_result["status"] = "ERROR"
            integrity_result["issues"].append(f"Archivo faltante: {file_name}")
            logger.error(f"Archivo faltante: {file_name} en {file_path}")
        elif file_info["type"] == "config":
            # Verificar validez del JSON
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json.load(f)
                integrity_result["components"][file_name]["valid_json"] = True
            except json.JSONDecodeError as e:
                integrity_result["status"] = "ERROR"
                integrity_result["components"][file_name]["valid_json"] = False
                error_msg = f"JSON inválido en: {file_name} - {str(e)}"
                integrity_result["issues"].append(error_msg)
                logger.error(error_msg)
    
    # Verificar que los módulos necesarios estén disponibles
    try:
        import importlib.util
        
        # Verificar módulo validation_system
        vs_path = os.path.join(current_dir, "validation_system.py")
        if os.path.exists(vs_path):
            try:
                spec = importlib.util.spec_from_file_location("validation_system", vs_path)
                validation_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(validation_module)
                
                # Verificar clases clave
                has_validator = hasattr(validation_module, "RecipeValidator")
                has_error = hasattr(validation_module, "ValidationError")
                
                integrity_result["components"]["validation_system_module"] = {
                    "status": "OK" if has_validator and has_error else "ERROR",
                    "has_validator_class": has_validator,
                    "has_error_class": has_error
                }
                
                if not has_validator or not has_error:
                    integrity_result["status"] = "ERROR"
                    if not has_validator:
                        integrity_result["issues"].append("Clase RecipeValidator no encontrada")
                    if not has_error:
                        integrity_result["issues"].append("Clase ValidationError no encontrada")
                
                # Intentar inicializar el validador
                try:
                    validator = validation_module.RecipeValidator()
                    integrity_result["components"]["validator_init"] = {"status": "OK"}
                except Exception as e:
                    integrity_result["status"] = "ERROR"
                    integrity_result["components"]["validator_init"] = {"status": "ERROR", "error": str(e)}
                    integrity_result["issues"].append(f"Error al inicializar validador: {str(e)}")
                    logger.error(f"Error al inicializar validador: {str(e)}")
            except Exception as e:
                integrity_result["status"] = "ERROR"
                integrity_result["components"]["validation_system_module"] = {"status": "ERROR", "error": str(e)}
                integrity_result["issues"].append(f"Error al cargar módulo validation_system: {str(e)}")
                logger.error(f"Error al cargar módulo validation_system: {str(e)}")
    except ImportError as e:
        integrity_result["status"] = "ERROR"
        integrity_result["issues"].append(f"Error de importación: {str(e)}")
        logger.error(f"Error de importación: {str(e)}")
    
    # Verificar ejemplo de receta
    try:
        recipe_path = os.path.join(current_dir, "example_recipe.json")
        if os.path.exists(recipe_path):
            with open(recipe_path, "r", encoding="utf-8") as f:
                recipe_data = json.load(f)
            
            required_fields = ["id", "name", "type", "ingredients"]
            missing_fields = [field for field in required_fields if field not in recipe_data]
            
            integrity_result["components"]["example_recipe"] = {
                "status": "OK" if not missing_fields else "ERROR",
                "missing_fields": missing_fields
            }
            
            if missing_fields:
                integrity_result["status"] = "ERROR"
                integrity_result["issues"].append(f"Campos faltantes en receta de ejemplo: {', '.join(missing_fields)}")
                logger.error(f"Campos faltantes en receta de ejemplo: {', '.join(missing_fields)}")
    except Exception as e:
        integrity_result["status"] = "ERROR"
        if "example_recipe" not in integrity_result["components"]:
            integrity_result["components"]["example_recipe"] = {}
        integrity_result["components"]["example_recipe"]["status"] = "ERROR"
        integrity_result["components"]["example_recipe"]["error"] = str(e)
        integrity_result["issues"].append(f"Error al verificar receta de ejemplo: {str(e)}")
        logger.error(f"Error al verificar receta de ejemplo: {str(e)}")
    
    return integrity_result

def save_check_result(result, output_file=None):
    """
    Guarda el resultado de la verificación en un archivo JSON.
    
    Args:
        result: Resultado de la verificación
        output_file: Ruta al archivo de salida (opcional)
    """
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Resultado guardado en: {output_file}")
        except Exception as e:
            logger.error(f"Error al guardar resultado: {str(e)}")
            print(f"Error al guardar resultado: {str(e)}")
    
    # Imprimir resumen
    print("\nVerificación de Integridad del Sistema:")
    print(f"  Estado: {result['status']}")
    
    if result['issues']:
        print("\nProblemas detectados:")
        for issue in result['issues']:
            print(f"  - {issue}")
    else:
        print("\nNo se detectaron problemas. El sistema está listo para su uso.")

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verificador de Integridad del Sistema de Validación PizzaAI")
    parser.add_argument("--output", help="Archivo para guardar resultado de verificación")
    
    args = parser.parse_args()
    
    try:
        logger.info("Iniciando verificación de integridad del sistema")
        result = check_system_integrity()
        logger.info(f"Verificación completada: {result['status']}")
        
        save_check_result(result, args.output)
        
        # Establecer código de salida
        if result["status"] == "ERROR":
            sys.exit(1)
        else:
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"Error durante la verificación: {str(e)}")
        print(f"Error durante la verificación: {str(e)}")
        sys.exit(2)

if __name__ == "__main__":
    main() 