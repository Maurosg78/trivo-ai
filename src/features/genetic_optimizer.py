import random
import copy
from typing import Dict, List, Tuple, Any, Set

class GeneticRecipeOptimizer:
    """
    Optimizador genético para recetas de masa que no requiere servicios externos.
    Utiliza algoritmos genéticos para encontrar combinaciones óptimas de ingredientes
    según las restricciones y preferencias del usuario.
    """
    
    def __init__(self, population_size=50, generations=30, 
                mutation_rate=0.2, crossover_rate=0.8, elitism_count=2):
        """
        Inicializa el optimizador genético con parámetros configurables.
        
        Args:
            population_size: Tamaño de la población
            generations: Número de generaciones
            mutation_rate: Tasa de mutación (0-1)
            crossover_rate: Tasa de cruce (0-1)
            elitism_count: Número de mejores individuos que pasan directamente a la siguiente generación
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count
        
        # Definir restricciones por tipo de receta
        self.recipe_constraints = {
            "pizza": {
                "hydration": (0.55, 0.65),     # Rango de hidratación (agua/harina)
                "salt": (0.018, 0.022),        # Rango de sal (1.8-2.2%)
                "yeast": (0.005, 0.015),       # Rango de levadura (0.5-1.5%)
                "oil": (0.03, 0.08)            # Rango de aceite (3-8%)
            },
            "pan": {
                "hydration": (0.65, 0.75),
                "salt": (0.018, 0.022),
                "yeast": (0.005, 0.015),
                "oil": (0.01, 0.03)
            },
            "flatbread": {
                "hydration": (0.60, 0.70),
                "salt": (0.015, 0.020),
                "yeast": (0.003, 0.010),
                "oil": (0.05, 0.10)
            }
        }
        
        # Categorías de ingredientes
        self.ingredient_categories = {
            "harinas": ["harina", "harina_integral", "harina_de_arroz", "harina_de_maíz", "almidón_de_maíz"],
            "líquidos": ["agua", "leche", "yogur"],
            "grasas": ["aceite_de_oliva", "mantequilla"],
            "fermentos": ["levadura", "bicarbonato", "masa_madre"],
            "otros": ["sal", "azúcar", "goma_xantana", "semillas_de_lino", "semillas_de_chía", 
                     "semillas_de_girasol", "salvado", "remolacha", "espinaca", "carbón_activado"]
        }
        
        # Compatibilidad de ingredientes (1: buena, 0: neutra, -1: mala)
        self.ingredient_compatibility = {
            ("harina_integral", "agua"): 1,          # La harina integral absorbe más agua
            ("harina_de_arroz", "goma_xantana"): 1,  # La goma xantana es necesaria con harina de arroz
            ("harina_de_maíz", "goma_xantana"): 1,   # La goma xantana es necesaria con harina de maíz
            ("levadura", "azúcar"): 1,               # El azúcar alimenta la levadura
            ("levadura", "sal"): -1,                 # La sal inhibe la levadura
            ("remolacha", "espinaca"): -1,           # Colores opuestos
            ("remolacha", "carbón_activado"): -1,    # Colores opuestos
            ("espinaca", "carbón_activado"): -1      # Colores opuestos
        }
        
        # Ingredientes conflictivos (no pueden estar juntos)
        self.ingredient_conflicts = [
            {"levadura", "bicarbonato"},           # No tiene sentido usar ambos
            {"carbón_activado", "espinaca", "remolacha"}  # Colores se anulan
        ]
    
    def optimize(self, base_recipe: Dict[str, float], recipe_type: str, 
                properties: Dict[str, Any]) -> Tuple[Dict[str, float], List[str]]:
        """
        Optimiza una receta utilizando algoritmos genéticos.
        
        Args:
            base_recipe: Receta base con ingredientes y cantidades
            recipe_type: Tipo de receta (pizza, pan, flatbread)
            properties: Propiedades especiales (sin gluten, colores, etc.)
            
        Returns:
            Tupla con la receta optimizada y recomendaciones
        """
        # Crear población inicial
        population = self._initialize_population(base_recipe, recipe_type, properties)
        
        # Ejecutar algoritmo genético
        for generation in range(self.generations):
            # Evaluar aptitud de cada individuo
            fitness_scores = [self._calculate_fitness(recipe, recipe_type, properties) 
                            for recipe in population]
            
            # Ordenar población por aptitud (mayor a menor)
            sorted_population = [x for _, x in sorted(zip(fitness_scores, population), 
                                                     key=lambda pair: pair[0], reverse=True)]
            
            # Seleccionar los mejores para elitismo
            elites = sorted_population[:self.elitism_count]
            
            # Crear nueva población mediante selección, cruce y mutación
            new_population = []
            
            # Añadir elites directamente
            new_population.extend(elites)
            
            # Llenar el resto de la población
            while len(new_population) < self.population_size:
                # Seleccionar padres
                parent1 = self._select_parent(sorted_population, fitness_scores)
                parent2 = self._select_parent(sorted_population, fitness_scores)
                
                # Cruzar con probabilidad crossover_rate
                if random.random() < self.crossover_rate:
                    child = self._crossover(parent1, parent2)
                else:
                    child = copy.deepcopy(parent1)
                
                # Mutar con probabilidad mutation_rate
                if random.random() < self.mutation_rate:
                    child = self._mutate(child, recipe_type, properties)
                
                # Añadir a nueva población
                new_population.append(child)
            
            # Actualizar población
            population = new_population
        
        # Seleccionar mejor receta
        fitness_scores = [self._calculate_fitness(recipe, recipe_type, properties) 
                         for recipe in population]
        best_recipe = population[fitness_scores.index(max(fitness_scores))]
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(best_recipe, recipe_type, properties)
        
        return best_recipe, recommendations
    
    def _initialize_population(self, base_recipe: Dict[str, float], recipe_type: str,
                              properties: Dict[str, Any]) -> List[Dict[str, float]]:
        """Inicializa una población diversa de recetas basadas en la receta base."""
        population = []
        
        # Añadir la receta base como primer individuo
        population.append(copy.deepcopy(base_recipe))
        
        # Crear individuos aleatorios basados en la receta base
        for _ in range(self.population_size - 1):
            new_recipe = copy.deepcopy(base_recipe)
            
            # Variar cantidades de ingredientes existentes
            for ingredient in new_recipe:
                # Variar cantidad en ±30%
                variation = random.uniform(0.7, 1.3)
                new_recipe[ingredient] *= variation
            
            # Añadir ocasionalmente un ingrediente nuevo
            if random.random() < 0.3:
                all_ingredients = [item for sublist in self.ingredient_categories.values() 
                                 for item in sublist]
                new_ingredient = random.choice(all_ingredients)
                
                # Si no está ya en la receta, añadirlo
                if new_ingredient not in new_recipe:
                    # Añadir en pequeña cantidad según categoría
                    if new_ingredient in self.ingredient_categories["harinas"]:
                        base_flour = sum(new_recipe.get(flour, 0) for flour in self.ingredient_categories["harinas"])
                        new_recipe[new_ingredient] = base_flour * random.uniform(0.1, 0.3)
                    elif new_ingredient in self.ingredient_categories["líquidos"]:
                        base_flour = sum(new_recipe.get(flour, 0) for flour in self.ingredient_categories["harinas"])
                        new_recipe[new_ingredient] = base_flour * random.uniform(0.05, 0.15)
                    elif new_ingredient in self.ingredient_categories["otros"]:
                        base_flour = sum(new_recipe.get(flour, 0) for flour in self.ingredient_categories["harinas"])
                        new_recipe[new_ingredient] = base_flour * random.uniform(0.01, 0.05)
                    else:
                        base_flour = sum(new_recipe.get(flour, 0) for flour in self.ingredient_categories["harinas"])
                        new_recipe[new_ingredient] = base_flour * random.uniform(0.02, 0.1)
            
            # Eliminar ocasionalmente un ingrediente (excepto ingredientes fundamentales)
            if random.random() < 0.2:
                non_essential = [ing for ing in new_recipe.keys() 
                               if ing not in ["harina", "agua", "sal"] and 
                               not (properties.get("es_sin_gluten", False) and ing in ["harina_de_arroz", "goma_xantana"])]
                
                if non_essential:
                    ingredient_to_remove = random.choice(non_essential)
                    new_recipe.pop(ingredient_to_remove, None)
            
            population.append(new_recipe)
        
        return population
    
    def _calculate_fitness(self, recipe: Dict[str, float], recipe_type: str, 
                         properties: Dict[str, Any]) -> float:
        """Calcula la aptitud de una receta según restricciones y propiedades deseadas."""
        fitness = 100.0  # Comenzar con valor máximo y penalizar
        
        # Verificar que hay harina
        total_flour = sum(recipe.get(flour, 0) for flour in self.ingredient_categories["harinas"])
        if total_flour <= 0:
            return 0.0  # Descalificar recetas sin harina
        
        # Normalizar receta a 1kg de harina para comparación
        normalized_recipe = {}
        for key, value in recipe.items():
            if key in self.ingredient_categories["harinas"]:
                normalized_recipe[key] = value / total_flour * 1000
            else:
                normalized_recipe[key] = value / total_flour * 1000
        
        # 1. Calcular y evaluar hidratación
        total_liquid = sum(recipe.get(liquid, 0) for liquid in self.ingredient_categories["líquidos"])
        if total_liquid <= 0:
            return 0.0  # Descalificar recetas sin líquidos
        
        hydration = total_liquid / total_flour
        hydration_min, hydration_max = self.recipe_constraints[recipe_type]["hydration"]
        
        if hydration < hydration_min:
            # Penalizar masa demasiado seca
            fitness -= (hydration_min - hydration) * 100
        elif hydration > hydration_max:
            # Penalizar masa demasiado húmeda
            fitness -= (hydration - hydration_max) * 100
        
        # 2. Evaluar cantidad de sal
        salt_amount = recipe.get("sal", 0)
        salt_ratio = salt_amount / total_flour
        salt_min, salt_max = self.recipe_constraints[recipe_type]["salt"]
        
        if salt_ratio < salt_min:
            fitness -= (salt_min - salt_ratio) * 1000
        elif salt_ratio > salt_max:
            fitness -= (salt_ratio - salt_max) * 1000
        
        # 3. Evaluar fermentación
        has_fermenting_agent = False
        if "levadura" in recipe and recipe["levadura"] > 0:
            has_fermenting_agent = True
            yeast_ratio = recipe["levadura"] / total_flour
            yeast_min, yeast_max = self.recipe_constraints[recipe_type]["yeast"]
            
            if yeast_ratio < yeast_min:
                fitness -= (yeast_min - yeast_ratio) * 1000
            elif yeast_ratio > yeast_max:
                fitness -= (yeast_ratio - yeast_max) * 1000
        
        if "masa_madre" in recipe and recipe["masa_madre"] > 0:
            has_fermenting_agent = True
        
        if not has_fermenting_agent:
            # Penalizar fuertemente si no tiene agente de fermentación
            fitness -= 50
        
        # 4. Evaluar aceite (si aplica)
        if recipe_type in ["pizza", "flatbread"]:
            oil_amount = recipe.get("aceite_de_oliva", 0) + recipe.get("mantequilla", 0)
            oil_ratio = oil_amount / total_flour
            oil_min, oil_max = self.recipe_constraints[recipe_type]["oil"]
            
            if oil_ratio < oil_min:
                fitness -= (oil_min - oil_ratio) * 500
            elif oil_ratio > oil_max:
                fitness -= (oil_ratio - oil_max) * 500
        
        # 5. Verificar coherencia con propiedades
        
        # Sin gluten
        if properties.get("es_sin_gluten", False):
            gluten_flours = ["harina", "harina_integral"]
            if any(recipe.get(flour, 0) > 0 for flour in gluten_flours):
                fitness -= 100  # Penalizar fuertemente si tiene harinas con gluten
            
            gluten_free_flours = ["harina_de_arroz", "harina_de_maíz", "almidón_de_maíz"]
            if not any(recipe.get(flour, 0) > 0 for flour in gluten_free_flours):
                fitness -= 75  # Penalizar si no tiene harinas sin gluten
            
            if recipe.get("goma_xantana", 0) <= 0:
                fitness -= 30  # Penalizar si no tiene goma xantana
        
        # Colores
        colors = properties.get("colores", {})
        if colors.get("rojo", False) and recipe.get("remolacha", 0) <= 0:
            fitness -= 25
        if colors.get("verde", False) and recipe.get("espinaca", 0) <= 0:
            fitness -= 25
        if colors.get("negro", False) and recipe.get("carbón_activado", 0) <= 0:
            fitness -= 25
        
        # Nutricional
        if properties.get("es_nutricional", False):
            nutritional_ingredients = ["semillas_de_lino", "semillas_de_chía", "semillas_de_girasol", 
                                     "salvado", "harina_integral"]
            if not any(recipe.get(ing, 0) > 0 for ing in nutritional_ingredients):
                fitness -= 25
        
        # 6. Verificar conflictos entre ingredientes
        for conflict_group in self.ingredient_conflicts:
            if sum(1 for ing in conflict_group if recipe.get(ing, 0) > 0) > 1:
                fitness -= 40  # Penalizar por cada grupo de conflicto violado
        
        # 7. Verificar compatibilidad
        for (ing1, ing2), compatibility in self.ingredient_compatibility.items():
            if ing1 in recipe and ing2 in recipe and recipe[ing1] > 0 and recipe[ing2] > 0:
                if compatibility == 1:
                    fitness += 10  # Bonificar buenas combinaciones
                elif compatibility == -1:
                    fitness -= 15  # Penalizar malas combinaciones
        
        # 8. Bonus por creatividad/variedad
        unique_categories_used = sum(1 for category in self.ingredient_categories.values() 
                                   if any(ing in recipe and recipe[ing] > 0 for ing in category))
        fitness += unique_categories_used * 5
        
        # Asegurar que la aptitud no sea negativa
        return max(0.0, fitness)
    
    def _select_parent(self, population: List[Dict[str, float]], 
                      fitness_scores: List[float]) -> Dict[str, float]:
        """Selecciona un padre utilizando selección por torneo."""
        tournament_size = 3
        selected_indices = random.sample(range(len(population)), tournament_size)
        selected_fitness = [fitness_scores[i] for i in selected_indices]
        winner_index = selected_indices[selected_fitness.index(max(selected_fitness))]
        return copy.deepcopy(population[winner_index])
    
    def _crossover(self, parent1: Dict[str, float], parent2: Dict[str, float]) -> Dict[str, float]:
        """Realiza cruce entre dos recetas padres."""
        child = {}
        
        # Obtener todos los ingredientes únicos de ambos padres
        all_ingredients = set(parent1.keys()).union(set(parent2.keys()))
        
        for ingredient in all_ingredients:
            # Para cada ingrediente, decidir aleatoriamente de qué padre heredar
            if ingredient in parent1 and ingredient in parent2:
                # Si ambos padres tienen el ingrediente, escoger valor o promediar
                if random.random() < 0.5:
                    child[ingredient] = parent1[ingredient]
                else:
                    child[ingredient] = parent2[ingredient]
            elif ingredient in parent1:
                # Solo padre1 tiene el ingrediente, 50% de probabilidad de heredarlo
                if random.random() < 0.5:
                    child[ingredient] = parent1[ingredient]
            elif ingredient in parent2:
                # Solo padre2 tiene el ingrediente, 50% de probabilidad de heredarlo
                if random.random() < 0.5:
                    child[ingredient] = parent2[ingredient]
        
        return child
    
    def _mutate(self, recipe: Dict[str, float], recipe_type: str, 
               properties: Dict[str, Any]) -> Dict[str, float]:
        """Aplica mutación a una receta."""
        mutated = copy.deepcopy(recipe)
        
        # Calcular harina total para referencia
        total_flour = sum(recipe.get(flour, 0) for flour in self.ingredient_categories["harinas"])
        
        # 1. Mutar valores existentes (30% de probabilidad por ingrediente)
        for ingredient in list(mutated.keys()):
            if random.random() < 0.3:
                # Variar cantidad en ±30%
                variation = random.uniform(0.7, 1.3)
                mutated[ingredient] *= variation
        
        # 2. Añadir un nuevo ingrediente (20% de probabilidad)
        if random.random() < 0.2:
            # Obtener todos los ingredientes posibles que no están en la receta
            all_ingredients = [item for sublist in self.ingredient_categories.values() 
                             for item in sublist]
            available_ingredients = [ing for ing in all_ingredients if ing not in mutated]
            
            if available_ingredients:
                new_ingredient = random.choice(available_ingredients)
                
                # Añadir en cantidad adecuada según categoría
                if new_ingredient in self.ingredient_categories["harinas"]:
                    mutated[new_ingredient] = total_flour * random.uniform(0.1, 0.3)
                elif new_ingredient in self.ingredient_categories["líquidos"]:
                    mutated[new_ingredient] = total_flour * random.uniform(0.05, 0.15)
                elif new_ingredient in self.ingredient_categories["otros"]:
                    mutated[new_ingredient] = total_flour * random.uniform(0.01, 0.05)
                else:
                    mutated[new_ingredient] = total_flour * random.uniform(0.02, 0.1)
        
        # 3. Eliminar un ingrediente (15% de probabilidad)
        if random.random() < 0.15:
            # No eliminar ingredientes esenciales
            non_essential = [ing for ing in mutated.keys() 
                           if ing not in ["harina", "agua", "sal"] and 
                           not (properties.get("es_sin_gluten", False) and ing in ["harina_de_arroz", "goma_xantana"])]
            
            if non_essential:
                ingredient_to_remove = random.choice(non_essential)
                mutated.pop(ingredient_to_remove, None)
        
        return mutated
    
    def _generate_recommendations(self, recipe: Dict[str, float], recipe_type: str, 
                                properties: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones para la receta optimizada."""
        recommendations = []
        
        # Calcular valores clave
        total_flour = sum(recipe.get(flour, 0) for flour in self.ingredient_categories["harinas"])
        total_liquid = sum(recipe.get(liquid, 0) for liquid in self.ingredient_categories["líquidos"])
        hydration = (total_liquid / total_flour) * 100 if total_flour > 0 else 0
        
        # Recomendación sobre hidratación
        if recipe_type == "pizza":
            recommendations.append(f"Hidratación: {hydration:.1f}%. Para pizza se recomienda entre 55-65%.")
        elif recipe_type == "pan":
            recommendations.append(f"Hidratación: {hydration:.1f}%. Para pan se recomienda entre 65-75%.")
        elif recipe_type == "flatbread":
            recommendations.append(f"Hidratación: {hydration:.1f}%. Para pan plano se recomienda entre 60-70%.")
        
        # Recomendación sobre levadura
        if "levadura" in recipe:
            yeast_ratio = (recipe["levadura"] / total_flour) * 100
            if yeast_ratio < 0.5:
                recommendations.append(f"Levadura: {yeast_ratio:.2f}%. Cantidad baja, recomendada para fermentación lenta (12-24h).")
            elif yeast_ratio > 1.5:
                recommendations.append(f"Levadura: {yeast_ratio:.2f}%. Cantidad alta, la fermentación será rápida (1-3h).")
            else:
                recommendations.append(f"Levadura: {yeast_ratio:.2f}%. Cantidad equilibrada para fermentación media (4-8h).")
        
        # Recomendación sobre receta sin gluten
        if properties.get("es_sin_gluten", False):
            if recipe.get("goma_xantana", 0) > 0:
                recommendations.append("La goma xantana ayuda a dar elasticidad a la masa sin gluten, similar al gluten.")
            else:
                recommendations.append("Considera añadir goma xantana para mejorar la elasticidad de la masa sin gluten.")
            
            recommendations.append("Para masas sin gluten, la fermentación será menos activa. Considera usar más levadura.")
        
        # Recomendación sobre temperatura de horneado
        if recipe_type == "pizza":
            recommendations.append("Temperatura de horneado: Máxima (250-300°C) durante 5-8 minutos.")
        elif recipe_type == "pan":
            recommendations.append("Temperatura de horneado: Iniciar a 220°C (15 min) y luego bajar a 190°C (25-35 min).")
        elif recipe_type == "flatbread":
            recommendations.append("Temperatura de horneado: 220°C durante 15-18 minutos.")
        
        # Consejos adicionales basados en ingredientes específicos
        if recipe.get("aceite_de_oliva", 0) > 0:
            oil_ratio = (recipe["aceite_de_oliva"] / total_flour) * 100
            if oil_ratio > 10:
                recommendations.append(f"El contenido de aceite ({oil_ratio:.1f}%) es alto. Dará sabor y suavidad, pero puede hacer la masa más pesada.")
        
        if recipe.get("semillas_de_lino", 0) > 0 or recipe.get("semillas_de_chía", 0) > 0:
            recommendations.append("Las semillas absorben agua. Considera aumentar ligeramente el agua si la masa queda seca.")
        
        return recommendations 