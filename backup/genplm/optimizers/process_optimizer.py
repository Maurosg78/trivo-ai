"""
Optimizador de Procesos Productivos basado en Algoritmos Genéticos.

Este módulo conecta el optimizador genético con los modelos de procesos
para obtener configuraciones óptimas de parámetros que mejoran
múltiples KPIs simultáneamente.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Callable, Union
import logging
import json
import os
from dataclasses import dataclass, field

from genplm.core.genetic_optimizer import GeneticOptimizer, Individual
from genplm.models.process_model import Process, ProcessStep, Resource, Product, QUALITY_METRICS

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('genplm.process_optimizer')

@dataclass
class OptimizationConfig:
    """Configuración para la optimización de procesos."""
    
    # Parámetros de optimización genética
    population_size: int = 50
    generations: int = 100
    crossover_rate: float = 0.7
    mutation_rate: float = 0.1
    elite_size: int = 5
    
    # Pesos para función de fitness multi-objetivo
    cost_weight: float = 0.3
    time_weight: float = 0.2
    quality_weight: float = 0.3
    resource_weight: float = 0.2
    
    # Restricciones del problema
    max_cost: Optional[float] = None
    max_time: Optional[float] = None
    min_quality: Optional[float] = None
    
    # Configuración de simulación
    simulation_runs: int = 10
    simulation_noise: float = 0.05
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a un diccionario."""
        return {
            "population_size": self.population_size,
            "generations": self.generations,
            "crossover_rate": self.crossover_rate,
            "mutation_rate": self.mutation_rate,
            "elite_size": self.elite_size,
            "cost_weight": self.cost_weight,
            "time_weight": self.time_weight,
            "quality_weight": self.quality_weight,
            "resource_weight": self.resource_weight,
            "max_cost": self.max_cost,
            "max_time": self.max_time,
            "min_quality": self.min_quality,
            "simulation_runs": self.simulation_runs,
            "simulation_noise": self.simulation_noise
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptimizationConfig':
        """Crea una configuración a partir de un diccionario."""
        return cls(
            population_size=data.get("population_size", 50),
            generations=data.get("generations", 100),
            crossover_rate=data.get("crossover_rate", 0.7),
            mutation_rate=data.get("mutation_rate", 0.1),
            elite_size=data.get("elite_size", 5),
            cost_weight=data.get("cost_weight", 0.3),
            time_weight=data.get("time_weight", 0.2),
            quality_weight=data.get("quality_weight", 0.3),
            resource_weight=data.get("resource_weight", 0.2),
            max_cost=data.get("max_cost"),
            max_time=data.get("max_time"),
            min_quality=data.get("min_quality"),
            simulation_runs=data.get("simulation_runs", 10),
            simulation_noise=data.get("simulation_noise", 0.05)
        )

class ProcessSimulator:
    """Simula la ejecución de un proceso con parámetros específicos."""
    
    def __init__(self, process: Process, config: OptimizationConfig):
        """
        Inicializa el simulador.
        
        Args:
            process: Proceso a simular
            config: Configuración de simulación
        """
        self.process = process
        self.config = config
    
    def simulate(self, parameters: Dict[str, Any]) -> Dict[str, float]:
        """
        Simula la ejecución del proceso con los parámetros dados.
        
        Args:
            parameters: Diccionario con valores de parámetros a aplicar
            
        Returns:
            Diccionario con métricas de resultado (costo, tiempo, calidad, uso de recursos)
        """
        # Clonar el proceso para la simulación
        simulation_process = Process.from_dict(self.process.to_dict())
        
        # Aplicar parámetros
        simulation_process.apply_optimized_parameters(parameters)
        
        # Ejecutar múltiples simulaciones y promediar resultados
        costs = []
        durations = []
        quality_scores = []
        resource_utilizations = []
        
        for _ in range(self.config.simulation_runs):
            # Aplicar ruido aleatorio para simular variabilidad del proceso real
            noise_factor = 1.0 + np.random.normal(0, self.config.simulation_noise)
            
            # Simular costo
            base_cost = simulation_process.calculate_total_cost()
            costs.append(base_cost * noise_factor)
            
            # Simular duración
            base_duration = simulation_process.calculate_estimated_duration().total_seconds() / 3600  # en horas
            durations.append(base_duration * noise_factor)
            
            # Simular calidad (valor entre 0 y 1, donde 1 es perfecto)
            quality_score = self._calculate_quality_score(simulation_process, parameters)
            quality_scores.append(max(0, min(1, quality_score * noise_factor)))
            
            # Simular utilización de recursos (valor entre 0 y 1, donde 1 es utilización perfecta)
            resource_utilization = self._calculate_resource_utilization(simulation_process, parameters)
            resource_utilizations.append(max(0, min(1, resource_utilization * noise_factor)))
        
        # Devolver promedios
        return {
            "cost": np.mean(costs),
            "duration": np.mean(durations),
            "quality": np.mean(quality_scores),
            "resource_utilization": np.mean(resource_utilizations)
        }
    
    def _calculate_quality_score(self, process: Process, parameters: Dict[str, Any]) -> float:
        """
        Calcula un puntaje de calidad basado en los parámetros y el proceso.
        Esta es una implementación simplificada; en un sistema real dependería
        de modelos específicos y datos históricos.
        """
        # Simular el impacto de los parámetros en la calidad
        quality_score = 0.7  # Valor base
        
        # Algunos factores simulados que afectan la calidad
        for step in process.steps:
            # Simular el impacto de cada paso en la calidad
            step_quality = 0.0
            
            # Considerar parámetros específicos del paso
            for param_name, param_range in step.input_parameters.items():
                full_param_name = f"{step.id}_{param_name}"
                if full_param_name in parameters:
                    param_value = parameters[full_param_name]
                    
                    # Simular el impacto del parámetro en la calidad
                    if isinstance(param_range, tuple) and len(param_range) == 2:
                        # Parámetro numérico
                        min_val, max_val = param_range
                        # Asumir que hay un valor óptimo en el medio del rango
                        optimal_value = (min_val + max_val) / 2
                        # La calidad disminuye cuanto más nos alejamos del óptimo
                        normalized_distance = abs(param_value - optimal_value) / (max_val - min_val)
                        param_quality = 1.0 - normalized_distance
                    else:
                        # Parámetro categórico, asumir calidad promedio
                        param_quality = 0.5
                    
                    # Sumar contribución ponderada del parámetro
                    step_quality += param_quality * 0.1  # Factor arbitrario
            
            # Considerar factores de calidad del paso
            for factor, impact in step.quality_factors.items():
                step_quality += impact
            
            # Normalizar y agregar calidad del paso al total
            step_quality = max(0, min(1, step_quality))
            quality_score += step_quality / len(process.steps)
        
        # Normalizar puntuación final
        return max(0, min(1, quality_score))
    
    def _calculate_resource_utilization(self, process: Process, parameters: Dict[str, Any]) -> float:
        """
        Calcula la eficiencia de utilización de recursos.
        Esta es una implementación simplificada.
        """
        # Obtener todos los recursos
        resources = list(process.resources.values())
        if not resources:
            return 0.5  # Valor predeterminado si no hay recursos
        
        # Calcular utilización general
        total_utilization = 0.0
        for resource in resources:
            # Obtener propiedades relevantes
            availability = resource.availability
            
            # Estimar la utilización del recurso
            utilization = 0.6  # Valor base arbitrario
            
            # Ajustar según parámetros (ejemplo simplificado)
            for param_name, param_value in parameters.items():
                if param_name.endswith("_speed") or param_name.endswith("_rate"):
                    # Velocidades y tasas afectan la utilización
                    # Solo un ejemplo simulado
                    utilization += 0.1 * np.random.random()
            
            # Normalizar y pesar por la disponibilidad
            utilization = max(0, min(1, utilization)) * availability
            total_utilization += utilization
        
        # Promediar utilización entre todos los recursos
        return total_utilization / len(resources)

class ProcessOptimizer:
    """
    Optimiza los parámetros de un proceso productivo utilizando algoritmos genéticos.
    """
    
    def __init__(self, process: Process, config: Optional[OptimizationConfig] = None):
        """
        Inicializa el optimizador de procesos.
        
        Args:
            process: Proceso a optimizar
            config: Configuración de optimización, o None para usar la configuración predeterminada
        """
        self.process = process
        self.config = config or OptimizationConfig()
        self.simulator = ProcessSimulator(process, self.config)
        
        # Obtener parámetros optimizables
        self.optimization_params = process.get_optimization_parameters()
        
        logger.info(f"Inicializado optimizador para proceso '{process.name}' con {len(self.optimization_params)} parámetros")
        
    def _fitness_function(self, parameters: Dict[str, Any]) -> float:
        """
        Función de fitness que evalúa un conjunto de parámetros.
        
        Args:
            parameters: Diccionario con valores de parámetros
            
        Returns:
            Valor de fitness (mayor es mejor)
        """
        # Simular el proceso con estos parámetros
        simulation_result = self.simulator.simulate(parameters)
        
        # Extraer métricas
        cost = simulation_result["cost"]
        duration = simulation_result["duration"]
        quality = simulation_result["quality"]
        resource_utilization = simulation_result["resource_utilization"]
        
        # Verificar restricciones
        if (self.config.max_cost is not None and cost > self.config.max_cost) or \
           (self.config.max_time is not None and duration > self.config.max_time) or \
           (self.config.min_quality is not None and quality < self.config.min_quality):
            return 0.0  # Solución no viable
        
        # Normalizar métricas
        # Suponemos que menor costo y duración son mejores, y mayor calidad y utilización son mejores
        normalized_cost = 1.0 - min(1.0, cost / (self.config.max_cost or 1000))
        normalized_duration = 1.0 - min(1.0, duration / (self.config.max_time or 100))
        normalized_quality = quality
        normalized_resource_utilization = resource_utilization
        
        # Calcular fitness combinado según pesos
        fitness = (
            self.config.cost_weight * normalized_cost +
            self.config.time_weight * normalized_duration +
            self.config.quality_weight * normalized_quality +
            self.config.resource_weight * normalized_resource_utilization
        )
        
        return fitness
    
    def optimize(self) -> Dict[str, Any]:
        """
        Ejecuta la optimización del proceso.
        
        Returns:
            Diccionario con resultados de la optimización
        """
        logger.info(f"Iniciando optimización del proceso '{self.process.name}'")
        
        # Crear optimizador genético
        optimizer = GeneticOptimizer(
            gene_ranges=self.optimization_params,
            fitness_function=self._fitness_function,
            population_size=self.config.population_size,
            elite_size=self.config.elite_size,
            mutation_rate=self.config.mutation_rate,
            crossover_rate=self.config.crossover_rate,
            maximize=True
        )
        
        # Ejecutar optimización
        optimization_result = optimizer.optimize(max_generations=self.config.generations)
        
        # Extraer mejor solución
        best_individual = optimization_result["best_individual"]
        best_params = best_individual.genes
        
        # Simular mejor solución para obtener métricas detalladas
        best_metrics = self.simulator.simulate(best_params)
        
        # Aplicar parámetros optimizados al proceso
        optimized_process = Process.from_dict(self.process.to_dict())
        optimized_process.apply_optimized_parameters(best_params)
        
        # Preparar resultado final
        result = {
            "optimized_process": optimized_process,
            "optimized_parameters": best_params,
            "metrics": best_metrics,
            "fitness": best_individual.fitness,
            "optimization_history": {
                "best_fitness": optimization_result["best_fitness_history"],
                "avg_fitness": optimization_result["avg_fitness_history"],
                "generations": optimization_result["generations"]
            }
        }
        
        logger.info(f"Optimización completada con fitness {best_individual.fitness:.4f}")
        logger.info(f"Costo optimizado: {best_metrics['cost']:.2f}, Duración: {best_metrics['duration']:.2f}h, "
                    f"Calidad: {best_metrics['quality']:.2f}, Utilización: {best_metrics['resource_utilization']:.2f}")
        
        return result
    
    def save_result(self, result: Dict[str, Any], filepath: str) -> None:
        """
        Guarda el resultado de la optimización.
        
        Args:
            result: Resultado de la optimización
            filepath: Ruta donde guardar el resultado
        """
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        # Preparar datos para serialización
        serializable_result = {
            "optimized_process": result["optimized_process"].to_dict(),
            "optimized_parameters": result["optimized_parameters"],
            "metrics": result["metrics"],
            "fitness": result["fitness"],
            "optimization_history": result["optimization_history"],
            "config": self.config.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Guardar en archivo
        with open(filepath, 'w') as f:
            json.dump(serializable_result, f, indent=2)
        
        logger.info(f"Resultados de optimización guardados en '{filepath}'")
    
    def load_result(self, filepath: str) -> Dict[str, Any]:
        """
        Carga un resultado de optimización previamente guardado.
        
        Args:
            filepath: Ruta del archivo
            
        Returns:
            Diccionario con el resultado cargado
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Reconstruir objetos
        result = {
            "optimized_process": Process.from_dict(data["optimized_process"]),
            "optimized_parameters": data["optimized_parameters"],
            "metrics": data["metrics"],
            "fitness": data["fitness"],
            "optimization_history": data["optimization_history"]
        }
        
        logger.info(f"Resultados de optimización cargados desde '{filepath}'")
        return result

from datetime import datetime  # Para timestamp en save_result 