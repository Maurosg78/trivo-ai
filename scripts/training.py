import os

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# Cargar datos nutricionales desde el CSV generado
nutritional_data = {}
if os.path.exists("data/nutritional_data.csv"):
    df_nutritional = pd.read_csv("data/nutritional_data.csv")
    for index, row in df_nutritional.iterrows():
        nutritional_data[row["ingredient"]] = {
            "calories": row["calories"] if pd.notna(row["calories"]) else 0,
            "protein": row["protein"] if pd.notna(row["protein"]) else 0,
            "carbs": row["carbs"] if pd.notna(row["carbs"]) else 0,
            "fat": row["fat"] if pd.notna(row["fat"]) else 0,
        }
else:
    print("Error: No se encontró 'nutritional_data.csv'. Usando valores predeterminados.")
    nutritional_data = {
        "cauliflower": {"calories": 24.0, "protein": 2.35, "carbs": 4.71, "fat": 0.0},
        "chickpea_flour": {"calories": 364.0, "protein": 19.0, "carbs": 61.0, "fat": 6.0},
        "rice_flour": {"calories": 346.0, "protein": 7.69, "carbs": 80.8, "fat": 0.0},
        "maize_flour": {"calories": 361.0, "protein": 6.9, "carbs": 76.85, "fat": 3.9},
        "potato_flour": {"calories": 357.0, "protein": 6.9, "carbs": 83.1, "fat": 0.34},
        "corn_starch": {"calories": 350.0, "protein": 0.0, "carbs": 90.0, "fat": 0.0},
        "olive_oil": {"calories": 900.0, "protein": 0.0, "carbs": 0.0, "fat": 100.0},
        "egg_substitute": {"calories": 50.0, "protein": 2.0, "carbs": 5.0, "fat": 0.0},
        "salt": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
        "water": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
        "xanthan_gum": {"calories": 333.0, "protein": 0.0, "carbs": 83.0, "fat": 0.0},
        "sugar": {"calories": 375.0, "protein": 0.0, "carbs": 100.0, "fat": 0.0},
    }

# Cargar datos experimentales para elasticidad y densidad
try:
    df_exp = pd.read_csv("data/experimental_data.csv")
except FileNotFoundError:
    print("Error: No se encontró 'experimental_data.csv'. Creando datos simulados.")
    df_exp = pd.DataFrame(
        {
            "cauliflower_ratio": [1.0, 0.8, 0.6, 0.4, 0.2, 0.0],
            "chickpea_ratio": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "elasticity": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            "density": [0.9, 0.85, 0.8, 0.75, 0.7, 0.65],
        }
    )
    df_exp.to_csv("data/experimental_data.csv", index=False)

# Modelos de predicción
elasticity_models = {}
density_models = {}
for ingredient in ["cauliflower", "chickpea_flour"]:
    if ingredient == "cauliflower":
        X_elasticity = df_exp[df_exp["chickpea_ratio"] == 0][["cauliflower_ratio"]]
        y_elasticity = df_exp[df_exp["chickpea_ratio"] == 0]["elasticity"]
        X_density = df_exp[df_exp["chickpea_ratio"] == 0][["cauliflower_ratio"]]
        y_density = df_exp[df_exp["chickpea_ratio"] == 0]["density"]
        feature_name = "cauliflower_ratio"
    else:
        X_elasticity = df_exp[df_exp["cauliflower_ratio"] == 0][["chickpea_ratio"]]
        y_elasticity = df_exp[df_exp["cauliflower_ratio"] == 0]["elasticity"]
        X_density = df_exp[df_exp["cauliflower_ratio"] == 0][["chickpea_ratio"]]
        y_density = df_exp[df_exp["cauliflower_ratio"] == 0]["density"]
        feature_name = "chickpea_ratio"
    if len(X_elasticity) > 0 and len(X_density) > 0:
        model_elasticity = LinearRegression()
        model_density = LinearRegression()
        model_elasticity.fit(X_elasticity, y_elasticity)
        model_density.fit(X_density, y_density)
        elasticity_models[ingredient] = (model_elasticity, feature_name)
        density_models[ingredient] = (model_density, feature_name)


# Clase base para formulaciones
class Masa:
    def __init__(self, name, main_ingredient, formulation):
        self.name = name
        self.main_ingredient = main_ingredient
        self.formulation = formulation.copy()
        self.validate_formulation()

    def validate_formulation(self):
        total = sum(self.formulation.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"La suma de proporciones en {self.name} debe ser aproximadamente 1.0 (es {total})"
            )

    def predict_properties(self):
        """Predice elasticidad, densidad, calorías y proteínas basándose en la formulación."""
        elasticity = 0.5  # Valor por defecto
        density = 0.8  # Valor por defecto
        if self.main_ingredient in elasticity_models:
            model_elasticity, feature_name = elasticity_models[self.main_ingredient]
            model_density, _ = density_models[self.main_ingredient]
            main_ratio = self.formulation.get(self.main_ingredient, 0)
            input_data = pd.DataFrame([[main_ratio]], columns=[feature_name])
            elasticity = model_elasticity.predict(input_data)[0]
            density = model_density.predict(input_data)[0]

        calories = sum(
            ratio * nutritional_data.get(ing, {"calories": 0})["calories"]
            for ing, ratio in self.formulation.items()
        )
        protein = sum(
            ratio * nutritional_data.get(ing, {"protein": 0})["protein"]
            for ing, ratio in self.formulation.items()
        )

        return {
            "elasticity": elasticity,
            "density": density,
            "calories": calories,
            "protein": protein,
        }


# Formulaciones iniciales basadas en Greensy
formulations = {
    "C12": Masa(
        "C12",
        "cauliflower",
        {
            "cauliflower": 0.323,
            "rice_flour": 0.323,
            "maize_flour": 0.162,
            "corn_starch": 0.041,
            "egg_substitute": 0.02,
            "salt": 0.008,
            "water": 0.123,
        },
    ),
    "G12": Masa(
        "G12",
        "chickpea_flour",
        {
            "chickpea_flour": 0.204,
            "rice_flour": 0.122,
            "potato_flour": 0.143,
            "corn_starch": 0.163,
            "olive_oil": 0.061,
            "salt": 0.01,
            "water": 0.244,
            "xanthan_gum": 0.008,
            "sugar": 0.045,
        },
    ),
}


# Función de optimización
def optimize_recipe(masa_name, target="min_density", min_elasticity=0.5, max_calories=300):
    """Optimiza una masa ajustando ingredientes secundarios."""
    masa = formulations[masa_name]
    best_result = None
    best_score = float("inf") if target == "min_density" else -float("inf")

    adjustable = "rice_flour" if masa_name == "C12" else "potato_flour"
    main_ing = masa.main_ingredient

    for ratio in np.arange(0.1, 0.4, 0.05):
        new_form = masa.formulation.copy()
        delta = new_form[adjustable] - ratio
        new_form[adjustable] = ratio
        new_form["water"] += delta  # Ajustamos agua para mantener la suma en 1.0

        temp_masa = Masa(masa_name, main_ing, new_form)
        result = temp_masa.predict_properties()

        if result["elasticity"] >= min_elasticity and result["calories"] <= max_calories:
            score = result["density"] if target == "min_density" else -result["calories"]
            if (target == "min_density" and score < best_score) or (
                target == "min_calories" and score > best_score
            ):
                best_score = score
                best_result = result
                best_result["formulation"] = new_form

    return best_result


# Pruebas
for masa_name in ["C12", "G12"]:
    masa = formulations[masa_name]
    print(f"\nPropiedades base para {masa_name}:")
    base_result = masa.predict_properties()
    for key, value in base_result.items():
        print(f"{key.capitalize()}: {value:.2f}")

    print("Mejor receta optimizada (mínima densidad):")
    optimal = optimize_recipe(masa_name, target="min_density")
    if optimal:
        for key, value in optimal.items():
            if key != "formulation":
                print(f"{key.capitalize()}: {value:.2f}")
        print("Formulación optimizada:", {k: f"{v:.3f}" for k, v in optimal["formulation"].items()})
    else:
        print("No se encontró solución.")
