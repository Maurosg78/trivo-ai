"""
Optimizador de recetas de masa de pizza usando algoritmos genéticos.

Este módulo extiende el optimizador genético general para aplicarlo
específicamente a la formulación de masas de pizza, considerando
restricciones y objetivos específicos de este dominio.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field

from genplm.core.genetic_optimizer import GeneticOptimizer, Individual
from genplm.dough.recipe import Recipe, Ingredient, ProductionScale
from genplm.validation.validator import RecipeValidator

# Configuración de logging
logger = logging.getLogger('genplm.recipe_optimizer')

@dataclass
class OptimizationGoal:
    """
    Define un objetivo de optimización para una receta.
    
    Attributes:
        name: Nombre del objetivo
        weight: Peso relativo del objetivo (0-1)
        target_value: Valor objetivo a alcanzar (si aplica)
        minimize: Si es True, se busca minimizar este objetivo
    """
    name: str
    weight: float = 1.0
    target_value: Optional[float] = None
    minimize: bool = False
    
    def __post_init__(self):
        """Validación después de la inicialización."""
        if not 0 <= self.weight <= 1:
            raise ValueError(f"El peso del objetivo {self.name} debe estar entre 0 y 1")

@dataclass
class RecipeOptimizationConfig:
    """
    Configuración para la optimización de recetas.
    
    Attributes:
        production_scale: Escala de producción objetivo
        base_recipe: Receta base a optimizar (opcional)
        fixed_ingredients: Ingredientes que no deben modificarse
        required_ingredients: Ingredientes que deben estar presentes
        optional_ingredients: Ingredientes opcionales que pueden incluirse
        forbidden_ingredients: Ingredientes que no deben incluirse
        goals: Objetivos de optimización
        constraints: Restricciones adicionales
    """
    production_scale: ProductionScale
    base_recipe: Optional[Recipe] = None
    fixed_ingredients: List[str] = field(default_factory=list)
    required_ingredients: List[str] = field(default_factory=list)
    optional_ingredients: List[str] = field(default_factory=list)
    forbidden_ingredients: List[str] = field(default_factory=list)
    goals: List[OptimizationGoal] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validación después de la inicialización."""
        # Verificar que no haya conflictos entre listas de ingredientes
        for ing in self.fixed_ingredients:
            if ing in self.forbidden_ingredients:
                raise ValueError(f"El ingrediente {ing} no puede estar en fixed_ingredients y forbidden_ingredients")
        
        for ing in self.required_ingredients:
            if ing in self.forbidden_ingredients:
                raise ValueError(f"El ingrediente {ing} no puede estar en required_ingredients y forbidden_ingredients")
        
        for ing in self.optional_ingredients:
            if ing in self.forbidden_ingredients:
                raise ValueError(f"El ingrediente {ing} no puede estar en optional_ingredients y forbidden_ingredients")
            if ing in self.required_ingredients:
                raise ValueError(f"El ingrediente {ing} no puede estar en optional_ingredients y required_ingredients")
        
        # Verificar que los pesos de los objetivos sumen 1
        total_weight = sum(goal.weight for goal in self.goals)
        if total_weight > 0 and abs(total_weight - 1.0) > 0.01:  # Permitir pequeño error de redondeo
            logger.warning(f"Los pesos de los objetivos suman {total_weight}, no 1.0. Serán normalizados.")
            for goal in self.goals:
                goal.weight /= total_weight

class RecipeOptimizer:
    """
    Optimizador de recetas de masa de pizza.
    
    Utiliza algoritmos genéticos para encontrar la mejor combinación de ingredientes
    y proporciones según los objetivos y restricciones especificados.
    """
    
    def __init__(
        self, 
        config: RecipeOptimizationConfig,
        validator: Optional[RecipeValidator] = None,
        population_size: int = 100,
        max_generations: int = 200,
        mutation_rate: float = 0.1,
        ingredient_library: Optional[Dict[str, Ingredient]] = None
    ):
        """
        Inicializa el optimizador de recetas.
        
        Args:
            config: Configuración de la optimización
            validator: Validador de recetas (opcional)
            population_size: Tamaño de la población genética
            max_generations: Número máximo de generaciones
            mutation_rate: Tasa de mutación genética
            ingredient_library: Biblioteca de ingredientes disponibles
        """
        self.config = config
        self.validator = validator
        self.population_size = population_size
        self.max_generations = max_generations
        self.mutation_rate = mutation_rate
        self.ingredient_library = ingredient_library or {}
        
        # Resolver ingredientes y establecer límites
        self._setup_ingredient_constraints()
        
        # Definir rangos para los genes
        self._gene_ranges = self._create_gene_ranges()
        
        # Inicializar optimizador genético
        self._optimizer = GeneticOptimizer(
            gene_ranges=self._gene_ranges,
            fitness_function=self._evaluate_recipe_fitness,
            population_size=population_size,
            mutation_rate=mutation_rate,
            crossover_rate=0.8,
            elite_size=int(population_size * 0.1),  # 10% de elitismo
            tournament_size=3,
            maximize=True
        )
        
        logger.info(f"Inicializado optimizador de recetas para escala {config.production_scale.name}")
        logger.info(f"Ingredientes posibles: {len(self._ingredient_pool)}")
        logger.info(f"Objetivos: {[g.name for g in config.goals]}")
        
    def _setup_ingredient_constraints(self):
        """Configura los ingredientes disponibles y sus límites."""
        # Inicializar conjunto de ingredientes utilizables
        self._ingredient_pool = set()
        
        # Añadir ingredientes requeridos
        self._ingredient_pool.update(self.config.required_ingredients)
        
        # Añadir ingredientes fijos
        if self.config.base_recipe:
            for ing in self.config.base_recipe.ingredients:
                if ing.name in self.config.fixed_ingredients:
                    self._ingredient_pool.add(ing.name)
        
        # Añadir ingredientes opcionales
        self._ingredient_pool.update(self.config.optional_ingredients)
        
        # Verificar que todos los ingredientes estén en la biblioteca
        missing_ingredients = [ing for ing in self._ingredient_pool if ing not in self.ingredient_library]
        if missing_ingredients:
            raise ValueError(f"Los siguientes ingredientes no están en la biblioteca: {missing_ingredients}")
        
        # Establecer límites por ingrediente
        self._ingredient_limits = {}
        
        for ing_name in self._ingredient_pool:
            ingredient = self.ingredient_library[ing_name]
            scale = self.config.production_scale
            
            # Determinar límites
            if scale == ProductionScale.SMALL:
                min_qty = ingredient.min_small_scale
                max_qty = ingredient.max_small_scale
            elif scale == ProductionScale.MEDIUM:
                min_qty = ingredient.min_medium_scale
                max_qty = ingredient.max_medium_scale
            else:  # LARGE
                min_qty = ingredient.min_large_scale
                max_qty = ingredient.max_large_scale
            
            # Si es un ingrediente fijo, usar la cantidad actual
            if self.config.base_recipe and ing_name in self.config.fixed_ingredients:
                for ing in self.config.base_recipe.ingredients:
                    if ing.name == ing_name:
                        min_qty = max_qty = ing.quantity
                        break
            
            self._ingredient_limits[ing_name] = (min_qty, max_qty)
    
    def _create_gene_ranges(self) -> Dict[str, Union[Tuple[float, float], List[bool]]]:
        """
        Crea los rangos para los genes del optimizador genético.
        
        Returns:
            Diccionario con los rangos para cada gen
        """
        gene_ranges = {}
        
        # Genes para la presencia o ausencia de ingredientes opcionales
        for ing_name in self.config.optional_ingredients:
            gene_ranges[f"use_{ing_name}"] = [True, False]
        
        # Genes para las cantidades de ingredientes
        for ing_name in self._ingredient_pool:
            # Si es un ingrediente opcional, la cantidad solo importa si está presente
            if ing_name in self.config.optional_ingredients:
                min_qty, max_qty = self._ingredient_limits[ing_name]
                gene_ranges[f"qty_{ing_name}"] = (min_qty, max_qty)
            # Si es requerido o fijo, siempre está presente
            else:
                min_qty, max_qty = self._ingredient_limits[ing_name]
                gene_ranges[f"qty_{ing_name}"] = (min_qty, max_qty)
        
        return gene_ranges
    
    def _genes_to_recipe(self, genes: Dict[str, Any]) -> Recipe:
        """
        Convierte un conjunto de genes en una receta.
        
        Args:
            genes: Genes que definen la receta
            
        Returns:
            Receta construida a partir de los genes
        """
        ingredients = []
        
        # Añadir ingredientes según los genes
        for ing_name in self._ingredient_pool:
            # Verificar si el ingrediente está activo (si es opcional)
            is_optional = ing_name in self.config.optional_ingredients
            is_active = not is_optional or genes[f"use_{ing_name}"]
            
            if is_active:
                quantity = genes[f"qty_{ing_name}"]
                ingredient = self.ingredient_library[ing_name]
                ingredients.append(Ingredient(
                    name=ing_name,
                    quantity=quantity,
                    unit=ingredient.unit,
                    category=ingredient.category
                ))
        
        # Crear receta
        return Recipe(
            name="Receta optimizada",
            ingredients=ingredients,
            production_scale=self.config.production_scale
        )
    
    def _evaluate_recipe_fitness(self, genes: Dict[str, Any]) -> float:
        """
        Calcula la aptitud de una receta definida por genes.
        
        Args:
            genes: Genes que definen la receta
            
        Returns:
            Valor de aptitud (mayor es mejor)
        """
        # Convertir genes a receta
        recipe = self._genes_to_recipe(genes)
        
        # Validar la receta si hay un validador
        validation_score = 1.0
        validation_results = None
        if self.validator:
            validation_results = self.validator.validate_recipe(recipe)
            
            # Penalizar por errores críticos
            critical_issues = sum(1 for r in validation_results if r.severity == "CRITICAL")
            if critical_issues > 0:
                validation_score = 0.1 / (1 + critical_issues)  # Penalización severa
            else:
                # Penalizar por advertencias
                warnings = sum(1 for r in validation_results if r.severity == "WARNING")
                validation_score = 1.0 / (1 + warnings * 0.2)  # Penalización más leve
        
        # Evaluar cada objetivo de optimización
        goal_scores = {}
        for goal in self.config.goals:
            goal_score = self._evaluate_goal(goal, recipe, validation_results)
            goal_scores[goal.name] = goal_score
        
        # Calcular puntuación ponderada
        weighted_score = 0
        for goal in self.config.goals:
            weighted_score += goal_scores[goal.name] * goal.weight
        
        # Ajustar por resultados de validación
        final_score = weighted_score * validation_score
        
        return final_score
    
    def _evaluate_goal(self, goal: OptimizationGoal, recipe: Recipe, 
                      validation_results: Optional[List[Any]] = None) -> float:
        """
        Evalúa el cumplimiento de un objetivo específico.
        
        Args:
            goal: Objetivo a evaluar
            recipe: Receta a evaluar
            validation_results: Resultados de validación (si están disponibles)
            
        Returns:
            Puntuación del objetivo (0-1, mayor es mejor)
        """
        # Diferentes tipos de objetivos
        if goal.name == "minimizar_costo":
            return self._evaluate_cost_goal(recipe, goal)
        elif goal.name == "balance_nutricional":
            return self._evaluate_nutritional_goal(recipe, goal)
        elif goal.name == "simplicidad":
            return self._evaluate_simplicity_goal(recipe, goal)
        elif goal.name == "sabor":
            return self._evaluate_flavor_goal(recipe, goal)
        elif goal.name == "textura":
            return self._evaluate_texture_goal(recipe, goal)
        elif goal.name == "similitud_base":
            return self._evaluate_similarity_goal(recipe, goal)
        else:
            logger.warning(f"Objetivo desconocido: {goal.name}")
            return 0.5  # Valor neutral por defecto
    
    def _evaluate_cost_goal(self, recipe: Recipe, goal: OptimizationGoal) -> float:
        """Evalúa el costo de la receta."""
        total_cost = 0.0
        for ing in recipe.ingredients:
            ingredient_info = self.ingredient_library[ing.name]
            cost_per_unit = ingredient_info.cost_per_unit
            total_cost += ing.quantity * cost_per_unit
        
        # Normalizar a una puntuación entre 0 y 1 (inversamente proporcional al costo)
        # Esto asume que conocemos un rango razonable de costos
        max_expected_cost = 100.0  # Ajustar según el contexto
        normalized_cost = max(0, 1 - (total_cost / max_expected_cost))
        
        return normalized_cost
    
    def _evaluate_nutritional_goal(self, recipe: Recipe, goal: OptimizationGoal) -> float:
        """Evalúa el balance nutricional de la receta."""
        # Calcular macronutrientes totales
        total_protein = 0.0
        total_fat = 0.0
        total_carbs = 0.0
        total_calories = 0.0
        
        for ing in recipe.ingredients:
            ingredient_info = self.ingredient_library[ing.name]
            
            # Sumar macronutrientes proporcionales a la cantidad
            total_protein += ing.quantity * ingredient_info.protein_per_100g / 100
            total_fat += ing.quantity * ingredient_info.fat_per_100g / 100
            total_carbs += ing.quantity * ingredient_info.carbs_per_100g / 100
            total_calories += ing.quantity * ingredient_info.calories_per_100g / 100
        
        # Calcular proporciones
        total_macros = total_protein + total_fat + total_carbs
        if total_macros == 0:
            return 0.0  # Evitar división por cero
        
        protein_ratio = total_protein / total_macros
        fat_ratio = total_fat / total_macros
        carbs_ratio = total_carbs / total_macros
        
        # Ideales para masa de pizza (ajustar según necesidades específicas)
        ideal_protein = 0.15  # 15% de proteínas
        ideal_fat = 0.25     # 25% de grasas
        ideal_carbs = 0.60    # 60% de carbohidratos
        
        # Calcular desviación de los ideales
        protein_deviation = abs(protein_ratio - ideal_protein)
        fat_deviation = abs(fat_ratio - ideal_fat)
        carbs_deviation = abs(carbs_ratio - ideal_carbs)
        
        # Puntuación basada en la cercanía a los ideales
        # 1.0 significa perfecta correspondencia, 0.0 significa máxima desviación
        max_possible_deviation = 2.0  # La suma máxima de desviaciones
        total_deviation = protein_deviation + fat_deviation + carbs_deviation
        
        return max(0, 1 - (total_deviation / max_possible_deviation))
    
    def _evaluate_simplicity_goal(self, recipe: Recipe, goal: OptimizationGoal) -> float:
        """Evalúa la simplicidad de la receta."""
        # Una forma simple de medir simplicidad es por el número de ingredientes
        num_ingredients = len(recipe.ingredients)
        
        # Penalizar recetas con muchos ingredientes
        max_ingredients = 15  # Ajustar según el contexto
        min_ingredients = 4   # Receta mínima viable
        
        if num_ingredients < min_ingredients:
            return 0.5  # Penalización por tener muy pocos ingredientes
        
        if num_ingredients > max_ingredients:
            return 0.0  # Máxima penalización
        
        # Normalizar a una puntuación entre 0.5 y 1.0
        # (permitiendo que recetas simples tengan buena puntuación)
        return 1.0 - 0.5 * (num_ingredients - min_ingredients) / (max_ingredients - min_ingredients)
    
    def _evaluate_flavor_goal(self, recipe: Recipe, goal: OptimizationGoal) -> float:
        """Evalúa el perfil de sabor de la receta."""
        # Esta es una implementación simplificada
        # En un sistema real, esto podría ser mucho más complejo
        
        # Contar ingredientes por categorías de sabor
        flavor_categories = {
            "salado": 0,
            "umami": 0,
            "dulce": 0,
            "ácido": 0,
            "amargo": 0,
            "neutro": 0
        }
        
        total_weight = 0
        
        for ing in recipe.ingredients:
            ingredient_info = self.ingredient_library[ing.name]
            
            # Sumar la contribución de cada ingrediente a los sabores
            if hasattr(ingredient_info, "flavor_profile"):
                for flavor, intensity in ingredient_info.flavor_profile.items():
                    if flavor in flavor_categories:
                        flavor_categories[flavor] += ing.quantity * intensity
            
            total_weight += ing.quantity
        
        # Normalizar por peso total
        if total_weight > 0:
            for flavor in flavor_categories:
                flavor_categories[flavor] /= total_weight
        
        # Calcular balance de sabores
        # Para pizza, queremos un buen balance entre salado, umami y un toque de ácido
        # Esta es una simplificación y debe ajustarse según preferencias específicas
        salado_score = min(1.0, flavor_categories["salado"] / 0.3)  # Ideal ~30% salado
        umami_score = min(1.0, flavor_categories["umami"] / 0.2)   # Ideal ~20% umami
        acido_score = min(1.0, flavor_categories["ácido"] / 0.1)   # Ideal ~10% ácido
        
        # Penalizar exceso de amargor o dulzor
        bitter_penalty = max(0, 1 - flavor_categories["amargo"] * 5)  # Penalizar si > 20%
        sweet_penalty = max(0, 1 - flavor_categories["dulce"] * 2.5)  # Penalizar si > 40%
        
        # Ponderar los diferentes aspectos del sabor
        flavor_score = (salado_score * 0.4 + 
                       umami_score * 0.3 + 
                       acido_score * 0.1 +
                       bitter_penalty * 0.1 + 
                       sweet_penalty * 0.1)
        
        return flavor_score
    
    def _evaluate_texture_goal(self, recipe: Recipe, goal: OptimizationGoal) -> float:
        """Evalúa la textura esperada de la receta."""
        # Calcular proporciones de ingredientes clave para la textura
        total_flour = 0.0
        total_liquid = 0.0
        total_fat = 0.0
        total_weight = 0.0
        
        for ing in recipe.ingredients:
            ingredient_info = self.ingredient_library[ing.name]
            total_weight += ing.quantity
            
            # Sumar contribuciones según categoría
            if ingredient_info.category == "harina":
                total_flour += ing.quantity
            elif ingredient_info.category == "líquido":
                total_liquid += ing.quantity
            elif ingredient_info.category == "grasa":
                total_fat += ing.quantity
        
        # Evitar división por cero
        if total_weight == 0 or total_flour == 0:
            return 0.0
        
        # Calcular hidratación (ratio agua/harina)
        hydration = total_liquid / total_flour
        
        # Calcular ratio de grasa
        fat_ratio = total_fat / total_flour
        
        # Valores ideales para masa de pizza
        # Estos valores pueden ajustarse según el tipo específico de masa
        ideal_hydration = 0.65  # 65% hidratación
        ideal_fat_ratio = 0.05  # 5% grasa respecto a harina
        
        # Evaluar cercanía a los ideales
        hydration_score = 1.0 - min(1.0, abs(hydration - ideal_hydration) / 0.3)
        fat_score = 1.0 - min(1.0, abs(fat_ratio - ideal_fat_ratio) / 0.05)
        
        # Combinación ponderada
        texture_score = hydration_score * 0.7 + fat_score * 0.3
        
        return texture_score
    
    def _evaluate_similarity_goal(self, recipe: Recipe, goal: OptimizationGoal) -> float:
        """Evalúa la similitud con la receta base."""
        if not self.config.base_recipe:
            return 0.5  # Neutral si no hay receta base
        
        base_recipe = self.config.base_recipe
        
        # Comparar ingredientes y cantidades
        base_ingredients = {ing.name: ing.quantity for ing in base_recipe.ingredients}
        new_ingredients = {ing.name: ing.quantity for ing in recipe.ingredients}
        
        # Lista de todos los ingredientes en ambas recetas
        all_ingredients = set(base_ingredients.keys()) | set(new_ingredients.keys())
        
        # Calcular diferencias
        total_diff = 0.0
        max_possible_diff = 0.0
        
        for ing_name in all_ingredients:
            base_qty = base_ingredients.get(ing_name, 0.0)
            new_qty = new_ingredients.get(ing_name, 0.0)
            
            # Si el ingrediente es nuevo o se eliminó, diferencia máxima
            if base_qty == 0.0 or new_qty == 0.0:
                if ing_name in self.config.optional_ingredients:
                    total_diff += max(base_qty, new_qty) * 0.5  # Penalización menor para opcionales
                else:
                    total_diff += max(base_qty, new_qty)  # Penalización completa
            else:
                # Diferencia proporcional
                total_diff += abs(base_qty - new_qty)
            
            max_possible_diff += max(base_qty, new_qty)
        
        # Normalizar a puntuación entre 0 y 1
        if max_possible_diff == 0:
            return 1.0  # Evitar división por cero
        
        similarity = 1.0 - (total_diff / max_possible_diff)
        return similarity
    
    def optimize(self, verbose: bool = True) -> Tuple[Recipe, Dict[str, Any]]:
        """
        Ejecuta el proceso de optimización.
        
        Args:
            verbose: Si es True, muestra información durante la optimización
            
        Returns:
            Tupla con la mejor receta encontrada y un diccionario con estadísticas
        """
        # Ejecutar optimizador genético
        result = self._optimizer.optimize(
            max_generations=self.max_generations,
            verbose=verbose
        )
        
        # Convertir el mejor individuo a receta
        best_genes = result["best_individual"].genes
        best_recipe = self._genes_to_recipe(best_genes)
        
        # Calcular métricas finales
        metrics = {}
        validation_results = None
        
        if self.validator:
            validation_results = self.validator.validate_recipe(best_recipe)
            metrics["validation"] = {
                "passed": all(r.severity != "CRITICAL" for r in validation_results),
                "critical_issues": sum(1 for r in validation_results if r.severity == "CRITICAL"),
                "warnings": sum(1 for r in validation_results if r.severity == "WARNING"),
                "results": validation_results
            }
        
        # Evaluar cada objetivo individualmente
        metrics["goals"] = {}
        for goal in self.config.goals:
            goal_score = self._evaluate_goal(goal, best_recipe, validation_results)
            metrics["goals"][goal.name] = goal_score
        
        # Añadir información de la evolución
        metrics["evolution"] = {
            "generations": result["generations"],
            "final_fitness": result["best_fitness"],
            "fitness_history": result["best_fitness_history"],
            "avg_fitness_history": result["avg_fitness_history"],
            "elapsed_time": result["elapsed_time"]
        }
        
        # Mejorar nombre de la receta
        best_recipe.name = self._generate_recipe_name(best_recipe, metrics)
        
        if verbose:
            logger.info(f"Optimización completada: {best_recipe.name}")
            logger.info(f"Fitness final: {result['best_fitness']:.4f}")
            logger.info(f"Ingredientes: {len(best_recipe.ingredients)}")
            
            if self.validator:
                validation_status = "APROBADA" if metrics["validation"]["passed"] else "RECHAZADA"
                logger.info(f"Validación: {validation_status} - {metrics['validation']['critical_issues']} errores, "
                          f"{metrics['validation']['warnings']} advertencias")
        
        return best_recipe, metrics
    
    def _generate_recipe_name(self, recipe: Recipe, metrics: Dict[str, Any]) -> str:
        """
        Genera un nombre descriptivo para la receta optimizada.
        
        Args:
            recipe: Receta optimizada
            metrics: Métricas de la optimización
            
        Returns:
            Nombre para la receta
        """
        # Determinar características principales
        categories = set(ing.category for ing in recipe.ingredients if hasattr(ing, "category"))
        
        # Determinar tipo de masa
        has_whole_wheat = any(ing.name.lower().find("integral") >= 0 for ing in recipe.ingredients)
        is_gluten_free = not any(ing.category == "harina" and ing.name.lower().find("trigo") >= 0 
                                for ing in recipe.ingredients)
        
        # Determinar nivel de hidratación
        flour_qty = sum(ing.quantity for ing in recipe.ingredients if ing.category == "harina")
        water_qty = sum(ing.quantity for ing in recipe.ingredients if ing.category == "líquido")
        
        if flour_qty > 0:
            hydration = water_qty / flour_qty * 100
        else:
            hydration = 0
        
        # Construir nombre
        name_parts = ["Masa"]
        
        if is_gluten_free:
            name_parts.append("Sin Gluten")
        elif has_whole_wheat:
            name_parts.append("Integral")
        
        # Añadir nivel de hidratación
        if hydration > 70:
            name_parts.append("Alta Hidratación")
        elif hydration < 55:
            name_parts.append("Baja Hidratación")
        
        # Añadir escala
        name_parts.append(f"({self.config.production_scale.name})")
        
        # Añadir identificador de fitness
        if "evolution" in metrics and "final_fitness" in metrics["evolution"]:
            fitness = metrics["evolution"]["final_fitness"]
            name_parts.append(f"F{fitness:.2f}")
        
        return " ".join(name_parts) 