# flake8: noqa: E402
import matplotlib
matplotlib.use("Agg")  # Evita abrir ventanas gráficas

import datetime
import logging
import os
import random
from functools import partial
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from deap import base, creator, tools
from pydantic import BaseModel

from src.core.models.ingredient import Ingredient
from src.core.models.recipe import Recipe
from src.core.services.usda_service import USDAService

# ----------------------------------------------------------------------
# 1. CONFIGURACIÓN DE LOGGING Y CARPETAS
# ----------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

RESULTS_FOLDER = os.path.join(CURRENT_DIR, "resultados_main")
REPORTS_FOLDER = os.path.join(CURRENT_DIR, "informes_main")
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# ----------------------------------------------------------------------
# 2. CONSTANTES Y LISTAS
# ----------------------------------------------------------------------
CORN_STARCH = "corn starch"
XANTHAN_GUM = "xanthan gum"

# Ingrediente base por cada tipo de masa
BASE_INGREDIENTS = {"C12": "cauliflower", "G12": "chickpea_flour"}

# Ingredientes ajustables
ADJUSTABLE_INGREDIENTS = [
    "rice_flour",
    "potato_flour",
    CORN_STARCH,
    "olive_oil",
    XANTHAN_GUM,
    "sugar",
    "salt",
    "vinegar",
]

# Ejemplo de sustitutos
SUBSTITUTES = {
    "chickpea_flour": ["almond_flour", "coconut_flour"],
    "rice_flour": [CORN_STARCH, "potato_flour"],
}

# Costos de ejemplo
INGREDIENT_COSTS = {
    "water": 0.01,
    "cauliflower": 0.25,
    "chickpea_flour": 0.30,
    "rice_flour": 0.20,
    "potato_flour": 0.15,
    CORN_STARCH: 0.10,
    "olive_oil": 0.50,
    XANTHAN_GUM: 0.80,
    "sugar": 0.05,
    "salt": 0.03,
    "vinegar": 0.07,
    "almond_flour": 0.35,
    "coconut_flour": 0.40,
}

# ----------------------------------------------------------------------
# 3. CARGA DE DATOS DE INGREDIENTES
# ----------------------------------------------------------------------
try:
    csv_path = os.path.join(CURRENT_DIR, "data", "processed", "ingredients_data_gluten_free.csv")
    df = pd.read_csv(csv_path, encoding="utf-8")
    df["ingredient"] = df["ingredient"].str.strip().str.lower()
    INGREDIENTS_DATA = df.set_index("ingredient").to_dict("index")
    logging.info(f"Datos de ingredientes cargados desde: {csv_path}")
except FileNotFoundError:
    logging.warning("No se encontró el CSV. Usando valores simulados en memoria.")
    df = pd.DataFrame(
        [
            ["cauliflower", 30.0, 2.4, 5.0, 0.4, 2.0, 15.0],
            ["chickpea_flour", 400.0, 16.67, 70.0, 5.0, 16.70, 0.0],
            ["rice_flour", 375.0, 7.5, 82.5, 0.0, 0.0, 0.0],
            ["potato_flour", 333.0, 0.0, 83.3, 0.0, 0.0, 0.0],
            ["corn starch", 350.0, 0.0, 90.0, 0.0, 0.0, 0.0],
            ["xanthan gum", 625.0, 0.0, 125.0, 0.0, 0.0, 3125.0],
            ["water", 42.0, 0.0, 10.8, 0.0, 0.0, 8.0],
            ["olive_oil", 900.0, 0.0, 0.0, 100.0, 0.0, 2.0],
            ["sugar", 375.0, 0.0, 100.0, 0.0, 0.0, 0.0],
            ["salt", 0.0, 0.0, 0.0, 0.0, 0.0, 39300.0],
            ["vinegar", 20.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        columns=["ingredient", "calories", "protein", "carbs", "fat", "fiber", "sodium"],
    )
    df["ingredient"] = df["ingredient"].str.lower()
    INGREDIENTS_DATA = df.set_index("ingredient").to_dict("index")
    logging.info("Datos simulados creados en memoria.")

# ----------------------------------------------------------------------
# 4. CREACIÓN DE FITNESS E INDIVIDUOS
#    Minimizar densidad, costo y también (negativo de) elasticidad
# ----------------------------------------------------------------------
creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()


# ----------------------------------------------------------------------
# 5. FUNCIONES AUXILIARES
# ----------------------------------------------------------------------
def estimar_densidad_ingrediente(ing):
    data = INGREDIENTS_DATA.get(ing.lower(), {})
    # Valor por defecto si no existe
    return data.get("density", 0.5)


def estimar_elasticidad_ingrediente(ing):
    data = INGREDIENTS_DATA.get(ing.lower(), {})
    if "elasticity" in data:
        return data["elasticity"]
    carbs = data.get("carbs", 0)
    protein = data.get("protein", 0)
    fat = data.get("fat", 0)
    # Ejemplo sencillo
    return min(1.0, 0.01 * carbs + 0.02 * protein + 0.005 * fat)


def calcular_sodio(receta):
    return sum(
        INGREDIENTS_DATA.get(ing, {}).get("sodium", 0) * prop for ing, prop in receta.items()
    )


def calcular_proteinas(receta):
    return sum(
        INGREDIENTS_DATA.get(ing, {}).get("protein", 0) * prop for ing, prop in receta.items()
    )


def calcular_contribuciones(receta):
    densidad = 0.0
    elasticidad = 0.0
    for ing, prop in receta.items():
        densidad += estimar_densidad_ingrediente(ing) * prop
        elasticidad += estimar_elasticidad_ingrediente(ing) * prop
    return densidad, elasticidad


def evaluate_individual(individual, masa_name, all_ingredients):
    """Devuelve (densidad, costo, -elasticidad)."""
    receta = dict(zip(all_ingredients, individual))
    base_ing = BASE_INGREDIENTS[masa_name]

    # Penalizamos si el ingrediente base está en 0
    if receta.get(base_ing, 0) <= 0:
        return (9999.0, 9999.0, 9999.0)

    densidad, elasticidad = calcular_contribuciones(receta)
    sodio = calcular_sodio(receta)
    proteinas = calcular_proteinas(receta)

    # Penalizaciones suaves
    if sodio > 400:
        densidad += 200.0
    if proteinas < 6:
        elasticidad -= 200.0

    # Bonus por vinagre
    if receta.get("vinegar", 0) > 0.01:
        elasticidad += 0.05

    # Costo
    costo = 0.0
    for ing, prop in receta.items():
        c = INGREDIENT_COSTS.get(ing, 0.1)
        costo += c * prop

    # Minimizar densidad, costo y -elasticidad (=> maximizar elasticidad)
    return (densidad, costo, -elasticidad)


def suggest_substitutes(ing):
    """Sustituto basado en la similitud de densidad y elasticidad."""
    if ing not in SUBSTITUTES:
        return ing
    orig_d = estimar_densidad_ingrediente(ing)
    orig_e = estimar_elasticidad_ingrediente(ing)
    best_sub = SUBSTITUTES[ing][0]
    min_diff = float("inf")

    for sub in SUBSTITUTES[ing]:
        d2 = estimar_densidad_ingrediente(sub)
        e2 = estimar_elasticidad_ingrediente(sub)
        diff = abs(orig_d - d2) + abs(orig_e - e2)
        if diff < min_diff:
            min_diff = diff
            best_sub = sub
    return best_sub


# ----------------------------------------------------------------------
# 6. FUNCIÓN DE REPARACIÓN Y NORMALIZACIÓN
# ----------------------------------------------------------------------
def repair_individual(individual, masa_name, all_ingredients):
    base_ing = BASE_INGREDIENTS[masa_name]
    for i, ing in enumerate(all_ingredients):
        # Clampeamos [0..1]
        individual[i] = max(0.0, min(1.0, individual[i]))

        if ing == base_ing:
            # Forzamos [0.2..0.5] para el ingrediente base
            individual[i] = max(0.2, min(0.5, individual[i]))
        elif ing == "water":
            individual[i] = max(0.4, min(0.6, individual[i]))
        elif ing == CORN_STARCH:
            individual[i] = max(0.05, individual[i])
        elif ing == XANTHAN_GUM:
            individual[i] = max(0.005, individual[i])
        elif ing == "vinegar":
            individual[i] = max(0.01, individual[i])

    total = sum(individual)
    if total > 0:
        individual = [p / total for p in individual]
    else:
        # Fallback si todo se va a 0
        n = len(individual)
        individual = [1.0 / n] * n

    return individual


# ----------------------------------------------------------------------
# 7. CREACIÓN DE INDIVIDUO INICIAL
# ----------------------------------------------------------------------
def crear_receta_inicial(masa_name, all_ingredients):
    props = []
    base_ing = BASE_INGREDIENTS[masa_name]
    for ing in all_ingredients:
        if ing == base_ing:
            prop = random.uniform(0.2, 0.3)
        elif ing == "water":
            prop = random.uniform(0.4, 0.6)
        elif ing == CORN_STARCH:
            prop = random.uniform(0.05, 0.15)
        elif ing == XANTHAN_GUM:
            prop = random.uniform(0.005, 0.02)
        elif ing == "vinegar":
            prop = random.uniform(0.01, 0.02)
        else:
            prop = random.uniform(0.0, 0.1)
        props.append(prop)

    total = sum(props)
    if total > 0:
        return [p / total for p in props]
    return [1.0 / len(props)] * len(props)


# ----------------------------------------------------------------------
# 8. ALGORITMO GENÉTICO MÍNIMO (EA MU+LAMBDA)
# ----------------------------------------------------------------------
def evaluate_and_repair_population(population, toolbox):
    """Evalúa y repara cada individuo de la población."""
    for ind in population:
        toolbox.repair(ind)
        ind.fitness.values = toolbox.evaluate(ind)


def create_offspring(parents, lambda_, toolbox, cxpb, mutpb):
    """Genera la descendencia."""
    offspring = []
    while len(offspring) < lambda_:
        p1, p2 = random.sample(parents, 2)
        p1, p2 = map(toolbox.clone, (p1, p2))

        if random.random() < cxpb:
            toolbox.mate(p1, p2)
        if random.random() < mutpb:
            toolbox.mutate(p1)
        if random.random() < mutpb:
            toolbox.mutate(p2)

        toolbox.repair(p1)
        toolbox.repair(p2)
        del p1.fitness.values
        del p2.fitness.values

        offspring.append(p1)
        if len(offspring) < lambda_:
            offspring.append(p2)

    return offspring


def custom_ea_mu_plus_lambda(population, toolbox, mu, lambda_, cxpb, mutpb, ngen):
    # Evaluar población inicial
    evaluate_and_repair_population(population, toolbox)

    for _ in range(ngen):
        parents = toolbox.select(population, mu)
        parents = list(map(toolbox.clone, parents))

        offspring = create_offspring(parents, lambda_, toolbox, cxpb, mutpb)

        for ind in offspring:
            ind.fitness.values = toolbox.evaluate(ind)

        population = parents + offspring
        population = toolbox.select(population, mu + lambda_)

    return population


# ----------------------------------------------------------------------
# 9. GUARDAR ARCHIVOS DE RESULTADOS
# ----------------------------------------------------------------------
def _save_file(content: str, folder_path: str, max_files: int = 10):
    """Guarda un archivo .txt y elimina los más antiguos si excede max_files."""
    os.makedirs(folder_path, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.txt"
    filepath = os.path.join(folder_path, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    logging.info("Archivo guardado en: %s", filepath)

    # Limitar la cantidad de archivos
    files = [os.path.join(folder_path, x) for x in os.listdir(folder_path) if x.endswith(".txt")]
    files.sort(key=lambda x: os.path.getmtime(x))
    while len(files) > max_files:
        oldest = files.pop(0)
        os.remove(oldest)
        logging.info("Archivo antiguo eliminado: %s", oldest)


# ----------------------------------------------------------------------
# 10. OPTIMIZACIÓN PRINCIPAL
# ----------------------------------------------------------------------
def optimize_genetic(masa_name, pop_size=30, ngen=20):
    """Optimiza la masa (C12 o G12) y retorna la mejor receta."""
    all_ingredients = ["water", BASE_INGREDIENTS[masa_name]] + ADJUSTABLE_INGREDIENTS

    toolbox.register(
        "individual",
        tools.initIterate,
        creator.Individual,
        partial(crear_receta_inicial, masa_name, all_ingredients),
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register(
        "evaluate",
        partial(evaluate_individual, masa_name=masa_name, all_ingredients=all_ingredients),
    )
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.05, indpb=0.3)
    toolbox.register("select", tools.selNSGA2)
    toolbox.register(
        "repair", partial(repair_individual, masa_name=masa_name, all_ingredients=all_ingredients)
    )

    # Crear población
    pop = toolbox.population(n=pop_size)
    # Ejecutar el algoritmo
    final_pop = custom_ea_mu_plus_lambda(
        pop, toolbox, mu=pop_size, lambda_=pop_size, cxpb=0.7, mutpb=0.3, ngen=ngen
    )

    # Hall of Fame
    hof = tools.ParetoFront()
    hof.update(final_pop)
    best_ind = hof[0]
    best_recipe = dict(zip(all_ingredients, best_ind))

    # Graficar frentes de Pareto
    fronts = tools.sortNondominated(final_pop, len(final_pop), first_front_only=False)
    for i, front in enumerate(fronts):
        densidades = [ind.fitness.values[0] for ind in front]
        elasticidades = [-ind.fitness.values[2] for ind in front]  # inverso
        plt.scatter(densidades, elasticidades, label=f"Frente {i+1}")

    plt.xlabel("Densidad")
    plt.ylabel("Elasticidad")
    plt.title(f"Fronteras de Pareto para {masa_name}")
    plt.legend()

    # Guardar PNG
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    png_name = f"pareto_{masa_name}_{now_str}.png"
    png_path = os.path.join(RESULTS_FOLDER, png_name)
    plt.savefig(png_path)
    plt.close()
    logging.info("Gráfico Pareto guardado en: %s", png_path)

    # Guardar resumen en resultados_main
    text_result = f"--- Resumen de Optimización para {masa_name} ---\n"
    for ing, prop in best_recipe.items():
        text_result += f"{ing}: {prop*100:.1f}%\n"
    _save_file(text_result, RESULTS_FOLDER)

    # Sugerencias de sustitución
    for ing in best_recipe:
        maybe_sub = suggest_substitutes(ing)
        if maybe_sub != ing:
            logging.info("Sugerencia: sustituir '%s' por '%s'", ing, maybe_sub)

    return best_recipe


# ----------------------------------------------------------------------
# 11. INFORME AMIGABLE
# ----------------------------------------------------------------------
def generate_friendly_report(masa_name, best_recipe):
    """Genera un informe en texto más entendible y lo guarda en 'informes_main'."""
    all_ingredients = ["water", BASE_INGREDIENTS[masa_name]] + ADJUSTABLE_INGREDIENTS
    dens, cost, neg_elas = evaluate_individual(
        list(best_recipe.values()), masa_name, all_ingredients
    )
    elas = -neg_elas

    report = f"\n--- Informe Amigable ({masa_name}) ---\n\n"
    report += "Receta optimizada:\n"
    for ing, prop in best_recipe.items():
        report += f"  - {ing}: {prop*100:.2f}%\n"
    report += "\nResultados:\n"
    report += f"  - Densidad: {dens:.2f}\n"
    report += f"  - Elasticidad: {elas:.2f}\n"
    report += f"  - Costo: {cost:.2f}\n"
    report += "--- Fin del Informe ---\n"

    logging.info(report)
    _save_file(report, REPORTS_FOLDER)  # Guardar en informes_main
    logging.info(f"Informe amigable guardado en carpeta: {REPORTS_FOLDER}")


# ----------------------------------------------------------------------
# 12. EJEMPLO DE USO (MAIN)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Optimizar masa C12
    best_c12 = optimize_genetic("C12", pop_size=30, ngen=20)
    logging.info("Mejor receta C12 -> %s", best_c12)
    generate_friendly_report("C12", best_c12)

    # Optimizar masa G12
    best_g12 = optimize_genetic("G12", pop_size=30, ngen=20)
    logging.info("Mejor receta G12 -> %s", best_g12)
    generate_friendly_report("G12", best_g12)
