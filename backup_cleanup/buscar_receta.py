#!/usr/bin/env python
"""
Script para buscar recetas de cheesecake de frambuesa usando la API de Spoonacular.
"""

from src.features.external_api import spoonacular

def main():
    print("Buscando cheesecake de frambuesa...")
    
    # Buscar recetas
    recipes = spoonacular.search_recipes('raspberry cheesecake', number=1)
    
    if not recipes:
        print("No se encontraron recetas de cheesecake de frambuesa.")
        return
    
    # Obtener detalles de la receta
    recipe = recipes[0]
    recipe_id = recipe.get('id')
    
    print(f"Encontrada receta con ID: {recipe_id}")
    
    # Obtener receta completa
    full_recipe = spoonacular.get_recipe_by_id(recipe_id)
    
    # Convertir a formato TRIVO-AI
    trivo_recipe = spoonacular.convert_spoonacular_to_trivo(full_recipe)
    
    # Mostrar información
    print("\nNOMBRE DE LA RECETA:")
    print(trivo_recipe.get('name'))
    
    print("\nINGREDIENTES:")
    for ing, amount in trivo_recipe.get('ingredients', {}).items():
        print(f"- {ing.replace('_', ' ')}: {amount:.1f}g")
    
    print("\nINSTRUCCIONES:")
    for i, instr in enumerate(trivo_recipe.get('instructions', []), 1):
        print(f"{i}. {instr}")
    
    # Información adicional
    print("\nPROPIEDADES:")
    for prop, value in trivo_recipe.get('properties', {}).items():
        if prop in ['original_id', 'original_url']:
            continue
        print(f"- {prop}: {value}")
    
    print("\nFUENTE ORIGINAL:")
    print(trivo_recipe.get('properties', {}).get('original_url', 'No disponible'))

if __name__ == "__main__":
    main() 