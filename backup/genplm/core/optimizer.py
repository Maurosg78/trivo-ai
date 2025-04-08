"""
Sistema de optimización genética para recetas.

Este módulo implementa un algoritmo genético para optimizar recetas
de acuerdo a distintos objetivos como costos, nutrición o propiedades.
"""

import random
import copy
import math
from typing import List, Dict, Any, Callable, Tuple, Optional

from genplm.core.recipe_model import Recipe, Ingredient


class GeneticOptimizer:
    """
    Optimizador genético para recetas.
    
    Utiliza algoritmos genéticos para encontrar la mejor combinación de
    ingredientes y cantidades para una receta de acuerdo a los criterios
    especificados.
    """
    
    def __init__(
        self,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elitism: int = 2
    ):
        """
        Inicializa el optimizador genético.
        
        Args:
            population_size: Tamaño de la población de recetas
            generations: Número máximo de generaciones
            mutation_rate: Probabilidad de mutación (0-1)
            crossover_rate: Probabilidad de cruce (0-1)
            elitism: Número de mejores individuos que pasan a la siguiente generación
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism = elitism
        
        # Restricciones para las cantidades de ingredientes
        self.ingredient_constraints: Dict[str, Tuple[float, float]] = {}
        
        # Pesos para la función de fitness
        self.fitness_weights: Dict[str, float] = {
            "cost": 1.0,         # Minimizar costo
            "nutrition": 1.0,    # Optimizar nutrición
            "texture": 1.0,      # Optimizar textura
            "constraints": 5.0   # Penalización por violar restricciones
        }
        
        # Funciones de fitness personalizadas
        self.custom_fitness_functions: List[Tuple[Callable[[Recipe], float], float]] = []
    
    def set_ingredient_constraints(self, ingredient_name: str, min_amount: float, max_amount: float) -> None:
        """
        Establece restricciones de cantidad para un ingrediente.
        
        Args:
            ingredient_name: Nombre del ingrediente
            min_amount: Cantidad mínima permitida (gramos)
            max_amount: Cantidad máxima permitida (gramos)
        """
        self.ingredient_constraints[ingredient_name] = (min_amount, max_amount)
    
    def clear_ingredient_constraints(self) -> None:
        """
        Elimina todas las restricciones de ingredientes.
        """
        self.ingredient_constraints = {}
    
    def add_custom_fitness_function(self, function: Callable[[Recipe], float], weight: float = 1.0) -> None:
        """
        Añade una función de fitness personalizada.
        
        Args:
            function: Función que toma una receta y devuelve un valor numérico
            weight: Peso de esta función en el fitness total
        """
        self.custom_fitness_functions.append((function, weight))
    
    def clear_custom_fitness_functions(self) -> None:
        """
        Elimina todas las funciones de fitness personalizadas.
        """
        self.custom_fitness_functions = []
    
    def set_fitness_weight(self, criterion: str, weight: float) -> None:
        """
        Establece el peso para un criterio de fitness.
        
        Args:
            criterion: Nombre del criterio ('cost', 'nutrition', 'texture', 'constraints')
            weight: Peso a asignar
        """
        if criterion in self.fitness_weights:
            self.fitness_weights[criterion] = weight
        else:
            raise ValueError(f"Criterio de fitness desconocido: {criterion}")
    
    def _create_initial_population(self, template_recipe: Recipe) -> List[Recipe]:
        """
        Crea la población inicial de recetas basada en una plantilla.
        
        Args:
            template_recipe: Receta base para la población
            
        Returns:
            Lista de recetas que forman la población inicial
        """
        population = []
        
        # La primera receta es la plantilla original
        population.append(copy.deepcopy(template_recipe))
        
        # Crear el resto de la población con variaciones
        for _ in range(self.population_size - 1):
            new_recipe = copy.deepcopy(template_recipe)
            
            # Variar las cantidades de los ingredientes
            for ingredient in new_recipe.ingredients:
                # Variación aleatoria entre 70% y 130% de la cantidad original
                variation = random.uniform(0.7, 1.3)
                ingredient.amount *= variation
                
                # Aplicar restricciones si existen
                if ingredient.name in self.ingredient_constraints:
                    min_val, max_val = self.ingredient_constraints[ingredient.name]
                    ingredient.amount = max(min_val, min(max_val, ingredient.amount))
            
            population.append(new_recipe)
            
        return population
    
    def _calculate_fitness(self, recipe: Recipe) -> float:
        """
        Calcula el valor de fitness para una receta.
        
        Un valor más alto indica una mejor receta.
        
        Args:
            recipe: Receta a evaluar
            
        Returns:
            Valor de fitness
        """
        fitness = 0.0
        
        # 1. Evaluación de costo (menor es mejor)
        cost = 0.0
        for ingredient in recipe.ingredients:
            ingredient_cost = ingredient.properties.get("cost_per_gram", 0.0)
            cost += ingredient_cost * ingredient.amount
        
        # Normalizar costo (inverso para que menor costo sea mejor fitness)
        if cost > 0:
            cost_fitness = 1.0 / cost
        else:
            cost_fitness = 1.0
        
        fitness += cost_fitness * self.fitness_weights["cost"]
        
        # 2. Evaluación nutricional
        nutritional_fitness = 0.0
        target_nutrition = recipe.properties.get("target_nutrition", {})
        
        if target_nutrition:
            actual_nutrition = recipe.get_nutritional_summary()
            nutrition_score = 0.0
            
            for nutrient, target in target_nutrition.items():
                if nutrient in actual_nutrition:
                    # Calcular qué tan cerca estamos del objetivo
                    actual = actual_nutrition[nutrient]
                    if target > 0:
                        ratio = actual / target
                        # Penalizar tanto exceso como defecto
                        score = 1.0 - min(abs(1.0 - ratio), 1.0)
                        nutrition_score += score
            
            if target_nutrition:
                nutritional_fitness = nutrition_score / len(target_nutrition)
        
        fitness += nutritional_fitness * self.fitness_weights["nutrition"]
        
        # 3. Evaluación de textura y propiedades físicas
        texture_fitness = 0.0
        target_texture = recipe.properties.get("target_texture", {})
        
        if target_texture:
            # Calcular propiedades actuales basadas en ingredientes
            # Este es un cálculo simplificado y debería ser más complejo en un sistema real
            actual_texture = {}
            for ingredient in recipe.ingredients:
                ingredient_texture = ingredient.properties.get("texture", {})
                for property_name, value in ingredient_texture.items():
                    if property_name in actual_texture:
                        actual_texture[property_name] += value * (ingredient.amount / recipe.get_total_weight())
                    else:
                        actual_texture[property_name] = value * (ingredient.amount / recipe.get_total_weight())
            
            texture_score = 0.0
            for property_name, target in target_texture.items():
                if property_name in actual_texture:
                    actual = actual_texture[property_name]
                    if target > 0:
                        ratio = actual / target
                        score = 1.0 - min(abs(1.0 - ratio), 1.0)
                        texture_score += score
            
            if target_texture:
                texture_fitness = texture_score / len(target_texture)
        
        fitness += texture_fitness * self.fitness_weights["texture"]
        
        # 4. Verificación de restricciones
        constraints_penalty = 0.0
        
        # Verificar restricciones de ingredientes
        for ingredient in recipe.ingredients:
            if ingredient.name in self.ingredient_constraints:
                min_val, max_val = self.ingredient_constraints[ingredient.name]
                if ingredient.amount < min_val:
                    # Penalizar proporcionalmente a cuánto se viola la restricción
                    violation = (min_val - ingredient.amount) / min_val
                    constraints_penalty += violation
                elif ingredient.amount > max_val:
                    violation = (ingredient.amount - max_val) / max_val
                    constraints_penalty += violation
        
        # Aplicar penalización por restricciones
        fitness -= constraints_penalty * self.fitness_weights["constraints"]
        
        # 5. Funciones de fitness personalizadas
        for func, weight in self.custom_fitness_functions:
            try:
                custom_value = func(recipe)
                fitness += custom_value * weight
            except Exception as e:
                # Ignorar errores en funciones personalizadas
                print(f"Error al evaluar función de fitness personalizada: {e}")
        
        return max(0.0, fitness)  # Asegurar que el fitness no sea negativo
    
    def _select_parents(self, population: List[Recipe], fitness_values: List[float]) -> Tuple[Recipe, Recipe]:
        """
        Selecciona dos padres para reproducción usando selección por torneo.
        
        Args:
            population: Lista de recetas candidatas
            fitness_values: Lista de valores de fitness correspondientes
            
        Returns:
            Tupla con dos recetas seleccionadas como padres
        """
        def select_one():
            # Selección por torneo: escoge k individuos al azar y selecciona el mejor
            k = 3  # Tamaño del torneo
            competitors = random.sample(range(len(population)), k)
            winner_idx = max(competitors, key=lambda i: fitness_values[i])
            return population[winner_idx]
        
        return select_one(), select_one()
    
    def _crossover(self, parent1: Recipe, parent2: Recipe) -> Tuple[Recipe, Recipe]:
        """
        Realiza el cruce entre dos recetas para crear dos hijos.
        
        Args:
            parent1: Primera receta padre
            parent2: Segunda receta padre
            
        Returns:
            Tupla con dos recetas hijas
        """
        # Decidir si se realiza el cruce
        if random.random() > self.crossover_rate:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # Obtener listas de nombres de ingredientes
        ingredients1 = {ing.name: i for i, ing in enumerate(child1.ingredients)}
        ingredients2 = {ing.name: i for i, ing in enumerate(child2.ingredients)}
        
        # Encontrar ingredientes comunes
        common_ingredients = set(ingredients1.keys()) & set(ingredients2.keys())
        
        # Realizar cruce sólo en los ingredientes comunes
        for ing_name in common_ingredients:
            # Punto de cruce: mezclar cantidades
            alpha = random.random()  # Factor de mezcla
            
            idx1 = ingredients1[ing_name]
            idx2 = ingredients2[ing_name]
            
            amount1 = child1.ingredients[idx1].amount
            amount2 = child2.ingredients[idx2].amount
            
            # Cruce aritmético: crear nuevas cantidades como combinación lineal
            new_amount1 = alpha * amount1 + (1 - alpha) * amount2
            new_amount2 = (1 - alpha) * amount1 + alpha * amount2
            
            child1.ingredients[idx1].amount = new_amount1
            child2.ingredients[idx2].amount = new_amount2
            
            # Aplicar restricciones si existen
            if ing_name in self.ingredient_constraints:
                min_val, max_val = self.ingredient_constraints[ing_name]
                child1.ingredients[idx1].amount = max(min_val, min(max_val, child1.ingredients[idx1].amount))
                child2.ingredients[idx2].amount = max(min_val, min(max_val, child2.ingredients[idx2].amount))
        
        return child1, child2
    
    def _mutate(self, recipe: Recipe) -> None:
        """
        Aplica mutación a una receta modificando las cantidades de ingredientes.
        
        Args:
            recipe: Receta a mutar
        """
        for ingredient in recipe.ingredients:
            # Decidir si este ingrediente muta
            if random.random() < self.mutation_rate:
                # Aplicar mutación gaussiana
                mutation_factor = random.gauss(1.0, 0.1)  # Media 1.0, desviación 0.1
                ingredient.amount *= mutation_factor
                
                # Evitar valores negativos
                ingredient.amount = max(0.1, ingredient.amount)
                
                # Aplicar restricciones si existen
                if ingredient.name in self.ingredient_constraints:
                    min_val, max_val = self.ingredient_constraints[ingredient.name]
                    ingredient.amount = max(min_val, min(max_val, ingredient.amount))
    
    def optimize(self, template_recipe: Recipe, callback: Optional[Callable[[int, Recipe, float], None]] = None) -> Recipe:
        """
        Optimiza una receta utilizando algoritmos genéticos.
        
        Args:
            template_recipe: Receta base a optimizar
            callback: Función opcional para recibir actualizaciones en cada generación
            
        Returns:
            La mejor receta encontrada
        """
        # Crear población inicial
        population = self._create_initial_population(template_recipe)
        
        best_recipe = None
        best_fitness = -math.inf
        
        # Iterar por el número de generaciones
        for generation in range(self.generations):
            # Calcular fitness para toda la población
            fitness_values = [self._calculate_fitness(recipe) for recipe in population]
            
            # Encontrar el mejor individuo
            current_best_idx = max(range(len(fitness_values)), key=lambda i: fitness_values[i])
            current_best_recipe = population[current_best_idx]
            current_best_fitness = fitness_values[current_best_idx]
            
            # Actualizar el mejor global si es necesario
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_recipe = copy.deepcopy(current_best_recipe)
            
            # Llamar al callback si está definido
            if callback:
                callback(generation, current_best_recipe, current_best_fitness)
            
            # Terminar si hemos alcanzado la última generación
            if generation == self.generations - 1:
                break
            
            # Crear nueva población
            new_population = []
            
            # Elitismo: copiar los mejores individuos directamente
            elite_indices = sorted(range(len(fitness_values)), key=lambda i: fitness_values[i], reverse=True)[:self.elitism]
            for idx in elite_indices:
                new_population.append(copy.deepcopy(population[idx]))
            
            # Llenar el resto de la población con descendencia
            while len(new_population) < self.population_size:
                # Seleccionar padres
                parent1, parent2 = self._select_parents(population, fitness_values)
                
                # Realizar cruce
                child1, child2 = self._crossover(parent1, parent2)
                
                # Aplicar mutación
                self._mutate(child1)
                self._mutate(child2)
                
                # Añadir hijos a la nueva población
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            # Reemplazar población anterior
            population = new_population
        
        # Devolver la mejor receta encontrada
        return best_recipe
    
    def optimize_batch(
        self, 
        template_recipe: Recipe, 
        runs: int = 3,
        callback: Optional[Callable[[int, int, Recipe, float], None]] = None
    ) -> Recipe:
        """
        Ejecuta varias optimizaciones y devuelve el mejor resultado.
        
        Args:
            template_recipe: Receta base a optimizar
            runs: Número de ejecuciones independientes
            callback: Función opcional para recibir actualizaciones
            
        Returns:
            La mejor receta encontrada de todas las ejecuciones
        """
        best_recipe = None
        best_fitness = -math.inf
        
        for run in range(runs):
            # Callback específico para esta ejecución
            def run_callback(generation, recipe, fitness):
                if callback:
                    callback(run, generation, recipe, fitness)
            
            # Ejecutar optimización
            result = self.optimize(template_recipe, run_callback)
            
            # Calcular fitness del resultado
            fitness = self._calculate_fitness(result)
            
            # Actualizar mejor global si es necesario
            if fitness > best_fitness:
                best_fitness = fitness
                best_recipe = copy.deepcopy(result)
        
        return best_recipe 