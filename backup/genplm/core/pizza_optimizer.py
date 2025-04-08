"""
Optimizador específico para recetas de masa de pizza.

Este módulo proporciona funcionalidades para optimizar recetas de masa de pizza
utilizando algoritmos genéticos. Configura los parámetros y restricciones específicas
para el dominio de las masas de pizza.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union

from genplm.core.genetic_optimizer import GeneticOptimizer, Individual
from genplm.core.recipe_model import Recipe, Ingredient
from genplm.validation.validation_system import ValidationSystem

# Configuración de logging
logger = logging.getLogger('genplm.pizza_optimizer')

class PizzaOptimizer:
    """
    Optimizador específico para recetas de masa de pizza.
    
    Utiliza un algoritmo genético para encontrar la combinación óptima de ingredientes
    que maximice las propiedades deseadas (elasticidad, sabor, textura, etc.) mientras
    cumple con las restricciones de producción y calidad.
    """
    
    def __init__(
        self, 
        base_recipe: Recipe,
        ingredient_ranges: Dict[str, Tuple[float, float]],
        optional_ingredients: Optional[Dict[str, Tuple[float, float]]] = None,
        fixed_ingredients: Optional[Dict[str, float]] = None,
        target_weight: Optional[float] = None,
        validation_system: Optional[ValidationSystem] = None,
        population_size: int = 100,
        max_generations: int = 50,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        elite_size: int = 5
    ):
        """
        Inicializa el optimizador de masa de pizza.
        
        Args:
            base_recipe: Receta base que sirve como punto de partida
            ingredient_ranges: Diccionario con los rangos permitidos para cada ingrediente (min, max)
            optional_ingredients: Ingredientes opcionales con sus rangos permitidos
            fixed_ingredients: Ingredientes con cantidades fijas que no variarán
            target_weight: Peso objetivo de la masa final
            validation_system: Sistema de validación para verificar las recetas
            population_size: Tamaño de la población para el algoritmo genético
            max_generations: Número máximo de generaciones
            mutation_rate: Tasa de mutación para el algoritmo genético
            crossover_rate: Tasa de cruce para el algoritmo genético
            elite_size: Número de mejores individuos que pasan directamente
        """
        self.base_recipe = base_recipe
        self.ingredient_ranges = ingredient_ranges
        self.optional_ingredients = optional_ingredients or {}
        self.fixed_ingredients = fixed_ingredients or {}
        self.target_weight = target_weight
        self.validation_system = validation_system
        
        # Parámetros del algoritmo genético
        self.population_size = population_size
        self.max_generations = max_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        
        # Pesos para la función de aptitud
        self.fitness_weights = {
            'validation': 5.0,    # Peso para las validaciones
            'consistency': 3.0,   # Peso para la consistencia de la masa
            'elasticity': 2.0,    # Peso para la elasticidad
            'flavor': 1.5,        # Peso para el sabor
            'nutrition': 1.0,     # Peso para el valor nutricional
            'cost': 2.0           # Peso para el costo
        }
        
        # Preparar el optimizador genético
        self._setup_genetic_optimizer()
        
        logger.info(f"Optimizador de pizza inicializado con {len(ingredient_ranges)} ingredientes variables")
        if optional_ingredients:
            logger.info(f"Ingredientes opcionales: {len(optional_ingredients)}")
        if fixed_ingredients:
            logger.info(f"Ingredientes fijos: {len(fixed_ingredients)}")
        if target_weight:
            logger.info(f"Peso objetivo: {target_weight}g")
    
    def _setup_genetic_optimizer(self):
        """Configura el optimizador genético con los parámetros adecuados."""
        # Construir el espacio de búsqueda para el optimizador genético
        gene_ranges = {}
        
        # Agregar ingredientes variables
        for ingredient_name, (min_val, max_val) in self.ingredient_ranges.items():
            gene_ranges[ingredient_name] = (min_val, max_val)
        
        # Agregar ingredientes opcionales
        for ingredient_name, (min_val, max_val) in self.optional_ingredients.items():
            # Para ingredientes opcionales, añadimos un gen booleano para activar/desactivar
            gene_ranges[f"{ingredient_name}_active"] = [True, False]
            gene_ranges[ingredient_name] = (min_val, max_val)
        
        # Crear el optimizador
        self.optimizer = GeneticOptimizer(
            gene_ranges=gene_ranges,
            fitness_function=self._evaluate_recipe,
            population_size=self.population_size,
            mutation_rate=self.mutation_rate,
            crossover_rate=self.crossover_rate,
            elite_size=self.elite_size,
            maximize=True  # Queremos maximizar la puntuación
        )
    
    def _create_recipe_from_genes(self, genes: Dict[str, Any]) -> Recipe:
        """
        Crea una receta a partir de los genes de un individuo.
        
        Args:
            genes: Diccionario con los valores de los genes del individuo
        
        Returns:
            Receta completa con todos los ingredientes
        """
        # Crear una nueva receta basada en la receta base
        recipe = Recipe(name=self.base_recipe.name)
        
        # Añadir ingredientes fijos
        for ingredient_name, amount in self.fixed_ingredients.items():
            ingredient = Ingredient(name=ingredient_name, amount=amount)
            recipe.add_ingredient(ingredient)
        
        # Añadir ingredientes variables
        for ingredient_name, (min_val, max_val) in self.ingredient_ranges.items():
            amount = genes[ingredient_name]
            ingredient = Ingredient(name=ingredient_name, amount=amount)
            recipe.add_ingredient(ingredient)
        
        # Añadir ingredientes opcionales (si están activos)
        for ingredient_name in self.optional_ingredients:
            active_key = f"{ingredient_name}_active"
            if active_key in genes and genes[active_key]:
                amount = genes[ingredient_name]
                ingredient = Ingredient(name=ingredient_name, amount=amount)
                recipe.add_ingredient(ingredient)
        
        return recipe
    
    def _evaluate_recipe(self, genes: Dict[str, Any]) -> float:
        """
        Evalúa la aptitud de una receta basada en los genes.
        
        Args:
            genes: Diccionario con los valores de los genes del individuo
        
        Returns:
            Puntuación de aptitud de la receta
        """
        # Crear la receta a partir de los genes
        recipe = self._create_recipe_from_genes(genes)
        
        # Calcular el peso total de la receta
        total_weight = sum(ingredient.amount for ingredient in recipe.ingredients)
        
        # Inicializar la puntuación de aptitud
        fitness_score = 0.0
        
        # Aplicar validaciones si existe el sistema de validación
        validation_score = 0.0
        if self.validation_system:
            validation_results = self.validation_system.validate_recipe(recipe)
            
            # Calcular puntuación basada en validaciones
            num_validations = len(validation_results)
            if num_validations > 0:
                passed_validations = sum(1 for result in validation_results.values() if result.passed)
                validation_score = passed_validations / num_validations
            
        # Calcular penalización de peso si hay un objetivo de peso
        weight_penalty = 0.0
        if self.target_weight:
            weight_diff_percent = abs(total_weight - self.target_weight) / self.target_weight
            weight_penalty = min(1.0, weight_diff_percent)  # Limitar a 1.0 máximo
        
        # Calcular factores de calidad simulados
        # En una implementación real, estos se obtendrían de modelos predictivos
        # basados en la composición de ingredientes
        
        # Simular consistencia (mayor proporción de harina y menor de líquidos = mayor consistencia)
        consistency = self._calculate_consistency(recipe)
        
        # Simular elasticidad (cantidad de gluten y proporción agua/harina)
        elasticity = self._calculate_elasticity(recipe)
        
        # Simular sabor (presencia de ingredientes de sabor, como sal, azúcar, aceite)
        flavor = self._calculate_flavor(recipe)
        
        # Simular valor nutricional (diversidad de ingredientes, presencia de integrales)
        nutrition = self._calculate_nutrition(recipe)
        
        # Simular costo (basado en cantidades y tipo de ingredientes)
        cost_factor = self._calculate_cost(recipe)
        
        # Combinar los diferentes factores con sus pesos respectivos
        fitness_score = (
            self.fitness_weights['validation'] * validation_score +
            self.fitness_weights['consistency'] * consistency +
            self.fitness_weights['elasticity'] * elasticity +
            self.fitness_weights['flavor'] * flavor +
            self.fitness_weights['nutrition'] * nutrition -
            self.fitness_weights['cost'] * cost_factor -  # El costo afecta negativamente
            weight_penalty * 2.0  # Penalización por desviación del peso objetivo
        )
        
        return max(0.0, fitness_score)  # Asegurar que no sea negativo
    
    def _calculate_consistency(self, recipe: Recipe) -> float:
        """
        Calcula un factor de consistencia para la masa.
        
        Args:
            recipe: Receta a evaluar
        
        Returns:
            Factor de consistencia entre 0.0 y 1.0
        """
        # Simplificación: mayor proporción de harina y menor de líquidos = mayor consistencia
        flour_amount = sum(i.amount for i in recipe.ingredients if 'harina' in i.name.lower())
        water_amount = sum(i.amount for i in recipe.ingredients if 'agua' in i.name.lower())
        oil_amount = sum(i.amount for i in recipe.ingredients if 'aceite' in i.name.lower())
        
        # Calcular proporción agua/harina (hidratación)
        if flour_amount == 0:
            return 0.0
        
        hydration = water_amount / flour_amount
        oil_ratio = oil_amount / flour_amount if flour_amount > 0 else 0
        
        # Hidratación óptima alrededor de 0.6-0.65 para pizza
        optimal_hydration = 0.625
        hydration_score = 1.0 - min(1.0, abs(hydration - optimal_hydration) / 0.3)
        
        # Proporción de aceite óptima 0.02-0.05
        optimal_oil_ratio = 0.035
        oil_score = 1.0 - min(1.0, abs(oil_ratio - optimal_oil_ratio) / 0.05)
        
        # Combinar factores
        consistency = 0.7 * hydration_score + 0.3 * oil_score
        
        return consistency
    
    def _calculate_elasticity(self, recipe: Recipe) -> float:
        """
        Calcula un factor de elasticidad para la masa.
        
        Args:
            recipe: Receta a evaluar
        
        Returns:
            Factor de elasticidad entre 0.0 y 1.0
        """
        # Simplificación: la elasticidad depende del gluten y hidratación
        flour_amount = sum(i.amount for i in recipe.ingredients if 'harina' in i.name.lower())
        water_amount = sum(i.amount for i in recipe.ingredients if 'agua' in i.name.lower())
        
        # Detectar harinas con alto contenido de gluten
        high_gluten_flour = sum(i.amount for i in recipe.ingredients if 'fuerza' in i.name.lower())
        
        # Calcular proporción agua/harina (hidratación)
        if flour_amount == 0:
            return 0.0
        
        hydration = water_amount / flour_amount
        gluten_ratio = high_gluten_flour / flour_amount if flour_amount > 0 else 0
        
        # Hidratación óptima para elasticidad 0.65-0.75
        optimal_hydration = 0.7
        hydration_score = 1.0 - min(1.0, abs(hydration - optimal_hydration) / 0.3)
        
        # Factor de harina de fuerza
        gluten_score = 0.5 + 0.5 * gluten_ratio
        
        # Combinar factores
        elasticity = 0.6 * hydration_score + 0.4 * gluten_score
        
        return elasticity
    
    def _calculate_flavor(self, recipe: Recipe) -> float:
        """
        Calcula un factor de sabor para la masa.
        
        Args:
            recipe: Receta a evaluar
        
        Returns:
            Factor de sabor entre 0.0 y 1.0
        """
        # Simplificación: el sabor depende de sal, azúcar, aceite y otros potenciadores
        flour_amount = sum(i.amount for i in recipe.ingredients if 'harina' in i.name.lower())
        if flour_amount == 0:
            return 0.0
        
        # Calcular proporciones relativas a la harina
        salt_ratio = sum(i.amount for i in recipe.ingredients if 'sal' in i.name.lower()) / flour_amount
        sugar_ratio = sum(i.amount for i in recipe.ingredients if 'azúcar' in i.name.lower()) / flour_amount
        oil_ratio = sum(i.amount for i in recipe.ingredients if 'aceite' in i.name.lower()) / flour_amount
        
        # Presencia de potenciadores de sabor
        enhancers = any(
            ingredient.name.lower() in ['ajo', 'cebolla', 'orégano', 'tomillo', 'romero']
            for ingredient in recipe.ingredients
        )
        
        # Proporciones óptimas
        optimal_salt_ratio = 0.02  # 2% de la harina
        optimal_sugar_ratio = 0.01  # 1% de la harina
        optimal_oil_ratio = 0.03   # 3% de la harina
        
        # Calcular puntuaciones
        salt_score = 1.0 - min(1.0, abs(salt_ratio - optimal_salt_ratio) / 0.03)
        sugar_score = 1.0 - min(1.0, abs(sugar_ratio - optimal_sugar_ratio) / 0.02)
        oil_score = 1.0 - min(1.0, abs(oil_ratio - optimal_oil_ratio) / 0.05)
        enhancer_score = 0.1 if enhancers else 0.0
        
        # Combinar factores
        flavor = 0.4 * salt_score + 0.2 * sugar_score + 0.3 * oil_score + enhancer_score
        
        return flavor
    
    def _calculate_nutrition(self, recipe: Recipe) -> float:
        """
        Calcula un factor de valor nutricional para la masa.
        
        Args:
            recipe: Receta a evaluar
        
        Returns:
            Factor de nutrición entre 0.0 y 1.0
        """
        # Simplificación: mayor presencia de ingredientes integrales y variedad = mayor valor nutricional
        flour_amount = sum(i.amount for i in recipe.ingredients if 'harina' in i.name.lower())
        if flour_amount == 0:
            return 0.0
        
        # Calcular proporción de harinas integrales
        whole_grain = sum(i.amount for i in recipe.ingredients if 'integral' in i.name.lower())
        whole_grain_ratio = whole_grain / flour_amount
        
        # Verificar presencia de ingredientes nutricionales
        nutritional_ingredients = [
            'semillas', 'lino', 'chía', 'avena', 'salvado', 'centeno', 'quinoa'
        ]
        
        nutritional_count = sum(
            1 for ingredient in recipe.ingredients
            if any(item in ingredient.name.lower() for item in nutritional_ingredients)
        )
        
        # Calcular diversidad de ingredientes
        diversity = min(1.0, len(recipe.ingredients) / 10)
        
        # Combinar factores
        nutrition = 0.5 * whole_grain_ratio + 0.3 * min(1.0, nutritional_count / 3) + 0.2 * diversity
        
        return nutrition
    
    def _calculate_cost(self, recipe: Recipe) -> float:
        """
        Calcula un factor de costo para la masa.
        
        Args:
            recipe: Receta a evaluar
        
        Returns:
            Factor de costo entre 0.0 y 1.0 (mayor valor = mayor costo)
        """
        # Valores relativos de costo (simulados)
        ingredient_costs = {
            'harina': 1.0,
            'agua': 0.1,
            'sal': 0.5,
            'azúcar': 1.2,
            'aceite': 3.0,
            'levadura': 8.0,
            'integral': 1.5,  # Harina integral
            'fuerza': 1.3,    # Harina de fuerza
            'semilla': 5.0,
            'chía': 10.0,
            'lino': 7.0,
            'centeno': 2.0,
            'quinoa': 12.0
        }
        
        total_cost = 0.0
        total_weight = 0.0
        
        for ingredient in recipe.ingredients:
            # Calcular el costo del ingrediente
            ingredient_cost = 1.0  # Costo base
            for name, cost in ingredient_costs.items():
                if name in ingredient.name.lower():
                    ingredient_cost = max(ingredient_cost, cost)
                    break
            
            total_cost += ingredient.amount * ingredient_cost
            total_weight += ingredient.amount
        
        # Normalizar el costo (1.0 = muy caro, 0.0 = muy barato)
        if total_weight == 0:
            return 0.5
        
        # El costo promedio de referencia es 1.5
        avg_cost = total_cost / total_weight
        normalized_cost = min(1.0, avg_cost / 3.0)
        
        return normalized_cost
    
    def optimize(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Ejecuta el proceso de optimización para encontrar la mejor receta.
        
        Args:
            verbose: Si es True, muestra información durante la optimización
        
        Returns:
            Diccionario con los resultados de la optimización
        """
        logger.info("Iniciando optimización de receta de pizza")
        
        # Inicializar población
        self.optimizer.initialize_population()
        
        # Ejecutar optimización
        results = self.optimizer.optimize(
            max_generations=self.max_generations,
            verbose=verbose
        )
        
        # Crear la receta final a partir del mejor individuo
        best_genes = results["best_individual"].genes
        best_recipe = self._create_recipe_from_genes(best_genes)
        
        # Añadir información adicional a los resultados
        results["best_recipe"] = best_recipe
        
        # Calcular validaciones para la mejor receta
        if self.validation_system:
            validation_results = self.validation_system.validate_recipe(best_recipe)
            results["validation_results"] = validation_results
        
        # Calcular métricas de calidad para la mejor receta
        quality_metrics = {
            "consistency": self._calculate_consistency(best_recipe),
            "elasticity": self._calculate_elasticity(best_recipe),
            "flavor": self._calculate_flavor(best_recipe),
            "nutrition": self._calculate_nutrition(best_recipe),
            "cost": self._calculate_cost(best_recipe)
        }
        results["quality_metrics"] = quality_metrics
        
        # Mostrar resultados
        if verbose:
            logger.info(f"Optimización completada: fitness = {results['best_fitness']:.4f}")
            logger.info(f"Mejor receta: {best_recipe.name}")
            
            for ingredient in best_recipe.ingredients:
                logger.info(f"  {ingredient.name}: {ingredient.amount:.2f}g")
            
            logger.info("Métricas de calidad:")
            for metric, value in quality_metrics.items():
                logger.info(f"  {metric}: {value:.4f}")
        
        return results 