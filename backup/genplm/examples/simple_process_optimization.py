"""
Ejemplo de optimización de un proceso productivo simple.

Este script muestra cómo usar el sistema genPLM para modelar y optimizar
un proceso productivo básico de fabricación.
"""

import sys
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Tuple

# Añadir el directorio raíz al path para importaciones
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importar los módulos del sistema
from genplm.core.process_model import (
    Process, ProcessStep, Resource, ProcessType, ResourceType
)
from genplm.core.genetic_optimizer import (
    GeneticOptimizer, Individual
)
from genplm.optimizers.process_optimizer import (
    ProcessOptimizer, OptimizationConfig
)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('genplm.example')

def create_example_process() -> Process:
    """
    Crea un proceso de fabricación simple para el ejemplo.
    
    Returns:
        Proceso creado
    """
    # Definir el proceso
    process = Process(
        id="proc-001",
        name="Proceso de fabricación de producto X",
        type=ProcessType.MANUFACTURING
    )
    
    # Definir recursos
    resources = [
        Resource(
            id="mach-001",
            name="Máquina CNC",
            type=ResourceType.MACHINE,
            capacity=1.0,
            cost_per_hour=50.0,
            efficiency=0.9
        ),
        Resource(
            id="mach-002",
            name="Máquina Extrusora",
            type=ResourceType.MACHINE,
            capacity=1.0,
            cost_per_hour=35.0,
            efficiency=0.85
        ),
        Resource(
            id="op-001",
            name="Operador",
            type=ResourceType.HUMAN,
            capacity=2.0,  # 2 operadores disponibles
            cost_per_hour=18.0,
            efficiency=0.95
        ),
        Resource(
            id="mat-001",
            name="Materia Prima A",
            type=ResourceType.MATERIAL,
            capacity=100.0,  # kg disponibles
            cost_per_hour=0.0,  # costo por unidad, no por hora
            attributes={"cost_per_kg": 5.0}
        ),
        Resource(
            id="mat-002",
            name="Materia Prima B",
            type=ResourceType.MATERIAL,
            capacity=100.0,  # kg disponibles
            cost_per_hour=0.0,
            attributes={"cost_per_kg": 8.0}
        )
    ]
    
    # Añadir recursos al proceso
    for resource in resources:
        process.add_resource(resource)
    
    # Definir pasos del proceso
    steps = [
        ProcessStep(
            id="step-001",
            name="Preparación de materiales",
            duration=30.0,  # minutos
            resources=[("op-001", 1.0), ("mat-001", 10.0), ("mat-002", 5.0)],
            predecessors=[],
            outputs={"prep-material": 1.0},
            quality_factors={"precision": 0.8},
            failure_rate=0.02,
            cost=15.0
        ),
        ProcessStep(
            id="step-002",
            name="Extrusión de material",
            duration=45.0,
            resources=[("mach-002", 1.0), ("op-001", 1.0)],
            predecessors=["step-001"],
            outputs={"extruded-part": 1.0},
            quality_factors={"uniformity": 0.85},
            failure_rate=0.05,
            cost=25.0
        ),
        ProcessStep(
            id="step-003",
            name="Mecanizado CNC",
            duration=60.0,
            resources=[("mach-001", 1.0), ("op-001", 1.0)],
            predecessors=["step-002"],
            outputs={"machined-part": 1.0},
            quality_factors={"precision": 0.95, "finish": 0.9},
            failure_rate=0.03,
            cost=40.0
        ),
        ProcessStep(
            id="step-004",
            name="Inspección de calidad",
            duration=15.0,
            resources=[("op-001", 1.0)],
            predecessors=["step-003"],
            outputs={"inspected-part": 1.0},
            quality_factors={"detection": 0.98},
            failure_rate=0.01,
            cost=10.0
        ),
        ProcessStep(
            id="step-005",
            name="Acabado final",
            duration=30.0,
            resources=[("op-001", 1.0)],
            predecessors=["step-004"],
            outputs={"finished-product": 1.0},
            quality_factors={"finish": 0.95},
            failure_rate=0.02,
            cost=20.0
        )
    ]
    
    # Añadir pasos al proceso
    for step in steps:
        process.add_step(step)
    
    # Definir entradas y salidas del proceso
    process.inputs = {
        "mat-001": 10.0,
        "mat-002": 5.0
    }
    
    process.outputs = {
        "finished-product": 1.0
    }
    
    # Definir KPIs del proceso
    process.kpis = {
        "total_time": {
            "description": "Tiempo total de producción",
            "unit": "minutos",
            "target": 150.0,
            "weight": 0.3
        },
        "total_cost": {
            "description": "Costo total de producción",
            "unit": "USD",
            "target": 150.0,
            "weight": 0.3
        },
        "quality": {
            "description": "Índice de calidad del producto",
            "unit": "porcentaje",
            "target": 0.95,
            "weight": 0.4
        }
    }
    
    return process

def define_optimization_parameters(process: Process) -> Dict[str, Tuple]:
    """
    Define los parámetros a optimizar en el proceso.
    
    Args:
        process: Proceso a optimizar
        
    Returns:
        Diccionario con parámetros y sus rangos
    """
    # Definir parámetros para optimización
    optimization_params = {
        # Temperatura de extrusión (°C)
        "extrusion_temp": (180, 250),
        
        # Velocidad de la extrusora (mm/s)
        "extrusion_speed": (10, 50),
        
        # Velocidad de corte CNC (mm/min)
        "cnc_cutting_speed": (100, 500),
        
        # Profundidad de corte CNC (mm)
        "cnc_cutting_depth": (0.5, 3.0),
        
        # Tiempo de inspección (min)
        "inspection_time": (10, 30),
        
        # Número de puntos de inspección
        "inspection_points": (5, 15),
        
        # Tipo de acabado (categórico: 1=básico, 2=estándar, 3=premium)
        "finish_type": [1, 2, 3]
    }
    
    return optimization_params

def fitness_function(params: Dict[str, Any]) -> float:
    """
    Función de aptitud para evaluar una configuración de parámetros.
    
    Args:
        params: Parámetros a evaluar
        
    Returns:
        Valor de aptitud (mayor es mejor)
    """
    # Extraer parámetros
    extrusion_temp = params.get("extrusion_temp")
    extrusion_speed = params.get("extrusion_speed")
    cnc_cutting_speed = params.get("cnc_cutting_speed")
    cnc_cutting_depth = params.get("cnc_cutting_depth")
    inspection_time = params.get("inspection_time")
    inspection_points = params.get("inspection_points")
    finish_type = params.get("finish_type")
    
    # Cálculos simplificados para el ejemplo
    
    # Impacto en tiempo de producción
    time_factor = 1.0
    time_factor *= 1.0 - ((extrusion_speed - 10) / 80)  # Mayor velocidad, menor tiempo
    time_factor *= 1.0 - ((cnc_cutting_speed - 100) / 800)  # Mayor velocidad, menor tiempo
    time_factor *= 1.0 + ((cnc_cutting_depth - 0.5) / 5)  # Mayor profundidad, mayor tiempo
    time_factor *= inspection_time / 20.0  # Tiempo normalizado
    
    total_time = 180.0 * time_factor  # 180 minutos base
    
    # Impacto en costo
    cost_factor = 1.0
    cost_factor *= 1.0 + ((extrusion_temp - 180) / 140)  # Mayor temperatura, mayor costo energético
    cost_factor *= 1.0 - ((extrusion_speed - 10) / 100)  # Mayor velocidad, menor costo operativo
    cost_factor *= 1.0 - ((cnc_cutting_speed - 100) / 1000)  # Mayor velocidad, menor costo operativo
    cost_factor *= 1.0 + (finish_type - 1) / 4  # Mejor acabado, mayor costo
    
    total_cost = 200.0 * cost_factor  # 200 USD base
    
    # Impacto en calidad
    quality_factor = 0.7  # Base
    quality_factor += (250 - extrusion_temp) / 500  # Temperatura más baja tiende a mejor calidad
    quality_factor -= (extrusion_speed - 10) / 200  # Velocidad más baja tiende a mejor calidad
    quality_factor -= (cnc_cutting_speed - 100) / 2000  # Velocidad más baja tiende a mejor calidad
    quality_factor += (cnc_cutting_depth - 0.5) / 20  # Profundidad ideal depende del caso
    quality_factor += inspection_points / 100  # Más puntos, mejor inspección
    quality_factor += (finish_type - 1) / 10  # Mejor acabado, mejor calidad
    
    quality = max(0.0, min(1.0, quality_factor))  # Limitar entre 0 y 1
    
    # Calcular fitness combinando los tres factores
    # Normalizar cada factor (menor tiempo y costo es mejor, mayor calidad es mejor)
    norm_time = max(0, min(1, 1.0 - (total_time / 300)))  # 300 como tiempo máximo referencia
    norm_cost = max(0, min(1, 1.0 - (total_cost / 400)))  # 400 como costo máximo referencia
    norm_quality = quality
    
    # Pesos de cada factor
    w_time = 0.3
    w_cost = 0.3
    w_quality = 0.4
    
    # Fitness final
    fitness = (w_time * norm_time) + (w_cost * norm_cost) + (w_quality * norm_quality)
    
    return fitness

def optimize_process() -> Dict[str, Any]:
    """
    Optimiza un proceso de ejemplo.
    
    Returns:
        Resultados de la optimización
    """
    # Crear proceso
    process = create_example_process()
    
    # Validar proceso
    if not process.validate():
        logger.error("El proceso no es válido para optimización")
        return {"error": "Proceso inválido"}
    
    # Calcular ruta crítica
    critical_path, total_duration = process.get_critical_path()
    logger.info(f"Ruta crítica: {critical_path}, Duración total: {total_duration} minutos")
    
    # Obtener parámetros para optimización
    optimization_params = define_optimization_parameters(process)
    
    # Configurar optimizador genético
    optimizer = GeneticOptimizer(
        gene_ranges=optimization_params,
        fitness_function=fitness_function,
        population_size=50,
        elite_size=5,
        mutation_rate=0.1,
        crossover_rate=0.7,
        maximize=True
    )
    
    # Ejecutar optimización
    logger.info("Iniciando optimización...")
    optimization_result = optimizer.optimize(max_generations=100)
    
    # Obtener mejor solución
    best_individual = optimization_result["best_individual"]
    best_fitness = best_individual.fitness
    best_params = best_individual.genes
    
    logger.info(f"Optimización completada. Mejor fitness: {best_fitness:.4f}")
    logger.info(f"Mejores parámetros: {best_params}")
    
    # Evaluar la mejor solución para obtener métricas específicas
    time_factor = 1.0
    time_factor *= 1.0 - ((best_params["extrusion_speed"] - 10) / 80)
    time_factor *= 1.0 - ((best_params["cnc_cutting_speed"] - 100) / 800)
    time_factor *= 1.0 + ((best_params["cnc_cutting_depth"] - 0.5) / 5)
    time_factor *= best_params["inspection_time"] / 20.0
    
    optimized_time = 180.0 * time_factor
    
    cost_factor = 1.0
    cost_factor *= 1.0 + ((best_params["extrusion_temp"] - 180) / 140)
    cost_factor *= 1.0 - ((best_params["extrusion_speed"] - 10) / 100)
    cost_factor *= 1.0 - ((best_params["cnc_cutting_speed"] - 100) / 1000)
    cost_factor *= 1.0 + (best_params["finish_type"] - 1) / 4
    
    optimized_cost = 200.0 * cost_factor
    
    quality_factor = 0.7
    quality_factor += (250 - best_params["extrusion_temp"]) / 500
    quality_factor -= (best_params["extrusion_speed"] - 10) / 200
    quality_factor -= (best_params["cnc_cutting_speed"] - 100) / 2000
    quality_factor += (best_params["cnc_cutting_depth"] - 0.5) / 20
    quality_factor += best_params["inspection_points"] / 100
    quality_factor += (best_params["finish_type"] - 1) / 10
    
    optimized_quality = max(0.0, min(1.0, quality_factor))
    
    metrics = {
        "time": optimized_time,
        "cost": optimized_cost,
        "quality": optimized_quality
    }
    
    logger.info(f"Tiempo optimizado: {optimized_time:.2f} minutos")
    logger.info(f"Costo optimizado: {optimized_cost:.2f} USD")
    logger.info(f"Calidad optimizada: {optimized_quality:.4f}")
    
    # Registrar historial de la optimización
    generation_count = optimization_result["generations"]
    best_fitness_history = optimization_result["best_fitness_history"]
    avg_fitness_history = optimization_result["avg_fitness_history"]
    
    # Preparar resultado
    result = {
        "best_params": best_params,
        "best_fitness": best_fitness,
        "metrics": metrics,
        "history": {
            "generations": generation_count,
            "best_fitness": best_fitness_history,
            "avg_fitness": avg_fitness_history
        },
        "process": process
    }
    
    return result

def plot_optimization_results(results: Dict[str, Any]) -> None:
    """
    Visualiza los resultados de la optimización.
    
    Args:
        results: Resultados de la optimización
    """
    # Obtener datos del historial
    generations = results["history"]["generations"]
    best_fitness = results["history"]["best_fitness"]
    avg_fitness = results["history"]["avg_fitness"]
    
    # Crear figura
    plt.figure(figsize=(12, 10))
    
    # Gráfico de convergencia
    plt.subplot(2, 1, 1)
    x = list(range(len(best_fitness)))
    plt.plot(x, best_fitness, 'b-', label='Mejor fitness')
    plt.plot(x, avg_fitness, 'r-', label='Fitness promedio')
    plt.xlabel('Generación')
    plt.ylabel('Fitness')
    plt.title('Convergencia del algoritmo genético')
    plt.legend()
    plt.grid(True)
    
    # Gráfico de radar para métricas
    plt.subplot(2, 1, 2)
    
    # Datos para el radar
    metrics = results["metrics"]
    categories = ['Tiempo\n(inverso)', 'Costo\n(inverso)', 'Calidad']
    
    # Normalizar métricas (inverso para tiempo y costo)
    norm_time = max(0, min(1, 1.0 - (metrics["time"] / 300)))
    norm_cost = max(0, min(1, 1.0 - (metrics["cost"] / 400)))
    norm_quality = metrics["quality"]
    
    values = [norm_time, norm_cost, norm_quality]
    
    # Cerrar el polígono
    categories = [*categories, categories[0]]
    values = [*values, values[0]]
    
    # Configurar el radar
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    ax = plt.subplot(2, 1, 2, polar=True)
    plt.xticks(angles[:-1], categories[:-1], color='grey', size=10)
    ax.set_rlabel_position(0)
    plt.yticks([0.25, 0.5, 0.75], ["0.25", "0.5", "0.75"], color="grey", size=7)
    plt.ylim(0, 1)
    
    # Dibujar el polígono
    ax.plot(angles, values, linewidth=1, linestyle='solid')
    ax.fill(angles, values, 'b', alpha=0.1)
    
    plt.title('Métricas del proceso optimizado')
    
    # Guardar figura
    plt.tight_layout()
    plt.savefig('optimization_results.png')
    plt.close()
    
    logger.info("Gráficos generados y guardados como 'optimization_results.png'")

def main():
    """Función principal del ejemplo."""
    logger.info("Iniciando ejemplo de optimización de proceso productivo")
    
    # Optimizar proceso
    results = optimize_process()
    
    if "error" in results:
        logger.error(f"Error en la optimización: {results['error']}")
        return
    
    # Visualizar resultados
    plot_optimization_results(results)
    
    # Mostrar resumen final
    logger.info("Resumen de optimización:")
    logger.info(f"Mejor fitness: {results['best_fitness']:.4f}")
    logger.info(f"Tiempo optimizado: {results['metrics']['time']:.2f} minutos")
    logger.info(f"Costo optimizado: {results['metrics']['cost']:.2f} USD")
    logger.info(f"Calidad optimizada: {results['metrics']['quality']:.4f}")
    
    best_params = results["best_params"]
    logger.info("Mejores parámetros:")
    for param, value in best_params.items():
        logger.info(f"  {param}: {value}")
    
    logger.info("Ejemplo completado con éxito")

if __name__ == "__main__":
    main() 