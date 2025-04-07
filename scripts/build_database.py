import time

import pandas as pd
import requests

# Clave de la API de la USDA
API_KEY = "Rntzc9HDaefGgZL0w3Sid120qfk4kdJD4YZuicE4"

# Lista de 100 ingredientes para masas vegetales
INGREDIENTS = [
    "chickpea flour",
    "white rice flour",
    "brown rice flour",
    "tapioca starch",
    "potato starch",
    "corn starch",
    "xanthan gum",
    "guar gum",
    "water",
    "olive oil",
    "coconut oil",
    "sunflower oil",
    "sea salt",
    "cane sugar",
    "coconut sugar",
    "honey",
    "maple syrup",
    "apple cider vinegar",
    "dry yeast",
    "baking powder",
    "baking soda",
    "chia seeds",
    "flaxseed meal",
    "psyllium husk",
    "almond flour",
    "coconut flour",
    "quinoa flour",
    "buckwheat flour",
    "sorghum flour",
    "teff flour",
    "millet flour",
    "arrowroot starch",
    "sweet potato starch",
    "cassava starch",
    "agar agar",
    "pectin",
    "lemon juice",
    "orange juice",
    "carrot juice",
    "beet juice",
    "spinach juice",
    "tomato juice",
    "turmeric powder",
    "cinnamon",
    "ginger powder",
    "paprika",
    "cumin",
    "coriander",
    "oregano",
    "thyme",
    "basil",
    "rosemary",
    "garlic powder",
    "onion powder",
    "black pepper",
    "vanilla extract",
    "cocoa powder",
    "carob powder",
    "nutritional yeast",
    "pumpkin puree",
    "sweet potato puree",
    "zucchini puree",
    "carrot puree",
    "spinach puree",
    "beet puree",
    "tomato puree",
    "cauliflower puree",
    "broccoli puree",
    "kale puree",
    "pea flour",
    "lentil flour",
    "fava bean flour",
    "amaranth flour",
    "flaxseed flour",
    "sunflower seed flour",
    "pumpkin seed flour",
    "sesame seed flour",
    "hemp seed flour",
    "oat bran",
    "rice bran",
    "millet bran",
    "coconut water",
    "apple sauce",
    "aquafaba",
    "mashed banana",
    "spirulina powder",
    "chlorella powder",
    "wheat flour",
    "rye flour",
    "barley flour",
    "spelt flour",
]

# Clasificación de gluten y alérgenos para cada ingrediente
CLASSIFICATION = {
    "chickpea flour": {"gluten": "No", "alergenos": "No"},
    "white rice flour": {"gluten": "No", "alergenos": "No"},
    "brown rice flour": {"gluten": "No", "alergenos": "No"},
    "tapioca starch": {"gluten": "No", "alergenos": "No"},
    "potato starch": {"gluten": "No", "alergenos": "No"},
    "corn starch": {"gluten": "No", "alergenos": "No"},
    "xanthan gum": {"gluten": "No", "alergenos": "No"},
    "guar gum": {"gluten": "No", "alergenos": "No"},
    "water": {"gluten": "No", "alergenos": "No"},
    "olive oil": {"gluten": "No", "alergenos": "No"},
    "coconut oil": {"gluten": "No", "alergenos": "No"},
    "sunflower oil": {"gluten": "No", "alergenos": "No"},
    "sea salt": {"gluten": "No", "alergenos": "No"},
    "cane sugar": {"gluten": "No", "alergenos": "No"},
    "coconut sugar": {"gluten": "No", "alergenos": "No"},
    "honey": {"gluten": "No", "alergenos": "No"},
    "maple syrup": {"gluten": "No", "alergenos": "No"},
    "apple cider vinegar": {"gluten": "No", "alergenos": "No"},
    "dry yeast": {"gluten": "No", "alergenos": "No"},
    "baking powder": {"gluten": "No", "alergenos": "No"},
    "baking soda": {"gluten": "No", "alergenos": "No"},
    "chia seeds": {"gluten": "No", "alergenos": "No"},
    "flaxseed meal": {"gluten": "No", "alergenos": "No"},
    "psyllium husk": {"gluten": "No", "alergenos": "No"},
    "almond flour": {"gluten": "No", "alergenos": "Sí"},
    "coconut flour": {"gluten": "No", "alergenos": "No"},
    "quinoa flour": {"gluten": "No", "alergenos": "No"},
    "buckwheat flour": {"gluten": "No", "alergenos": "No"},
    "sorghum flour": {"gluten": "No", "alergenos": "No"},
    "teff flour": {"gluten": "No", "alergenos": "No"},
    "millet flour": {"gluten": "No", "alergenos": "No"},
    "arrowroot starch": {"gluten": "No", "alergenos": "No"},
    "sweet potato starch": {"gluten": "No", "alergenos": "No"},
    "cassava starch": {"gluten": "No", "alergenos": "No"},
    "agar agar": {"gluten": "No", "alergenos": "No"},
    "pectin": {"gluten": "No", "alergenos": "No"},
    "lemon juice": {"gluten": "No", "alergenos": "No"},
    "orange juice": {"gluten": "No", "alergenos": "No"},
    "carrot juice": {"gluten": "No", "alergenos": "No"},
    "beet juice": {"gluten": "No", "alergenos": "No"},
    "spinach juice": {"gluten": "No", "alergenos": "No"},
    "tomato juice": {"gluten": "No", "alergenos": "No"},
    "turmeric powder": {"gluten": "No", "alergenos": "No"},
    "cinnamon": {"gluten": "No", "alergenos": "No"},
    "ginger powder": {"gluten": "No", "alergenos": "No"},
    "paprika": {"gluten": "No", "alergenos": "No"},
    "cumin": {"gluten": "No", "alergenos": "No"},
    "coriander": {"gluten": "No", "alergenos": "No"},
    "oregano": {"gluten": "No", "alergenos": "No"},
    "thyme": {"gluten": "No", "alergenos": "No"},
    "basil": {"gluten": "No", "alergenos": "No"},
    "rosemary": {"gluten": "No", "alergenos": "No"},
    "garlic powder": {"gluten": "No", "alergenos": "No"},
    "onion powder": {"gluten": "No", "alergenos": "No"},
    "black pepper": {"gluten": "No", "alergenos": "No"},
    "vanilla extract": {"gluten": "No", "alergenos": "No"},
    "cocoa powder": {"gluten": "No", "alergenos": "No"},
    "carob powder": {"gluten": "No", "alergenos": "No"},
    "nutritional yeast": {"gluten": "No", "alergenos": "No"},
    "pumpkin puree": {"gluten": "No", "alergenos": "No"},
    "sweet potato puree": {"gluten": "No", "alergenos": "No"},
    "zucchini puree": {"gluten": "No", "alergenos": "No"},
    "carrot puree": {"gluten": "No", "alergenos": "No"},
    "spinach puree": {"gluten": "No", "alergenos": "No"},
    "beet puree": {"gluten": "No", "alergenos": "No"},
    "tomato puree": {"gluten": "No", "alergenos": "No"},
    "cauliflower puree": {"gluten": "No", "alergenos": "No"},
    "broccoli puree": {"gluten": "No", "alergenos": "No"},
    "kale puree": {"gluten": "No", "alergenos": "No"},
    "pea flour": {"gluten": "No", "alergenos": "No"},
    "lentil flour": {"gluten": "No", "alergenos": "No"},
    "fava bean flour": {"gluten": "No", "alergenos": "No"},
    "amaranth flour": {"gluten": "No", "alergenos": "No"},
    "flaxseed flour": {"gluten": "No", "alergenos": "No"},
    "sunflower seed flour": {"gluten": "No", "alergenos": "No"},
    "pumpkin seed flour": {"gluten": "No", "alergenos": "No"},
    "sesame seed flour": {"gluten": "No", "alergenos": "No"},
    "hemp seed flour": {"gluten": "No", "alergenos": "No"},
    "oat bran": {"gluten": "No (certificado)", "alergenos": "No"},
    "rice bran": {"gluten": "No", "alergenos": "No"},
    "millet bran": {"gluten": "No", "alergenos": "No"},
    "coconut water": {"gluten": "No", "alergenos": "No"},
    "apple sauce": {"gluten": "No", "alergenos": "No"},
    "aquafaba": {"gluten": "No", "alergenos": "No"},
    "mashed banana": {"gluten": "No", "alergenos": "No"},
    "spirulina powder": {"gluten": "No", "alergenos": "No"},
    "chlorella powder": {"gluten": "No", "alergenos": "No"},
    "wheat flour": {"gluten": "Sí", "alergenos": "No"},
    "rye flour": {"gluten": "Sí", "alergenos": "No"},
    "barley flour": {"gluten": "Sí", "alergenos": "No"},
    "spelt flour": {"gluten": "Sí", "alergenos": "No"},
}


# Función para obtener el fdcId de un ingrediente
def get_fdc_id(ingredient):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={ingredient}&api_key={API_KEY}"
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=30).json()
            if "foods" in response and response["foods"]:
                return response["foods"][0]["fdcId"]
            else:
                print(f"No se encontraron resultados para '{ingredient}'.")
                return None
        except requests.exceptions.ReadTimeout:
            print(f"Timeout para '{ingredient}'. Reintentando en {2 ** attempt} segundos...")
            time.sleep(2**attempt)
        except Exception as e:
            print(f"Error al obtener fdcId para '{ingredient}': {e}")
            return None
    print(f"No se pudo obtener fdcId para '{ingredient}' tras 3 intentos.")
    return None


# Función para obtener los datos nutricionales de un ingrediente usando su fdcId
def get_nutritional_data(fdc_id):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={API_KEY}"
    try:
        response = requests.get(url, timeout=30).json()
        nutrients = response["foodNutrients"]
        data = {}
        for nutrient in nutrients:
            name = nutrient["nutrient"]["name"]
            value = nutrient.get("amount", 0)
            if name == "Energy":
                data["calories"] = value
            elif name == "Protein":
                data["protein"] = value
            elif name == "Carbohydrate, by difference":
                data["carbs"] = value
            elif name == "Total lipid (fat)":
                data["fat"] = value
            elif name == "Fiber, total dietary":
                data["fiber"] = value
            elif name == "Sodium, Na":
                data["sodium"] = value
        data["contains_gluten"] = CLASSIFICATION.get(ingredient, {"gluten": "No"})["gluten"]
        data["contains_allergens"] = CLASSIFICATION.get(ingredient, {"alergenos": "No"})[
            "alergenos"
        ]
        return data
    except Exception as e:
        print(f"Error al obtener datos nutricionales para fdcId {fdc_id}: {e}")
        return {}


# Recolectar datos para todos los ingredientes
database = []
for ingredient in INGREDIENTS:
    print(f"Procesando '{ingredient}'...")
    fdc_id = get_fdc_id(ingredient)
    if fdc_id:
        data = get_nutritional_data(fdc_id)
        if data:
            data["ingredient"] = ingredient
            database.append(data)
    time.sleep(1)  # Retraso para respetar límites de la API

# Guardar los datos en un archivo CSV
if database:
    df = pd.DataFrame(
        database,
        columns=[
            "ingredient",
            "calories",
            "protein",
            "carbs",
            "fat",
            "fiber",
            "sodium",
            "contains_gluten",
            "contains_allergens",
        ],
    )
    df.to_csv("../data/ingredients_data_doughs.csv", index=False)
    print("Base de datos guardada en '../data/ingredients_data_doughs.csv'.")
else:
    print("No se recolectaron datos para ningún ingrediente.")
