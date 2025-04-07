#!/usr/bin/env python
"""
Demo del Optimizador Avanzado de Recetas para PizzaAI

Este script demuestra el uso del optimizador avanzado de recetas para crear
formulaciones especiales a partir de descripciones en lenguaje natural.
"""

import json
import argparse
from typing import Dict, List, Optional, Tuple

from src.core.services.usda_service import USDAService
from src.features.nutrition.nutrition_analyzer import NutritionAnalyzer
from src.core.services.recommendation_service import RecommendationService
from src.features.nutrition.recipe_optimizer_advanced import AdvancedRecipeOptimizer


def print_recipe(recipe: Dict[str, float], title: str = "Receta"):
    """Imprime una receta de forma legible."""
    print(f"\n=== {title} ===")
    
    # Agrupar ingredientes por categoría
    categories = {
        "Harinas y almidones": [],
        "Vegetales": [],
        "Aglutinantes y aditivos": [],
        "Líquidos": [],
        "Grasas y aceites": [],
        "Otros": []
    }
    
    # Clasificar ingredientes
    for ingredient, amount in recipe.items():
        if any(flour_type in ingredient.lower() for flour_type in ["flour", "starch", "meal"]):
            categories["Harinas y almidones"].append((ingredient, amount))
        elif any(veggie in ingredient.lower() for veggie in ["beetroot", "carrot", "spinach", "cauliflower", "pumpkin", "tomato", "pepper", "cabbage"]):
            categories["Vegetales"].append((ingredient, amount))
        elif any(binder in ingredient.lower() for binder in ["gum", "psyllium", "gluten", "egg"]):
            categories["Aglutinantes y aditivos"].append((ingredient, amount))
        elif any(liquid in ingredient.lower() for liquid in ["water", "milk", "juice"]):
            categories["Líquidos"].append((ingredient, amount))
        elif any(fat in ingredient.lower() for fat in ["oil", "butter", "margarine", "shortening"]):
            categories["Grasas y aceites"].append((ingredient, amount))
        else:
            categories["Otros"].append((ingredient, amount))
    
    # Imprimir ingredientes por categoría
    for category, ingredients in categories.items():
        if ingredients:
            print(f"\n{category}:")
            for ingredient, amount in sorted(ingredients, key=lambda x: -x[1]):
                print(f"  {ingredient}: {amount:.1f}g")
    
    # Imprimir peso total
    total_weight = sum(recipe.values())
    print(f"\nPeso total: {total_weight:.1f}g")
    print("="*30)


def print_recommendations(recommendations: List[Dict], title: str = "Recomendaciones"):
    """Imprime recomendaciones para la receta."""
    if not recommendations:
        return
        
    print(f"\n=== {title} ===")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"{i}. {rec['name'].capitalize()} (puntuación: {rec['score']:.1f})")
        if "substitution_ratio" in rec:
            print(f"   Ratio de sustitución: {rec['substitution_ratio'].get('flour', 0):.1f}:1")
        if "usage_tips" in rec and rec["usage_tips"]:
            print("   Consejos:")
            for tip in rec['usage_tips'][:2]:
                print(f"   - {tip}")
        print()
    print("="*30)


def demo_red_gluten_free_pizza():
    """Demostración de una pizza sin gluten de color rojo."""
    print("\n\n*** DEMO: PIZZA SIN GLUTEN DE COLOR ROJO (REMOLACHA) ***")
    print("Creando una masa de pizza de 250g sin gluten, de color rojo,")
    print("con textura similar a la masa tradicional de trigo.")
    
    # Inicializar servicios
    usda_service = USDAService()
    nutrition_analyzer = NutritionAnalyzer(usda_service)
    recommendation_service = RecommendationService(usda_service)
    optimizer = AdvancedRecipeOptimizer(nutrition_analyzer, recommendation_service)
    
    # Método 1: Usando descripción en lenguaje natural
    description = "250 gramos de masa de pizza libres de gluten, de color rojo asociado a las vitaminas de la remolacha, con una textura lo más cercana a la masa de pizza tradicional de trigo"
    
    print("\nMétodo 1: Usando descripción en lenguaje natural")
    print("-"*50)
    print(f"Descripción: '{description}'")
    
    recipe, recommendations = optimizer.create_recipe_from_description(
        description=description,
        recipe_type="pizza",
        base_weight=250.0
    )
    
    print_recipe(recipe, "Receta generada automáticamente")
    print_recommendations(recommendations)
    
    # Método 2: Usando parámetros específicos
    print("\nMétodo 2: Usando parámetros específicos")
    print("-"*50)
    
    # Receta base sin gluten
    base_recipe = {
        "rice flour": 100.0,     # Harina de arroz (sin gluten)
        "tapioca starch": 25.0,  # Almidón de tapioca (sin gluten)
        "potato starch": 25.0,   # Almidón de patata (sin gluten)
        "psyllium husk": 10.0,   # Cáscara de psyllium (mejora elasticidad)
        "xanthan gum": 3.0,      # Goma xantana (mejora estructura)
        "olive oil": 15.0,       # Aceite de oliva
        "salt": 3.0,             # Sal
        "yeast": 2.0             # Levadura
    }
    
    # Optimizar la receta con parámetros específicos
    recipe_adv, recommendations_adv = optimizer.optimize_recipe_advanced(
        base_recipe=base_recipe,
        target_weight=250.0,
        desired_color="red",
        desired_texture="elastic",
        dietary_restrictions=["gluten_free"],
        recipe_type="pizza"
    )
    
    print_recipe(recipe_adv, "Receta optimizada con parámetros específicos")
    print_recommendations(recommendations_adv)


def demo_halloween_pumpkin_bread():
    """Demostración de un pan de calabaza para Halloween."""
    print("\n\n*** DEMO: PAN AMARILLO DE CALABAZA PARA HALLOWEEN ***")
    print("Creando un pan de calabaza de color amarillo intenso para Halloween.")
    
    # Inicializar servicios
    usda_service = USDAService()
    nutrition_analyzer = NutritionAnalyzer(usda_service)
    recommendation_service = RecommendationService(usda_service)
    optimizer = AdvancedRecipeOptimizer(nutrition_analyzer, recommendation_service)
    
    # Descripción en lenguaje natural
    description = "pan amarillo de calabaza para Halloween, con textura esponjosa"
    
    recipe, recommendations = optimizer.create_recipe_from_description(
        description=description,
        recipe_type="bread",
        base_weight=400.0
    )
    
    print_recipe(recipe, "Pan de Calabaza para Halloween")
    print_recommendations(recommendations)


def create_custom_recipe():
    """Crea una receta personalizada basada en la entrada del usuario."""
    print("\n\n*** CREACIÓN DE RECETA PERSONALIZADA ***")
    
    # Inicializar servicios
    usda_service = USDAService()
    nutrition_analyzer = NutritionAnalyzer(usda_service)
    recommendation_service = RecommendationService(usda_service)
    optimizer = AdvancedRecipeOptimizer(nutrition_analyzer, recommendation_service)
    
    # Solicitar descripción al usuario
    print("Describe la receta que deseas crear (por ejemplo: 'masa de pizza verde sin gluten'):")
    description = input("> ")
    
    # Solicitar tipo de receta
    print("\n¿Qué tipo de receta quieres crear?")
    print("1. Pizza")
    print("2. Pan")
    print("3. Otro")
    recipe_type_choice = input("Selecciona una opción (1-3): ")
    
    recipe_type = "pizza"  # Valor por defecto
    if recipe_type_choice == "2":
        recipe_type = "bread"
    elif recipe_type_choice == "3":
        recipe_type = "other"
    
    # Solicitar peso objetivo
    print("\n¿Cuál es el peso objetivo en gramos?")
    weight_input = input("Peso (por defecto 250g): ")
    
    try:
        target_weight = float(weight_input) if weight_input else 250.0
    except ValueError:
        print("Valor inválido, usando 250g como valor por defecto.")
        target_weight = 250.0
    
    # Crear la receta
    print(f"\nCreando receta: '{description}' ({recipe_type}, {target_weight}g)")
    recipe, recommendations = optimizer.create_recipe_from_description(
        description=description,
        recipe_type=recipe_type,
        base_weight=target_weight
    )
    
    print_recipe(recipe, "Tu receta personalizada")
    print_recommendations(recommendations)


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Demo del Optimizador Avanzado de Recetas para PizzaAI"
    )
    parser.add_argument(
        "--demo", choices=["pizza", "halloween", "custom"], default="pizza",
        help="Tipo de demostración a ejecutar"
    )
    args = parser.parse_args()
    
    print("=== DEMOSTRACIÓN DEL OPTIMIZADOR AVANZADO DE RECETAS PIZZAAI ===")
    print("Este script demuestra el uso del optimizador avanzado de recetas para")
    print("crear formulaciones especiales a partir de descripciones en lenguaje natural.")
    
    if args.demo == "pizza":
        demo_red_gluten_free_pizza()
    elif args.demo == "halloween":
        demo_halloween_pumpkin_bread()
    elif args.demo == "custom":
        create_custom_recipe()
    else:
        demo_red_gluten_free_pizza()
        demo_halloween_pumpkin_bread()


if __name__ == "__main__":
    main() 