import csv
import os

import requests

# Obtener la API key de variables de entorno
API_KEY = os.environ.get("USDA_API_KEY", "")
if not API_KEY:
    print("Advertencia: No se ha configurado USDA_API_KEY en las variables de entorno")
    
BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


def get_nutritional_data(ingredient):
    """Obtiene datos nutricionales de un ingrediente usando la API de USDA."""
    params = {"query": ingredient, "api_key": API_KEY, "pageSize": 1}
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Lanza una excepción si la solicitud falla
        data = response.json()
        print(f"Respuesta de la API para {ingredient}: {data}")  # Depuración
        if "foods" in data and data["foods"]:  # Verifica que haya datos
            food = data["foods"][0]
            nutrients = {n["nutrientName"]: n["value"] for n in food["foodNutrients"]}
            return {
                "ingredient": ingredient,
                "calories": nutrients.get("Energy", 0),
                "protein": nutrients.get("Protein", 0),
                "carbs": nutrients.get("Carbohydrate, by difference", 0),
                "fat": nutrients.get("Total lipid (fat)", 0),
            }
        else:
            print(f"No se encontraron datos para {ingredient}")
            return None
    except requests.RequestException as e:
        print(f"Error al consultar {ingredient}: {e}")
        return None


def save_to_csv(data, filename):
    """Guarda los datos en un archivo CSV en la ruta especificada."""
    filepath = filename
    # Crear el directorio si no existe
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fieldnames = ["ingredient", "calories", "protein", "carbs", "fat"]
    with open(filepath, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Datos guardados en {filepath}")


if __name__ == "__main__":
    ingredients = ["cauliflower", "chickpea", "rice flour"]
    # Recolecta datos y filtra valores None
    data = [
        get_nutritional_data(ing) for ing in ingredients if get_nutritional_data(ing) is not None
    ]
    if data:
        save_to_csv(data, "./data/processed/nutritional_data.csv")
    else:
        print("No se encontraron datos para ningún ingrediente.")
