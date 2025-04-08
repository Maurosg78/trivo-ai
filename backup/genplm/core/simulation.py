"""
Sistema de simulación para evaluar soluciones en entornos productivos.

Este módulo proporciona capacidades para simular y evaluar diferentes
configuraciones de productos y procesos antes de su implementación real.
"""

import numpy as np
import random
import logging
import time
from typing import Dict, List, Tuple, Any, Optional, Callable, Union
from dataclasses import dataclass, field

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('genplm.simulation')

@dataclass
class SimulationResult:
    """
    Almacena los resultados de una simulación.
    
    Attributes:
        metrics: Diccionario con las métricas resultantes
        events: Lista de eventos ocurridos durante la simulación
        duration: Duración de la simulación en segundos
        success: Indica si la simulación se completó correctamente
    """
    metrics: Dict[str, float]
    events: List[Dict[str, Any]] = field(default_factory=list)
    duration: float = 0.0
    success: bool = True
    
    def get_metric(self, name: str, default: float = 0.0) -> float:
        """Obtiene el valor de una métrica específica."""
        return self.metrics.get(name, default)
    
    def add_event(self, event_type: str, timestamp: float, data: Dict[str, Any]) -> None:
        """Agrega un evento al registro de la simulación."""
        self.events.append({
            "type": event_type,
            "timestamp": timestamp,
            "data": data
        })
    
    def summary(self) -> str:
        """Genera un resumen de los resultados de la simulación."""
        lines = [
            f"Resultado de simulación ({'Exitoso' if self.success else 'Fallido'})",
            f"Duración: {self.duration:.2f} segundos",
            "Métricas principales:"
        ]
        
        for key, value in self.metrics.items():
            lines.append(f"  - {key}: {value:.4f}")
            
        return "\n".join(lines)

class Simulator:
    """
    Clase base para implementar diferentes tipos de simuladores.
    
    Un simulador evalúa el comportamiento y rendimiento de una solución
    en un entorno virtual antes de su implementación real.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        random_seed: Optional[int] = None
    ):
        """
        Inicializa el simulador con configuración básica.
        
        Args:
            config: Diccionario con la configuración del simulador
            random_seed: Semilla para generador de números aleatorios
        """
        self.config = config
        self.random_seed = random_seed
        
        # Inicializar generador de números aleatorios
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)
            
        # Estado de la simulación
        self.current_time = 0.0
        self.events = []
        
        logger.info(f"Inicializado simulador con configuración: {config}")
    
    def run(
        self,
        solution: Dict[str, Any],
        duration: float = 100.0,
        real_time: bool = False
    ) -> SimulationResult:
        """
        Ejecuta la simulación con una solución específica.
        
        Args:
            solution: Solución a evaluar en la simulación
            duration: Duración máxima de la simulación
            real_time: Si True, la simulación se ejecuta en tiempo real
            
        Returns:
            Resultado de la simulación
        """
        # Establecer estado inicial
        start_time = time.time()
        self.current_time = 0.0
        self.events = []
        
        try:
            # Preparar la simulación
            self._setup(solution)
            
            # Bucle principal de simulación
            while self.current_time < duration:
                # Actualizar paso de simulación
                delta_time = self._calculate_time_step()
                
                # Si es tiempo real, esperar el tiempo correspondiente
                if real_time:
                    time.sleep(delta_time)
                
                # Actualizar estado de la simulación
                self._update(delta_time)
                
                # Verificar condiciones de finalización anticipada
                if self._should_terminate():
                    logger.info(f"Simulación terminada anticipadamente en t={self.current_time:.2f}")
                    break
                
                # Avanzar el tiempo de simulación
                self.current_time += delta_time
            
            # Calcular métricas finales
            metrics = self._calculate_metrics()
            
            # Tiempo real de ejecución
            elapsed_time = time.time() - start_time
            
            # Crear resultado
            result = SimulationResult(
                metrics=metrics,
                events=self.events.copy(),
                duration=elapsed_time,
                success=True
            )
            
            logger.info(f"Simulación completada en {elapsed_time:.2f}s (tiempo simulado: {self.current_time:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error durante la simulación: {e}")
            
            # Tiempo real de ejecución hasta el error
            elapsed_time = time.time() - start_time
            
            # Crear resultado con estado de error
            return SimulationResult(
                metrics={},
                events=self.events.copy(),
                duration=elapsed_time,
                success=False
            )
    
    def _setup(self, solution: Dict[str, Any]) -> None:
        """
        Configura el estado inicial de la simulación.
        
        Args:
            solution: Solución a evaluar
        """
        # Implementación específica del simulador derivado
        pass
    
    def _calculate_time_step(self) -> float:
        """
        Calcula el incremento de tiempo para el siguiente paso.
        
        Returns:
            Delta de tiempo para el siguiente paso
        """
        # Por defecto, usar paso fijo
        return self.config.get("time_step", 1.0)
    
    def _update(self, delta_time: float) -> None:
        """
        Actualiza el estado de la simulación para un paso de tiempo.
        
        Args:
            delta_time: Incremento de tiempo
        """
        # Implementación específica del simulador derivado
        pass
    
    def _should_terminate(self) -> bool:
        """
        Verifica si la simulación debe terminar antes de la duración máxima.
        
        Returns:
            True si la simulación debe terminar, False en caso contrario
        """
        # Por defecto, no terminar anticipadamente
        return False
    
    def _calculate_metrics(self) -> Dict[str, float]:
        """
        Calcula las métricas finales de la simulación.
        
        Returns:
            Diccionario con métricas calculadas
        """
        # Implementación específica del simulador derivado
        return {}
    
    def add_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Registra un evento durante la simulación.
        
        Args:
            event_type: Tipo de evento
            data: Datos asociados al evento
        """
        self.events.append({
            "type": event_type,
            "timestamp": self.current_time,
            "data": data
        })
        
        logger.debug(f"Evento en t={self.current_time:.2f}: {event_type}")

class ProductionSimulator(Simulator):
    """
    Simula un entorno de producción para evaluar recetas y parámetros.
    
    Este simulador modela un entorno de producción con variables aleatorias
    para simular variaciones en las condiciones reales de fabricación.
    """
    
    def __init__(self, config: Dict[str, Any], random_seed: Optional[int] = None):
        """
        Inicializa el simulador de producción.
        
        Args:
            config: Configuración del simulador
            random_seed: Semilla para generador de números aleatorios
        """
        super().__init__(config, random_seed)
        
        # Parámetros específicos de producción
        self.variation_factor = config.get("variation_factor", 0.05)  # Variación en condiciones
        self.failure_probability = config.get("failure_probability", 0.01)  # Prob. de fallo por paso
        
        # Estado de producción
        self.production_rate = 0.0
        self.quality_score = 1.0
        self.resource_usage = {}
        self.failures = []
        
    def _setup(self, solution: Dict[str, Any]) -> None:
        """
        Prepara la simulación con la solución específica.
        
        Args:
            solution: Parámetros de la receta o proceso a simular
        """
        # Inicializar métricas
        self.production_rate = self.config.get("base_production_rate", 10.0)
        self.quality_score = 1.0
        
        # Inicializar recursos
        self.resource_usage = {
            resource: 0.0 for resource in self.config.get("resources", [])
        }
        
        # Registrar estado inicial
        self.add_event("setup", {
            "initial_parameters": solution,
            "production_rate": self.production_rate
        })
        
        logger.info(f"Simulación de producción iniciada con solución: {solution}")
    
    def _update(self, delta_time: float) -> None:
        """
        Actualiza el estado de la producción para un paso de tiempo.
        
        Args:
            delta_time: Incremento de tiempo
        """
        # Aplicar variación aleatoria a la tasa de producción
        variation = 1.0 + random.uniform(-self.variation_factor, self.variation_factor)
        self.production_rate *= variation
        
        # Simular posibles fallos aleatorios
        if random.random() < self.failure_probability * delta_time:
            failure_type = random.choice(["equipment", "material", "human", "power"])
            severity = random.uniform(0.1, 0.5)
            
            # Registrar fallo
            self.failures.append({
                "type": failure_type,
                "time": self.current_time,
                "severity": severity
            })
            
            # Impacto en producción y calidad
            self.production_rate *= (1.0 - severity)
            self.quality_score *= (1.0 - severity * 0.5)
            
            # Registrar evento
            self.add_event("failure", {
                "type": failure_type,
                "severity": severity,
                "new_rate": self.production_rate,
                "new_quality": self.quality_score
            })
            
            logger.warning(f"Fallo de {failure_type} en t={self.current_time:.2f} con severidad {severity:.2f}")
        
        # Actualizar uso de recursos
        for resource in self.resource_usage:
            # Consumo proporcional a la tasa de producción
            consumption = self.production_rate * delta_time * self.config.get(f"{resource}_factor", 1.0)
            self.resource_usage[resource] += consumption
        
        # Registrar métricas periódicas (cada 10 unidades de tiempo)
        if int(self.current_time / 10) != int((self.current_time - delta_time) / 10):
            self.add_event("metrics", {
                "time": self.current_time,
                "production_rate": self.production_rate,
                "quality_score": self.quality_score,
                "resource_usage": {k: v for k, v in self.resource_usage.items()}
            })
    
    def _should_terminate(self) -> bool:
        """
        Determina si la simulación debe terminar anticipadamente.
        
        Returns:
            True si la calidad o producción caen por debajo del umbral crítico
        """
        # Terminar si la calidad cae por debajo del umbral crítico
        quality_threshold = self.config.get("min_quality_threshold", 0.3)
        if self.quality_score < quality_threshold:
            logger.warning(f"Simulación terminada por baja calidad: {self.quality_score:.2f}")
            return True
        
        # Terminar si la producción cae por debajo del umbral crítico
        production_threshold = self.config.get("min_production_threshold", 1.0)
        if self.production_rate < production_threshold:
            logger.warning(f"Simulación terminada por baja producción: {self.production_rate:.2f}")
            return True
        
        return False
    
    def _calculate_metrics(self) -> Dict[str, float]:
        """
        Calcula las métricas finales de la simulación de producción.
        
        Returns:
            Diccionario con métricas de producción, calidad, eficiencia y costos
        """
        # Producción total
        total_production = self.production_rate * self.current_time
        
        # Costo total de recursos
        total_cost = sum(
            amount * self.config.get(f"{resource}_cost", 1.0)
            for resource, amount in self.resource_usage.items()
        )
        
        # Eficiencia de producción (producción / costo)
        efficiency = total_production / max(total_cost, 0.001)
        
        # Tasa de fallos
        failure_rate = len(self.failures) / max(self.current_time, 0.001)
        
        # Impacto de fallos en calidad
        quality_impact = sum(failure["severity"] for failure in self.failures)
        
        # Recopilar métricas
        metrics = {
            "total_production": total_production,
            "average_production_rate": total_production / self.current_time,
            "final_quality_score": self.quality_score,
            "total_cost": total_cost,
            "production_efficiency": efficiency,
            "failure_rate": failure_rate,
            "quality_impact": quality_impact
        }
        
        # Agregar métricas de recursos
        for resource, amount in self.resource_usage.items():
            metrics[f"{resource}_usage"] = amount
            metrics[f"{resource}_cost"] = amount * self.config.get(f"{resource}_cost", 1.0)
        
        return metrics

def run_simulation_batch(
    simulator: Simulator,
    solutions: List[Dict[str, Any]],
    duration: float = 100.0,
    parallel: bool = False
) -> List[SimulationResult]:
    """
    Ejecuta simulaciones para múltiples soluciones.
    
    Args:
        simulator: Instancia del simulador a utilizar
        solutions: Lista de soluciones a evaluar
        duration: Duración de cada simulación
        parallel: Si True, ejecuta simulaciones en paralelo
        
    Returns:
        Lista con los resultados de cada simulación
    """
    results = []
    start_time = time.time()
    
    logger.info(f"Iniciando lote de {len(solutions)} simulaciones")
    
    if parallel:
        # Implementación paralela (requiere módulos adicionales)
        try:
            import concurrent.futures
            
            with concurrent.futures.ProcessPoolExecutor() as executor:
                # Crear nuevas instancias de simulador para cada proceso
                sim_configs = [(simulator.config, i) for i in range(len(solutions))]
                simulators = [
                    simulator.__class__(config, seed) 
                    for config, seed in sim_configs
                ]
                
                # Lanzar simulaciones en paralelo
                futures = [
                    executor.submit(sim.run, solution, duration, False)
                    for sim, solution in zip(simulators, solutions)
                ]
                
                # Recoger resultados
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
                    
                # Ordenar resultados según orden original
                results = sorted(results, key=lambda r: futures.index(r))
                
        except ImportError:
            logger.warning("No se pudo importar módulo concurrent.futures. Ejecutando en secuencial.")
            parallel = False
    
    if not parallel:
        # Ejecución secuencial
        for i, solution in enumerate(solutions):
            logger.info(f"Ejecutando simulación {i+1}/{len(solutions)}")
            result = simulator.run(solution, duration)
            results.append(result)
    
    elapsed_time = time.time() - start_time
    logger.info(f"Lote de simulaciones completado en {elapsed_time:.2f}s")
    
    return results 