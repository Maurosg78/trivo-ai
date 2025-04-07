import pandas as pd

# Cargar el archivo existente
df = pd.read_csv("data/ingredients_data_gluten_free.csv")

# Diccionarios con valores de ejemplo (completa con los reales)
density_values = {
    "rice flour": 0.7,
    "cauliflower": 0.3,
    "water": 1.0,
    # Agrega todos tus ingredientes
}
absorption_values = {
    "rice flour": 0.6,
    "cauliflower": 0.8,
    "water": 0.0,
    # Agrega todos tus ingredientes
}

# Agregar columnas al DataFrame
df["density"] = df["ingredient"].map(density_values)
df["absorption"] = df["ingredient"].map(absorption_values)

# Guardar el archivo actualizado
df.to_csv("data/ingredients_data_gluten_free.csv", index=False)
print("Propiedades físicas agregadas a 'ingredients_data_gluten_free.csv'.")
