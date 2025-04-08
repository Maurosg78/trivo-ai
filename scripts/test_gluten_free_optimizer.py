#!/usr/bin/env python3
"""
Script para probar el optimizador genético para recetas sin gluten.

Este script permite probar diferentes configuraciones y propiedades
para recetas sin gluten y ver los resultados.
"""

import sys
import json
from pathlib import Path

# Añadir el directorio raíz al path para poder importar módulos del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from src.features.optimizer.gluten_free_optimizer import GlutenFreeOptimizer
except ImportError as e:
    print(f"Error: No se pudo importar el optimizador: {e}")
    sys.exit(1)

def print_recipe(recipe):
    """Imprime una receta formateada."""
    print("\n===== RECETA OPTIMIZADA =====")
    
    # Ingredientes
    print("\nINGREDIENTES:")
    for ingredient, amount in recipe["ingredients"].items():
        # Mejora presentación del nombre del ingrediente
        name = ingredient.replace("_", " ").title()
        print(f"  - {name}: {amount}g")
    
    # Propiedades
    if "properties" in recipe:
        print("\nPROPIEDADES:")
        for prop, value in recipe["properties"].items():
            print(f"  - {prop.title()}: {value:.2f}")
    
    # Recomendaciones
    if "recommendations" in recipe:
        print("\nRECOMENDACIONES:")
        for i, recommendation in enumerate(recipe["recommendations"]):
            print(f"  {i+1}. {recommendation}")
    
    # Instrucciones
    if "instructions" in recipe:
        print("\nINSTRUCCIONES:")
        for i, instruction in enumerate(recipe["instructions"]):
            print(f"  {i+1}. {instruction}")

def test_optimizer(product_type, desired_properties=None, cost_weight=0.3):
    """Prueba el optimizador con diferentes configuraciones."""
    try:
        optimizer = GlutenFreeOptimizer()
        recipe = optimizer.optimize(product_type, desired_properties, cost_weight)
        print_recipe(recipe)
        
        # Guardar la receta en un archivo JSON para referencia
        output_file = f"recipe_{product_type}_{'_'.join(desired_properties.keys() if desired_properties else ['default'])}.json"
        with open(output_file, 'w') as f:
            json.dump(recipe, f, indent=2)
        print(f"\nReceta guardada en: {output_file}")
        
        return recipe
    except Exception as e:
        print(f"Error durante la optimización: {e}")
        return None

def main():
    """Función principal del script."""
    print("TRIVO-AI - Prueba de Optimizador de Recetas Sin Gluten")
    print("====================================================")
    
    # Predefinir algunos casos de prueba
    test_cases = [
        {
            "name": "Pizza Elástica",
            "product_type": "pizza",
            "properties": {"elasticidad": True}
        },
        {
            "name": "Pan Suave",
            "product_type": "pan",
            "properties": {"suave": True}
        },
        {
            "name": "Galletas Crujientes",
            "product_type": "galletas",
            "properties": {"crujiente": True}
        },
        {
            "name": "Pizza Ligera y Económica",
            "product_type": "pizza",
            "properties": {"ligera": True},
            "cost_weight": 0.7
        }
    ]
    
    # Mostrar menú de opciones
    print("\nSelecciona una opción para probar:")
    for i, case in enumerate(test_cases):
        print(f"{i+1}. {case['name']}")
    print("5. Personalizado")
    print("0. Salir")
    
    try:
        choice = int(input("\nOpción: "))
        
        if choice == 0:
            print("Saliendo...")
            return
        
        if choice == 5:
            # Opción personalizada
            product_type = input("Tipo de producto (pizza, pan, galletas, pasta, tortitas): ")
            
            properties = {}
            print("\nPropiedades deseadas (deja en blanco para omitir):")
            for prop in ["elasticidad", "crujiente", "suave", "ligera"]:
                response = input(f"¿Deseas que sea {prop}? (s/n): ")
                if response.lower() == 's':
                    properties[prop] = True
            
            cost_weight = float(input("\nImportancia del costo (0-1, donde 0 es ignorar el costo): "))
            
            test_optimizer(product_type, properties, cost_weight)
        
        elif 1 <= choice <= len(test_cases):
            # Caso predefinido
            case = test_cases[choice-1]
            print(f"\nProbando: {case['name']}")
            test_optimizer(
                case["product_type"],
                case.get("properties"),
                case.get("cost_weight", 0.3)
            )
        
        else:
            print("Opción no válida")
    
    except ValueError:
        print("Por favor, ingresa un número válido")
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")

if __name__ == "__main__":
    main() 