import pandas as pd
import requests
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar configuración
from config import USDA_API_KEY, DATA_DIR

# Función para obtener datos de la API
def get_nutritional_data(ingredient, api_key):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={ingredient}&api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["foods"]:
            food = data["foods"][0]
            nutrients = {n["nutrientName"]: n["value"] for n in food["foodNutrients"]}
            return {
                "ingredient": ingredient,
                "calories": nutrients.get("Energy", 0),
                "protein": nutrients.get("Protein", 0),
                "carbs": nutrients.get("Carbohydrate, by difference", 0),
                "fat": nutrients.get("Total lipid (fat)", 0),
                "fiber": nutrients.get("Fiber, total dietary", 0),
            }
    return None


# Usar la clave API de la configuración
if not USDA_API_KEY:
    print("Error: La clave API de USDA no está configurada. Por favor defina la variable de entorno USDA_API_KEY.")
    sys.exit(1)

# Lista de ingredientes
ingredients = [
    "cauliflower",
    "chickpea flour",
    "rice flour",
    "potato flour",
    "corn starch",
    "olive oil",
    "salt",
    "water",
    "xanthan gum",
    "sugar",
    "almond flour",
    "coconut flour",
    "oat flour (gluten-free)",
    "quinoa flour",
    "buckwheat flour",
    "lentil flour",
    "corn flour",
    "potato starch",
    "tapioca starch",
    "psyllium husk",
    "flaxseed meal",
]

# Obtener datos y guardarlos
data = [
    get_nutritional_data(ing, USDA_API_KEY) for ing in ingredients if get_nutritional_data(ing, USDA_API_KEY)
]
df = pd.DataFrame(data)

# Asegurar que el directorio data existe
os.makedirs(DATA_DIR, exist_ok=True)

# Guardar archivo en el directorio de datos
output_file = DATA_DIR / "ingredients_data.csv"
df.to_csv(output_file, index=False)
print(f"Archivo '{output_file}' generado con éxito.")
