"""
Algoritmo genético para optimización de problemas en entornos productivos.

Este módulo implementa un algoritmo genético flexible para optimizar
diferentes tipos de soluciones relacionadas con procesos productivos.
"""

import numpy as np
import random
import logging
import time
import copy
from typing import Dict, List, Tuple, Any, Optional, Callable, Union, TypeVar
from dataclasses import dataclass, field

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('genplm.genetic')

# Tipo genérico para individuos
T = TypeVar('T')

@dataclass
class GeneticParams:
    """
    Parámetros para configurar el algoritmo genético.
    
    Attributes:
        population_size: Tamaño de la población
        generations: Número máximo de generaciones
        crossover_rate: Probabilidad de cruce entre individuos
        mutation_rate: Probabilidad de mutación de genes
        elite_size: Número de individuos elite que pasan directamente
        tournament_size: Tamaño del torneo para selección
        early_stopping: Detener si no hay mejora en N generaciones
        multi_objective: Si True, usa optimización multi-objetivo
    """
    population_size: int = 100
    generations: int = 50
    crossover_rate: float = 0.8
    mutation_rate: float = 0.2
    elite_size: int = 5
    tournament_size: int = 3
    early_stopping: int = 10
    multi_objective: bool = False
    
    def validate(self) -> None:
        """Valida que los parámetros sean coherentes."""
        if self.population_size < 10:
            raise ValueError("El tamaño de población debe ser al menos 10")
        
        if self.elite_size >= self.population_size / 2:
            raise ValueError("El tamaño de élite debe ser menor que la mitad de la población")
        
        if not (0 <= self.crossover_rate <= 1):
            raise ValueError("La tasa de cruce debe estar entre 0 y 1")
            
        if not (0 <= self.mutation_rate <= 1):
            raise ValueError("La tasa de mutación debe estar entre 0 y 1")

@dataclass
class Individual:
    """
    Representa un individuo en la población genética.
    
    Attributes:
        genes: Representación genética del individuo
        fitness: Valor(es) de aptitud del individuo
        age: Edad del individuo (generaciones)
        metadata: Información adicional sobre el individuo
    """
    genes: Any
    fitness: Union[float, List[float]] = 0.0
    age: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def dominant(self, other: 'Individual') -> bool:
        """
        Determina si este individuo domina a otro en sentido multi-objetivo.
        
        Args:
            other: Otro individuo para comparar
            
        Returns:
            True si este individuo domina al otro
        """
        if isinstance(self.fitness, float):
            return self.fitness > other.fitness
        
        # Dominancia de Pareto para múltiples objetivos
        self_better = False
        for i, (self_f, other_f) in enumerate(zip(self.fitness, other.fitness)):
            if self_f < other_f:  # Asumiendo minimización
                return False
            if self_f > other_f:
                self_better = True
        
        return self_better

@dataclass
class GeneticResults:
    """
    Almacena los resultados de la ejecución del algoritmo genético.
    
    Attributes:
        best_individual: Mejor individuo encontrado
        best_fitness: Mejor valor de aptitud (histórico)
        best_fitness_history: Historial de mejores aptitudes por generación
        avg_fitness_history: Historial de aptitudes promedio por generación
        population: Población final
        elapsed_time: Tiempo total de ejecución
        generations_executed: Número de generaciones ejecutadas
        early_stopped: Si True, se detuvo por early stopping
    """
    best_individual: Individual
    best_fitness: Union[float, List[float]]
    best_fitness_history: List[Union[float, List[float]]]
    avg_fitness_history: List[float]
    population: List[Individual]
    elapsed_time: float
    generations_executed: int
    early_stopped: bool = False
    
    def get_convergence_rate(self) -> float:
        """
        Calcula la tasa de convergencia del algoritmo.
        
        Returns:
            Tasa de convergencia (cambio promedio por generación)
        """
        if len(self.best_fitness_history) <= 1:
            return 0.0
        
        if isinstance(self.best_fitness_history[0], list):
            # Para multi-objetivo, usar la norma euclidiana
            diffs = []
            for i in range(1, len(self.best_fitness_history)):
                total_diff = sum(
                    (self.best_fitness_history[i][j] - self.best_fitness_history[i-1][j])**2
                    for j in range(len(self.best_fitness_history[i]))
                )
                diffs.append(np.sqrt(total_diff))
            
            return sum(diffs) / len(diffs) if diffs else 0.0
        else:
            # Para objetivo único
            diffs = [
                abs(self.best_fitness_history[i] - self.best_fitness_history[i-1])
                for i in range(1, len(self.best_fitness_history))
            ]
            return sum(diffs) / len(diffs) if diffs else 0.0
    
    def summary(self) -> str:
        """
        Genera un resumen de los resultados de la optimización.
        
        Returns:
            Resumen en forma de texto
        """
        lines = [
            "Resultados de Algoritmo Genético",
            "--------------------------------",
            f"Generaciones ejecutadas: {self.generations_executed}",
            f"Tiempo de ejecución: {self.elapsed_time:.2f} segundos",
            f"Early stopping: {'Sí' if self.early_stopped else 'No'}"
        ]
        
        # Mostrar fitness
        if isinstance(self.best_fitness, list):
            lines.append("Mejor fitness multi-objetivo:")
            for i, fit in enumerate(self.best_fitness):
                lines.append(f"  Objetivo {i+1}: {fit:.6f}")
        else:
            lines.append(f"Mejor fitness: {self.best_fitness:.6f}")
            
        # Tasa de convergencia
        lines.append(f"Tasa de convergencia: {self.get_convergence_rate():.6f}")
        
        return "\n".join(lines)

class GeneticOperators:
    """
    Operadores genéticos para manipular individuos.
    
    Esta clase define los métodos abstractos que deben implementar
    los operadores genéticos específicos para cada tipo de problema.
    """
    
    @staticmethod
    def initialize_population(size: int, **kwargs) -> List[Individual]:
        """
        Genera una población inicial aleatoria.
        
        Args:
            size: Tamaño de la población
            **kwargs: Parámetros adicionales
            
        Returns:
            Lista de individuos generados
        """
        raise NotImplementedError("El método debe ser implementado en una subclase")
    
    @staticmethod
    def evaluate_fitness(individual: Individual, **kwargs) -> Union[float, List[float]]:
        """
        Evalúa la aptitud de un individuo.
        
        Args:
            individual: Individuo a evaluar
            **kwargs: Parámetros adicionales
            
        Returns:
            Valor(es) de aptitud
        """
        raise NotImplementedError("El método debe ser implementado en una subclase")
    
    @staticmethod
    def select_parents(population: List[Individual], 
                       tournament_size: int,
                       **kwargs) -> Tuple[Individual, Individual]:
        """
        Selecciona dos padres para reproducción usando selección por torneo.
        
        Args:
            population: Población de individuos
            tournament_size: Tamaño del torneo
            **kwargs: Parámetros adicionales
            
        Returns:
            Tupla con dos individuos seleccionados
        """
        # Seleccionar individuos para el primer torneo
        tournament1 = random.sample(population, tournament_size)
        
        # Para objetivo único
        if not isinstance(tournament1[0].fitness, list):
            parent1 = max(tournament1, key=lambda ind: ind.fitness)
        else:
            # Para multi-objetivo: selección basada en dominancia
            non_dominated = [ind for ind in tournament1 
                            if not any(other.dominant(ind) for other in tournament1 if other != ind)]
            
            if non_dominated:
                parent1 = random.choice(non_dominated)
            else:
                parent1 = random.choice(tournament1)
        
        # Seleccionar individuos para el segundo torneo, excluyendo parent1
        remaining = [ind for ind in population if ind != parent1]
        tournament2 = random.sample(remaining, min(tournament_size, len(remaining)))
        
        # Seleccionar el segundo padre
        if not isinstance(tournament2[0].fitness, list):
            parent2 = max(tournament2, key=lambda ind: ind.fitness)
        else:
            non_dominated = [ind for ind in tournament2 
                            if not any(other.dominant(ind) for other in tournament2 if other != ind)]
            
            if non_dominated:
                parent2 = random.choice(non_dominated)
            else:
                parent2 = random.choice(tournament2)
        
        return parent1, parent2
    
    @staticmethod
    def crossover(parent1: Individual, parent2: Individual, **kwargs) -> Tuple[Individual, Individual]:
        """
        Realiza el cruce entre dos individuos padres para generar descendencia.
        
        Args:
            parent1: Primer individuo padre
            parent2: Segundo individuo padre
            **kwargs: Parámetros adicionales
            
        Returns:
            Tupla con dos individuos descendientes
        """
        raise NotImplementedError("El método debe ser implementado en una subclase")
    
    @staticmethod
    def mutate(individual: Individual, mutation_rate: float, **kwargs) -> Individual:
        """
        Aplica mutación a un individuo.
        
        Args:
            individual: Individuo a mutar
            mutation_rate: Probabilidad de mutación
            **kwargs: Parámetros adicionales
            
        Returns:
            Individuo mutado
        """
        raise NotImplementedError("El método debe ser implementado en una subclase")
    
    @staticmethod
    def is_valid(individual: Individual, **kwargs) -> bool:
        """
        Verifica si un individuo es válido según restricciones del problema.
        
        Args:
            individual: Individuo a validar
            **kwargs: Parámetros adicionales
            
        Returns:
            True si el individuo es válido, False en caso contrario
        """
        return True  # Por defecto, todos los individuos son válidos

class GeneticAlgorithm:
    """
    Implementación del algoritmo genético para optimización.
    
    Esta clase implementa la lógica principal del algoritmo genético,
    utilizando los operadores específicos del problema.
    """
    
    def __init__(
        self,
        operators: GeneticOperators,
        params: GeneticParams,
        problem_params: Dict[str, Any] = None,
        callbacks: List[Callable] = None
    ):
        """
        Inicializa el algoritmo genético.
        
        Args:
            operators: Operadores genéticos específicos del problema
            params: Parámetros de configuración del algoritmo
            problem_params: Parámetros específicos del problema
            callbacks: Funciones de callback para eventos del algoritmo
        """
        self.operators = operators
        self.params = params
        self.problem_params = problem_params or {}
        self.callbacks = callbacks or []
        
        # Validar parámetros
        self.params.validate()
        
        # Estado de ejecución
        self.population = []
        self.best_individual = None
        self.best_fitness = None if not params.multi_objective else []
        self.generation = 0
        
        logger.info(f"Algoritmo genético inicializado con {params.population_size} individuos")
    
    def initialize(self) -> None:
        """Inicializa la población y evalúa la aptitud inicial."""
        # Generar población inicial
        self.population = self.operators.initialize_population(
            self.params.population_size, 
            **self.problem_params
        )
        
        # Evaluar aptitud de cada individuo
        for ind in self.population:
            ind.fitness = self.operators.evaluate_fitness(ind, **self.problem_params)
        
        # Ordenar población por aptitud (para objetivo único)
        if not self.params.multi_objective:
            self.population.sort(key=lambda ind: ind.fitness, reverse=True)
            self.best_individual = copy.deepcopy(self.population[0])
            self.best_fitness = self.best_individual.fitness
        else:
            # Para multi-objetivo, encontrar frente no dominado
            non_dominated = self._get_non_dominated_front()
            if non_dominated:
                # Seleccionar uno aleatoriamente para seguimiento
                self.best_individual = copy.deepcopy(random.choice(non_dominated))
                self.best_fitness = self.best_individual.fitness
        
        logger.info(f"Población inicializada. Mejor fitness inicial: {self.best_fitness}")
    
    def _get_non_dominated_front(self) -> List[Individual]:
        """
        Obtiene el frente no dominado de la población actual.
        
        Returns:
            Lista de individuos no dominados
        """
        non_dominated = []
        
        for ind in self.population:
            # Verificar si es dominado por algún otro
            is_dominated = any(
                other.dominant(ind) for other in self.population 
                if other != ind
            )
            
            if not is_dominated:
                non_dominated.append(ind)
        
        return non_dominated
    
    def evolve(self) -> GeneticResults:
        """
        Ejecuta el algoritmo genético.
        
        Returns:
            Resultados de la ejecución
        """
        # Inicializar población si no se ha hecho
        if not self.population:
            self.initialize()
        
        # Variables para seguimiento
        start_time = time.time()
        self.generation = 0
        no_improvement_count = 0
        
        best_fitness_history = []
        avg_fitness_history = []
        
        # Guardar estado inicial
        if not self.params.multi_objective:
            best_fitness_history.append(self.best_fitness)
            avg_fitness = sum(ind.fitness for ind in self.population) / len(self.population)
            avg_fitness_history.append(avg_fitness)
        else:
            best_fitness_history.append(self.best_fitness.copy() if isinstance(self.best_fitness, list) else [self.best_fitness])
            # Para multi-objetivo, calcular promedio de cada objetivo
            objectives = list(zip(*[ind.fitness for ind in self.population]))
            avg_fitness = sum(sum(obj) / len(obj) for obj in objectives) / len(objectives)
            avg_fitness_history.append(avg_fitness)
        
        # Notificar inicio
        self._notify_callbacks('start', {
            'population': self.population,
            'best_individual': self.best_individual,
            'generation': self.generation
        })
        
        logger.info(f"Iniciando evolución por {self.params.generations} generaciones")
        
        # Bucle principal de evolución
        while self.generation < self.params.generations:
            self.generation += 1
            
            # Crear nueva generación
            new_population = self._create_new_generation()
            
            # Actualizar población
            self.population = new_population
            
            # Para objetivo único
            if not self.params.multi_objective:
                # Ordenar población por aptitud
                self.population.sort(key=lambda ind: ind.fitness, reverse=True)
                
                # Actualizar mejor individuo si hay mejora
                if self.population[0].fitness > self.best_fitness:
                    self.best_individual = copy.deepcopy(self.population[0])
                    self.best_fitness = self.best_individual.fitness
                    no_improvement_count = 0
                    logger.info(f"Generación {self.generation}: Nueva mejor aptitud = {self.best_fitness}")
                else:
                    no_improvement_count += 1
                
                # Guardar historial
                best_fitness_history.append(self.best_fitness)
                avg_fitness = sum(ind.fitness for ind in self.population) / len(self.population)
                avg_fitness_history.append(avg_fitness)
            else:
                # Para multi-objetivo
                non_dominated = self._get_non_dominated_front()
                
                # Verificar si hay nuevas soluciones no dominadas mejores
                improved = False
                for ind in non_dominated:
                    if any(ind.dominant(self.best_individual) for ind in non_dominated):
                        improved = True
                        self.best_individual = copy.deepcopy(random.choice(non_dominated))
                        self.best_fitness = self.best_individual.fitness
                        logger.info(f"Generación {self.generation}: Nueva mejor solución no dominada")
                        break
                
                if improved:
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1
                
                # Guardar historial
                best_fitness_history.append(self.best_fitness.copy() if isinstance(self.best_fitness, list) else [self.best_fitness])
                objectives = list(zip(*[ind.fitness for ind in self.population]))
                avg_fitness = sum(sum(obj) / len(obj) for obj in objectives) / len(objectives)
                avg_fitness_history.append(avg_fitness)
            
            # Notificar progreso
            self._notify_callbacks('generation', {
                'population': self.population,
                'best_individual': self.best_individual,
                'generation': self.generation,
                'no_improvement_count': no_improvement_count
            })
            
            # Early stopping
            if no_improvement_count >= self.params.early_stopping:
                logger.info(f"Deteniendo evolución: No hay mejora en {no_improvement_count} generaciones")
                break
        
        # Tiempo total
        elapsed_time = time.time() - start_time
        
        # Crear resultados
        results = GeneticResults(
            best_individual=self.best_individual,
            best_fitness=self.best_fitness,
            best_fitness_history=best_fitness_history,
            avg_fitness_history=avg_fitness_history,
            population=self.population,
            elapsed_time=elapsed_time,
            generations_executed=self.generation,
            early_stopped=no_improvement_count >= self.params.early_stopping
        )
        
        # Notificar finalización
        self._notify_callbacks('end', {
            'results': results
        })
        
        logger.info(f"Evolución completada en {elapsed_time:.2f}s. Mejor fitness: {self.best_fitness}")
        
        return results
    
    def _create_new_generation(self) -> List[Individual]:
        """
        Crea una nueva generación mediante selección, cruce y mutación.
        
        Returns:
            Nueva población de individuos
        """
        new_population = []
        
        # Elitismo: mantener los mejores individuos
        if self.params.elite_size > 0:
            if not self.params.multi_objective:
                # Para objetivo único, tomar los mejores
                elites = self.population[:self.params.elite_size]
            else:
                # Para multi-objetivo, tomar del frente no dominado
                non_dominated = self._get_non_dominated_front()
                elites = non_dominated[:self.params.elite_size] if len(non_dominated) >= self.params.elite_size else non_dominated
                
                # Completar con los mejores restantes si es necesario
                if len(elites) < self.params.elite_size:
                    remaining = [ind for ind in self.population if ind not in elites]
                    elites.extend(remaining[:self.params.elite_size - len(elites)])
            
            # Clonar elites para la nueva población
            for elite in elites:
                elite_copy = copy.deepcopy(elite)
                elite_copy.age += 1
                new_population.append(elite_copy)
        
        # Completar población con nuevos individuos
        while len(new_population) < self.params.population_size:
            # Seleccionar padres
            parent1, parent2 = self.operators.select_parents(
                self.population,
                self.params.tournament_size,
                **self.problem_params
            )
            
            # Aplicar cruce con cierta probabilidad
            if random.random() < self.params.crossover_rate:
                offspring1, offspring2 = self.operators.crossover(
                    parent1, parent2, 
                    **self.problem_params
                )
            else:
                # Sin cruce, clonar padres
                offspring1, offspring2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
            
            # Aplicar mutación
            offspring1 = self.operators.mutate(
                offspring1, 
                self.params.mutation_rate,
                **self.problem_params
            )
            
            offspring2 = self.operators.mutate(
                offspring2, 
                self.params.mutation_rate,
                **self.problem_params
            )
            
            # Validar descendientes
            valid1 = self.operators.is_valid(offspring1, **self.problem_params)
            valid2 = self.operators.is_valid(offspring2, **self.problem_params)
            
            # Evaluar aptitud de descendientes válidos
            if valid1:
                offspring1.age = 0
                offspring1.fitness = self.operators.evaluate_fitness(
                    offspring1, 
                    **self.problem_params
                )
                new_population.append(offspring1)
            
            # Agregar segundo descendiente si es válido y hay espacio
            if valid2 and len(new_population) < self.params.population_size:
                offspring2.age = 0
                offspring2.fitness = self.operators.evaluate_fitness(
                    offspring2, 
                    **self.problem_params
                )
                new_population.append(offspring2)
        
        return new_population
    
    def _notify_callbacks(self, event: str, data: Dict[str, Any]) -> None:
        """
        Notifica a los callbacks registrados sobre un evento.
        
        Args:
            event: Tipo de evento ('start', 'generation', 'end')
            data: Datos asociados al evento
        """
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                logger.error(f"Error en callback: {e}")

class RealValuedGeneticOperators(GeneticOperators):
    """
    Operadores genéticos para problemas con codificación de valores reales.
    
    Esta clase implementa operadores específicos para problemas donde los
    genes se representan como vectores de valores reales (números flotantes).
    """
    
    @staticmethod
    def initialize_population(
        size: int,
        dimension: int = 2,
        var_ranges: List[Tuple[float, float]] = None,
        **kwargs
    ) -> List[Individual]:
        """
        Genera una población inicial con valores reales aleatorios.
        
        Args:
            size: Tamaño de la población
            dimension: Dimensionalidad del problema (número de variables)
            var_ranges: Lista de tuplas (min, max) para cada variable
            **kwargs: Parámetros adicionales
            
        Returns:
            Lista de individuos generados
        """
        population = []
        
        # Usar rangos por defecto si no se especifican
        if var_ranges is None:
            var_ranges = [(0.0, 1.0)] * dimension
            
        # Asegurar que hay suficientes rangos
        if len(var_ranges) < dimension:
            var_ranges.extend([(0.0, 1.0)] * (dimension - len(var_ranges)))
        
        # Generar individuos aleatorios
        for _ in range(size):
            # Crear vector de valores aleatorios dentro de los rangos
            genes = np.array([
                random.uniform(min_val, max_val) 
                for min_val, max_val in var_ranges[:dimension]
            ])
            
            # Crear individuo
            ind = Individual(genes=genes)
            population.append(ind)
        
        return population
    
    @staticmethod
    def crossover(
        parent1: Individual, 
        parent2: Individual,
        alpha: float = 0.5,
        **kwargs
    ) -> Tuple[Individual, Individual]:
        """
        Realiza cruce aritmético entre dos individuos.
        
        Args:
            parent1: Primer individuo padre
            parent2: Segundo individuo padre
            alpha: Factor de mezcla (0-1)
            **kwargs: Parámetros adicionales
            
        Returns:
            Tupla con dos individuos descendientes
        """
        # Asegurar que ambos padres tienen genes del mismo tamaño
        if len(parent1.genes) != len(parent2.genes):
            raise ValueError("Los padres deben tener el mismo número de genes")
        
        # Cruce aritmético (combinación lineal)
        genes1 = alpha * parent1.genes + (1 - alpha) * parent2.genes
        genes2 = (1 - alpha) * parent1.genes + alpha * parent2.genes
        
        # Crear descendientes
        offspring1 = Individual(genes=genes1)
        offspring2 = Individual(genes=genes2)
        
        return offspring1, offspring2
    
    @staticmethod
    def mutate(
        individual: Individual, 
        mutation_rate: float,
        mutation_scale: float = 0.1,
        var_ranges: List[Tuple[float, float]] = None,
        **kwargs
    ) -> Individual:
        """
        Aplica mutación gaussiana a un individuo.
        
        Args:
            individual: Individuo a mutar
            mutation_rate: Probabilidad de mutación por gen
            mutation_scale: Escala de la distribución normal para mutación
            var_ranges: Lista de tuplas (min, max) para cada variable
            **kwargs: Parámetros adicionales
            
        Returns:
            Individuo mutado
        """
        # Clonar genes para evitar modificar el original
        genes = individual.genes.copy()
        
        # Usar rangos por defecto si no se especifican
        if var_ranges is None:
            var_ranges = [(0.0, 1.0)] * len(genes)
            
        # Asegurar que hay suficientes rangos
        if len(var_ranges) < len(genes):
            var_ranges.extend([(0.0, 1.0)] * (len(genes) - len(var_ranges)))
        
        # Aplicar mutación a cada gen con cierta probabilidad
        for i in range(len(genes)):
            if random.random() < mutation_rate:
                # Calcular escala de mutación basada en el rango
                min_val, max_val = var_ranges[i]
                range_size = max_val - min_val
                sigma = range_size * mutation_scale
                
                # Aplicar mutación gaussiana
                genes[i] += random.gauss(0, sigma)
                
                # Limitar al rango permitido
                genes[i] = max(min_val, min(max_val, genes[i]))
        
        # Crear individuo mutado
        mutated = copy.deepcopy(individual)
        mutated.genes = genes
        
        return mutated
    
    @staticmethod
    def is_valid(
        individual: Individual,
        constraints: List[Callable] = None,
        **kwargs
    ) -> bool:
        """
        Verifica si un individuo cumple con las restricciones.
        
        Args:
            individual: Individuo a validar
            constraints: Lista de funciones que verifican restricciones
            **kwargs: Parámetros adicionales
            
        Returns:
            True si el individuo es válido, False en caso contrario
        """
        # Sin restricciones, todos son válidos
        if constraints is None:
            return True
        
        # Verificar cada restricción
        for constraint in constraints:
            if not constraint(individual.genes, **kwargs):
                return False
        
        return True

# Ejemplo de función de callback para seguimiento
def progress_callback(event: str, data: Dict[str, Any]) -> None:
    """
    Ejemplo de callback para mostrar progreso del algoritmo.
    
    Args:
        event: Tipo de evento
        data: Datos asociados al evento
    """
    if event == 'start':
        print(f"Iniciando algoritmo genético con {len(data['population'])} individuos")
    elif event == 'generation':
        gen = data['generation']
        if gen % 10 == 0:  # Mostrar cada 10 generaciones
            best_fitness = data['best_individual'].fitness
            if isinstance(best_fitness, list):
                fitness_str = ", ".join(f"{f:.6f}" for f in best_fitness)
                print(f"Generación {gen}: Mejor fitness = [{fitness_str}]")
            else:
                print(f"Generación {gen}: Mejor fitness = {best_fitness:.6f}")
    elif event == 'end':
        results = data['results']
        print(f"Algoritmo completado en {results.elapsed_time:.2f}s")
        print(f"Mejor solución encontrada con fitness: {results.best_fitness}") 