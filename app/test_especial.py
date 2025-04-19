from app import mock_language_processing
import json
import os

def generar_receta_especial():
    """Genera una receta especial de pizza para Halloween"""
    texto = "pizza tamaño familiar, color naranja para repartir en halloween, sin gluten y lo más parecida una pizza de trigo natural"
    
    print(f"Generando receta con el texto: '{texto}'")
    recipe = mock_language_processing(texto)
    recipe_id = recipe['id']
    
    # Imprimir información básica
    print(f"\n--- RECETA PARA HALLOWEEN GENERADA ---")
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
    generar_receta_especial() 