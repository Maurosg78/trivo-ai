#!/usr/bin/env python
"""
Demo del Optimizador de Recetas para PizzaAI

Este script demuestra el uso del optimizador de recetas para crear formulaciones
de masas basadas en vegetales con perfiles nutricionales optimizados.
"""

import json
from src.core.services.usda_service import USDAService
from src.features.nutrition.nutrition_analyzer import NutritionAnalyzer, NutritionalProfile
from src.core.services.recommendation_service import RecommendationService
from src.features.nutrition.recipe_optimizer import RecipeOptimizer


def print_nutritional_profile(profile: NutritionalProfile):
    """Imprime un perfil nutricional de forma legible."""
    print("=== Perfil Nutricional ===")
    print(f"Proteínas: {profile.macronutrients.get('protein', 0):.1f}g")
    print(f"Grasas: {profile.macronutrients.get('fat', 0):.1f}g")
    print(f"Carbohidratos: {profile.macronutrients.get('carbohydrates', 0):.1f}g")
    print(f"Fibra: {profile.fiber:.1f}g")
    print(f"Calorías: {profile.calories:.1f}kcal")
    print(f"Índice glucémico: {profile.glycemic_index:.1f}")
    print("========================")


def print_recipe(ingredients: dict):
    """Imprime una receta de forma legible."""
    print("\n=== Receta ===")
    for ingredient, amount in ingredients.items():
        print(f"{ingredient}: {amount:.1f}g")
    print("==============")


def print_recommendations(recommendations: list):
    """Imprime recomendaciones de vegetales."""
    print("\n=== Recomendaciones de Vegetales ===")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"{i}. {rec['name'].capitalize()} (puntuación: {rec['score']:.1f})")
        print(f"   Ratio de sustitución: {rec['substitution_ratio'].get('flour', 0):.1f}:1")
        print("   Consejos:")
        for tip in rec['usage_tips'][:2]:
            print(f"   - {tip}")
        print()
    print("===================================")


def demo_cauliflower_pizza():
    """Demostración de optimización para pizza de coliflor."""
    print("\n\n*** DEMO: PIZZA DE COLIFLOR ***")
    
    # Inicialización de servicios
    usda_service = USDAService()
    nutrition_analyzer = NutritionAnalyzer(usda_service)
    recommendation_service = RecommendationService(usda_service)
    recipe_optimizer = RecipeOptimizer(nutrition_analyzer, recommendation_service)
    
    # Receta inicial de pizza de coliflor
    initial_recipe = {
        "cauliflower": 200.0,  # 200g de coliflor
        "rice flour": 100.0,   # 100g de harina de arroz
        "egg": 50.0,           # 50g de huevo
        "olive oil": 15.0,     # 15g de aceite de oliva
        "salt": 5.0            # 5g de sal
    }
    
    print("Receta inicial:")
    print_recipe(initial_recipe)
    
    # Analizar perfil nutricional inicial
    initial_profile = nutrition_analyzer.analyze_nutritional_profile(initial_recipe)
    print("\nPerfil nutricional inicial:")
    print_nutritional_profile(initial_profile)
    
    # Definir perfil objetivo personalizado
    target_profile = NutritionalProfile(
        macronutrients={"protein": 15.0, "fat": 7.0, "carbohydrates": 25.0},
        micronutrients={},
        fiber=10.0,
        calories=230.0,
        glycemic_index=45.0
    )
    
    # Optimizar receta
    optimized_recipe, recommendations = recipe_optimizer.optimize_recipe(
        initial_recipe, 
        target_profile=target_profile,
        recipe_type="pizza",
        constraints={"low_carb": True}
    )
    
    print("\nReceta optimizada:")
    print_recipe(optimized_recipe)
    
    # Analizar perfil nutricional optimizado
    optimized_profile = nutrition_analyzer.analyze_nutritional_profile(optimized_recipe)
    print("\nPerfil nutricional optimizado:")
    print_nutritional_profile(optimized_profile)
    
    # Mostrar recomendaciones
    print_recommendations(recommendations)
    
    # Visualización del perfil nutricional
    visualization_data = recipe_optimizer.visualize_nutritional_profile(
        optimized_recipe, target_profile=target_profile
    )
    
    print("\nDatos para visualización:")
    print(json.dumps(visualization_data, indent=2))


def demo_veggie_bread():
    """Demostración de optimización para pan con vegetales."""
    print("\n\n*** DEMO: PAN CON VEGETALES ***")
    
    # Inicialización de servicios
    usda_service = USDAService()
    nutrition_analyzer = NutritionAnalyzer(usda_service)
    recommendation_service = RecommendationService(usda_service)
    recipe_optimizer = RecipeOptimizer(nutrition_analyzer, recommendation_service)
    
    # Receta inicial de pan con vegetales
    initial_recipe = {
        "chickpea": 150.0,     # 150g de harina de garbanzo
        "carrot": 100.0,       # 100g de zanahoria
        "rice flour": 80.0,    # 80g de harina de arroz
        "zucchini": 50.0,      # 50g de calabacín
        "olive oil": 20.0,     # 20g de aceite de oliva
        "salt": 5.0            # 5g de sal
    }
    
    print("Receta inicial:")
    print_recipe(initial_recipe)
    
    # Analizar perfil nutricional inicial
    initial_profile = nutrition_analyzer.analyze_nutritional_profile(initial_recipe)
    print("\nPerfil nutricional inicial:")
    print_nutritional_profile(initial_profile)
    
    # Optimizar receta
    optimized_recipe, recommendations = recipe_optimizer.optimize_recipe(
        initial_recipe, 
        recipe_type="bread",
        constraints={"texture_preference": "elastic"}
    )
    
    print("\nReceta optimizada:")
    print_recipe(optimized_recipe)
    
    # Analizar perfil nutricional optimizado
    optimized_profile = nutrition_analyzer.analyze_nutritional_profile(optimized_recipe)
    print("\nPerfil nutricional optimizado:")
    print_nutritional_profile(optimized_profile)
    
    # Mostrar recomendaciones
    print_recommendations(recommendations)


if __name__ == "__main__":
    print("=== DEMOSTRACIÓN DEL OPTIMIZADOR DE RECETAS PIZZAAI ===")
    print("Este script demuestra el uso del optimizador de recetas para")
    print("crear formulaciones de masas basadas en vegetales.")
    
    demo_cauliflower_pizza()
    demo_veggie_bread() 