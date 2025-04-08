"""
Optimizador genético general para problemas de optimización.

Este módulo proporciona una implementación genérica de un optimizador
basado en algoritmos genéticos que puede ser especializado para
diferentes tipos de problemas.
"""

import random
import numpy as np
import time
import logging
from typing import Dict, List, Any, Tuple, Callable, Union, Optional
from dataclasses import dataclass, field

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('genplm.genetic_optimizer')

@dataclass
class Individual:
    """
    Representa un individuo en una población genética.
    
    Attributes:
        genes: Representación de los parámetros del individuo
        fitness: Valor de aptitud del individuo
        age: Edad del individuo (generaciones)
        metadata: Información adicional
    """
    genes: Dict[str, Any]
    fitness: float = 0.0
    age: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """Permite comparación para ordenamiento."""
        return self.fitness < other.fitness
    
    def __eq__(self, other):
        """Permite comparación de igualdad."""
        if not isinstance(other, Individual):
            return False
        return self.fitness == other.fitness

class GeneticOptimizer:
    """
    Implementación de un optimizador basado en algoritmos genéticos.
    
    Este optimizador puede trabajar con genes que son parámetros de diferentes
    tipos (continuos, discretos, categóricos) almacenados en un diccionario.
    """
    
    def __init__(
        self,
        gene_ranges: Dict[str, Union[Tuple[float, float], List[Any]]],
        fitness_function: Callable[[Dict[str, Any]], float],
        population_size: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        elite_size: int = 5,
        tournament_size: int = 3,
        maximize: bool = True
    ):
        """
        Inicializa el optimizador genético.
        
        Args:
            gene_ranges: Diccionario con los rangos posibles para cada gen
                       Cada gen puede tener un rango continuo (tupla min, max)
                       o discreto (lista de valores posibles)
            fitness_function: Función que evalúa la aptitud de un individuo
            population_size: Tamaño de la población
            mutation_rate: Probabilidad de mutación de cada gen
            crossover_rate: Probabilidad de cruce entre individuos
            elite_size: Número de mejores individuos que pasan directamente a la siguiente generación
            tournament_size: Tamaño del torneo para selección
            maximize: Si es True, maximiza la función de aptitud; si es False, la minimiza
        """
        self.gene_ranges = gene_ranges
        self.fitness_function = fitness_function
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        self.tournament_size = tournament_size
        self.maximize = maximize
        
        # Inicializar población
        self.population = []
        self.best_individual = None
        self.best_fitness = float('-inf') if maximize else float('inf')
        
        # Métricas
        self.current_generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []
        
        logger.info(f"Inicializado optimizador genético con {len(gene_ranges)} genes")
        logger.info(f"Tamaño de población: {population_size}, Tasa de mutación: {mutation_rate}, Elitismo: {elite_size}")
    
    def create_individual(self) -> Individual:
        """
        Crea un nuevo individuo con genes aleatorios.
        
        Returns:
            Nuevo individuo con genes aleatorios
        """
        genes = {}
        
        for gene_name, gene_range in self.gene_ranges.items():
            # Si el rango es una tupla, es un rango continuo (min, max)
            if isinstance(gene_range, tuple) and len(gene_range) == 2:
                min_val, max_val = gene_range
                # Si los valores son enteros, generamos un entero aleatorio
                if isinstance(min_val, int) and isinstance(max_val, int):
                    genes[gene_name] = random.randint(min_val, max_val)
                else:
                    # Si son flotantes, generamos un flotante aleatorio
                    genes[gene_name] = random.uniform(min_val, max_val)
            
            # Si el rango es una lista, elegimos un valor de la lista
            elif isinstance(gene_range, list):
                genes[gene_name] = random.choice(gene_range)
            
            else:
                raise ValueError(f"Formato no válido para el rango del gen {gene_name}")
        
        return Individual(genes)
    
    def initialize_population(self):
        """Inicializa la población con individuos aleatorios."""
        self.population = [self.create_individual() for _ in range(self.population_size)]
        
        # Evaluar aptitud inicial
        self.evaluate_population()
        
        # Guardar mejor individuo inicial
        self.update_best_individual()
        
        logger.info(f"Población inicial generada y evaluada")
        logger.info(f"Mejor aptitud inicial: {self.best_fitness:.4f}")
    
    def evaluate_population(self):
        """Evalúa la aptitud de todos los individuos en la población."""
        for individual in self.population:
            if individual.fitness is None:  # Solo evaluar si no tiene aptitud asignada
                individual.fitness = self.fitness_function(individual.genes)
    
    def update_best_individual(self):
        """Actualiza el mejor individuo de la población actual."""
        # Obtener el mejor de la población actual
        current_best = max(self.population, key=lambda ind: ind.fitness) if self.maximize else \
                     min(self.population, key=lambda ind: ind.fitness)
        
        # Comparar con el mejor histórico
        if self.best_individual is None or \
           (self.maximize and current_best.fitness > self.best_fitness) or \
           (not self.maximize and current_best.fitness < self.best_fitness):
            self.best_individual = current_best.clone()
            self.best_fitness = current_best.fitness
            logger.debug(f"Nuevo mejor individuo encontrado: fitness={self.best_fitness:.4f}")
    
    def select_parent(self) -> Individual:
        """
        Selecciona un padre mediante torneo.
        
        Returns:
            Individuo seleccionado como padre
        """
        # Seleccionar individuos aleatorios para el torneo
        tournament = random.sample(self.population, min(self.tournament_size, len(self.population)))
        
        # Seleccionar el mejor del torneo
        if self.maximize:
            return max(tournament, key=lambda ind: ind.fitness)
        else:
            return min(tournament, key=lambda ind: ind.fitness)
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """
        Realiza el cruce entre dos padres.
        
        Args:
            parent1: Primer padre
            parent2: Segundo padre
        
        Returns:
            Tupla con los dos hijos resultantes
        """
        # Decidir si hacer cruce
        if random.random() > self.crossover_rate:
            return parent1.clone(), parent2.clone()
        
        # Crear genes para los hijos
        child1_genes = {}
        child2_genes = {}
        
        # Para cada gen, decidir aleatoriamente de qué padre hereda cada hijo
        for gene_name in self.gene_ranges.keys():
            if random.random() < 0.5:
                child1_genes[gene_name] = parent1.genes[gene_name]
                child2_genes[gene_name] = parent2.genes[gene_name]
            else:
                child1_genes[gene_name] = parent2.genes[gene_name]
                child2_genes[gene_name] = parent1.genes[gene_name]
        
        return Individual(child1_genes), Individual(child2_genes)
    
    def mutate(self, individual: Individual) -> Individual:
        """
        Aplica mutación a un individuo.
        
        Args:
            individual: Individuo a mutar
        
        Returns:
            Individuo mutado
        """
        mutated_genes = individual.genes.copy()
        
        # Para cada gen, decidir si mutar
        for gene_name, gene_range in self.gene_ranges.items():
            if random.random() < self.mutation_rate:
                # Si el rango es una tupla, es un rango continuo (min, max)
                if isinstance(gene_range, tuple) and len(gene_range) == 2:
                    min_val, max_val = gene_range
                    
                    # Si los valores son enteros, generamos un entero aleatorio
                    if isinstance(min_val, int) and isinstance(max_val, int):
                        mutated_genes[gene_name] = random.randint(min_val, max_val)
                    else:
                        # Si son flotantes, aplicamos una mutación gaussiana
                        current = mutated_genes[gene_name]
                        range_width = max_val - min_val
                        mutation = random.gauss(0, range_width * 0.1)  # Desviación del 10% del rango
                        new_val = current + mutation
                        # Asegurar que está dentro del rango
                        mutated_genes[gene_name] = max(min_val, min(max_val, new_val))
                
                # Si el rango es una lista, elegimos un valor diferente de la lista
                elif isinstance(gene_range, list):
                    current = mutated_genes[gene_name]
                    options = [opt for opt in gene_range if opt != current]
                    if options:  # Si hay opciones diferentes
                        mutated_genes[gene_name] = random.choice(options)
        
        return Individual(mutated_genes)
    
    def create_next_generation(self):
        """Crea la siguiente generación mediante selección, cruce y mutación."""
        new_population = []
        
        # Mantener a la élite
        if self.elite_size > 0:
            # Ordenar población
            sorted_population = sorted(self.population, 
                                     key=lambda ind: ind.fitness, 
                                     reverse=self.maximize)
            
            # Añadir élite a la nueva población
            elite = sorted_population[:self.elite_size]
            new_population.extend([ind.clone() for ind in elite])
        
        # Completar el resto de la población con descendencia
        while len(new_population) < self.population_size:
            # Seleccionar padres
            parent1 = self.select_parent()
            parent2 = self.select_parent()
            
            # Crear hijos mediante cruce
            child1, child2 = self.crossover(parent1, parent2)
            
            # Mutar hijos
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)
            
            # Añadir hijos a la nueva población
            new_population.append(child1)
            if len(new_population) < self.population_size:  # Evitar exceder el tamaño
                new_population.append(child2)
        
        # Actualizar población
        self.population = new_population
    
    def optimize(self, max_generations: int = 100, verbose: bool = True) -> Dict[str, Any]:
        """
        Ejecuta el algoritmo genético para encontrar la solución óptima.
        
        Args:
            max_generations: Número máximo de generaciones
            verbose: Si es True, muestra información del progreso
        
        Returns:
            Diccionario con los resultados de la optimización
        """
        start_time = time.time()
        
        # Inicializar población si no se ha hecho
        if not self.population:
            self.initialize_population()
        
        # Ejecutar generaciones
        for generation in range(max_generations):
            self.current_generation = generation + 1
            
            # Crear nueva generación
            self.create_next_generation()
            
            # Evaluar nueva población
            self.evaluate_population()
            
            # Actualizar el mejor individuo
            self.update_best_individual()
            
            # Calcular métricas
            avg_fitness = sum(ind.fitness for ind in self.population) / len(self.population)
            self.best_fitness_history.append(self.best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            
            # Mostrar progreso
            if verbose and (generation % (max_generations // 10) == 0 or generation == max_generations - 1):
                elapsed = time.time() - start_time
                logger.info(f"Generación {generation+1}/{max_generations}: Mejor={self.best_fitness:.4f}, "
                          f"Promedio={avg_fitness:.4f}, Tiempo={elapsed:.2f}s")
        
        # Tiempo total
        total_time = time.time() - start_time
        logger.info(f"Optimización completada en {total_time:.2f} segundos")
        logger.info(f"Mejor aptitud: {self.best_fitness:.4f}")
        
        # Preparar resultados
        result = {
            "best_individual": self.best_individual,
            "best_fitness": self.best_fitness,
            "generations": self.current_generation,
            "best_fitness_history": self.best_fitness_history,
            "avg_fitness_history": self.avg_fitness_history,
            "elapsed_time": total_time
        }
        
        return result 