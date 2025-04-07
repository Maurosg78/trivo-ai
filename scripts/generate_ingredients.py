import pandas as pd
import requests


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


# Tu clave de API (reemplaza "TU_API_KEY" con tu clave real)
api_key = "Rntzc9HDaefGgZL0w3Sid120qfk4kdJD4YZuicE4"

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
    get_nutritional_data(ing, api_key) for ing in ingredients if get_nutritional_data(ing, api_key)
]
df = pd.DataFrame(data)
df.to_csv("data/ingredients_data.csv", index=False)
print("Archivo 'ingredients_data.csv' generado con éxito.")
