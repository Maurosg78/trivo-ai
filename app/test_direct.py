from app import mock_language_processing
import json
import os

def generar_receta(texto):
    """Genera una receta usando la función mock"""
    recipe = mock_language_processing(texto)
    recipe_id = recipe['id']
    
    # Imprimir información básica
    print(f"--- RECETA GENERADA ---")
    print(f"ID: {recipe_id}")
    print(f"Nombre: {recipe['nombre']}")
    print(f"Descripción: {recipe['descripcion']}")
    print("\nINGREDIENTES:")
    for ing in recipe['ingredientes']:
        print(f"- {ing['name']}: {ing['amount']} {ing['unit']}")
    
    print("\nMÉTODO DE PREPARACIÓN:")
    for i, paso in enumerate(recipe['metodo']):
        print(f"{i+1}. {paso}")
    
    print(f"\nNivel de dificultad: {recipe['dificultad']}")
    print(f"Tiempo de preparación: {recipe['tiempo_preparacion']} min")
    print(f"Tiempo de cocción: {recipe['tiempo_coccion']} min")
    print(f"Porciones: {recipe['porciones']}")
    
    # Leer el archivo JSON completo para mostrar datos adicionales
    json_path = f"app/static/data/recipe_{recipe_id}.json"
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            print("\nEXPLICACIONES:")
            for exp in data['explanations']:
                print(f"- {exp}")
                
            print(f"\nCONSEJO PROFESIONAL:")
            print(data['key_tip'])
        else:
            print(f"\nArchivo guardado en: {json_path} (pero no se pudo leer)")
    except Exception as e:
        print(f"Error al leer el archivo JSON: {e}")
    
    return recipe_id

if __name__ == "__main__":
    # Generar algunas recetas de prueba
    print("\n==== PRUEBA 1: Pizza Napolitana ====")
    generar_receta("quiero una pizza napolitana clásica con la masa fina")
    
    print("\n==== PRUEBA 2: Pizza Vegetariana ====")
    generar_receta("pizza vegetariana con muchos vegetales")
    
    print("\n==== PRUEBA 3: Pizza Hawaiana ====")
    generar_receta("pizza hawaiana con piña y jamón") 