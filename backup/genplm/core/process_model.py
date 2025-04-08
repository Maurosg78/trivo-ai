"""
Modelado de procesos para optimización en entornos PLM.

Este módulo proporciona las clases base para modelar procesos
productivos que serán optimizados con algoritmos genéticos.
"""

from typing import Dict, List, Tuple, Any, Optional, Union, Set
from dataclasses import dataclass, field
import numpy as np
import json
import logging
import time
from datetime import datetime
from enum import Enum, auto

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('genplm.process')

class ResourceType(Enum):
    """Tipos de recursos disponibles en el sistema."""
    MACHINE = auto()
    HUMAN = auto()
    TOOL = auto()
    MATERIAL = auto()
    ENERGY = auto()
    SPACE = auto()
    
    def __str__(self):
        return self.name.lower()

class ProcessType(Enum):
    """Tipos de procesos soportados."""
    MANUFACTURING = auto()
    ASSEMBLY = auto()
    QUALITY_CONTROL = auto()
    PACKAGING = auto()
    LOGISTICS = auto()
    MAINTENANCE = auto()
    
    def __str__(self):
        return self.name.lower()

@dataclass
class Resource:
    """
    Representa un recurso utilizado en un proceso productivo.
    
    Attributes:
        id: Identificador único del recurso
        name: Nombre descriptivo del recurso
        type: Tipo de recurso (máquina, humano, etc.)
        capacity: Capacidad disponible del recurso
        cost_per_hour: Costo por hora de uso
        efficiency: Factor de eficiencia (0.0-1.0)
        maintenance_schedule: Programa de mantenimiento (horas)
        attributes: Atributos adicionales específicos
    """
    id: str
    name: str
    type: ResourceType
    capacity: float = 1.0
    cost_per_hour: float = 0.0
    efficiency: float = 1.0
    maintenance_schedule: Optional[int] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el recurso a un diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'type': str(self.type),
            'capacity': self.capacity,
            'cost_per_hour': self.cost_per_hour,
            'efficiency': self.efficiency,
            'maintenance_schedule': self.maintenance_schedule,
            'attributes': self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        """Crea un recurso a partir de un diccionario."""
        resource_type = next(rt for rt in ResourceType if str(rt) == data['type'])
        
        return cls(
            id=data['id'],
            name=data['name'],
            type=resource_type,
            capacity=data.get('capacity', 1.0),
            cost_per_hour=data.get('cost_per_hour', 0.0),
            efficiency=data.get('efficiency', 1.0),
            maintenance_schedule=data.get('maintenance_schedule'),
            attributes=data.get('attributes', {})
        )

@dataclass
class ProcessStep:
    """
    Representa un paso en un proceso productivo.
    
    Attributes:
        id: Identificador único del paso
        name: Nombre descriptivo del paso
        duration: Duración en minutos
        resources: Recursos requeridos por el paso
        predecessors: IDs de pasos que deben completarse antes
        outputs: Resultados producidos por el paso
        quality_factors: Factores que afectan la calidad
        failure_rate: Tasa de fallos (0.0-1.0)
        cost: Costo fijo del paso
        optional: Si el paso es opcional
    """
    id: str
    name: str
    duration: float
    resources: List[Tuple[str, float]] = field(default_factory=list)  # (resource_id, amount)
    predecessors: List[str] = field(default_factory=list)
    outputs: Dict[str, float] = field(default_factory=dict)  # (output_id, amount)
    quality_factors: Dict[str, float] = field(default_factory=dict)
    failure_rate: float = 0.0
    cost: float = 0.0
    optional: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el paso a un diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'duration': self.duration,
            'resources': self.resources,
            'predecessors': self.predecessors,
            'outputs': self.outputs,
            'quality_factors': self.quality_factors,
            'failure_rate': self.failure_rate,
            'cost': self.cost,
            'optional': self.optional
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessStep':
        """Crea un paso a partir de un diccionario."""
        return cls(
            id=data['id'],
            name=data['name'],
            duration=data['duration'],
            resources=data.get('resources', []),
            predecessors=data.get('predecessors', []),
            outputs=data.get('outputs', {}),
            quality_factors=data.get('quality_factors', {}),
            failure_rate=data.get('failure_rate', 0.0),
            cost=data.get('cost', 0.0),
            optional=data.get('optional', False)
        )
    
    def get_total_cost(self, resource_map: Dict[str, Resource]) -> float:
        """
        Calcula el costo total del paso.
        
        Args:
            resource_map: Diccionario de recursos por ID
            
        Returns:
            Costo total del paso (fijo + recursos)
        """
        # Costo fijo
        total = self.cost
        
        # Costo de recursos
        for resource_id, amount in self.resources:
            if resource_id in resource_map:
                resource = resource_map[resource_id]
                # Convertir duración a horas para el cálculo
                hours = self.duration / 60.0
                total += resource.cost_per_hour * hours * amount
        
        return total

@dataclass
class Process:
    """
    Representa un proceso completo con múltiples pasos.
    
    Attributes:
        id: Identificador único del proceso
        name: Nombre descriptivo del proceso
        type: Tipo de proceso
        steps: Pasos que componen el proceso
        resources: Recursos disponibles para el proceso
        inputs: Materiales o recursos de entrada
        outputs: Productos o resultados de salida
        constraints: Restricciones del proceso
        kpis: Indicadores clave de rendimiento
    """
    id: str
    name: str
    type: ProcessType
    steps: List[ProcessStep] = field(default_factory=list)
    resources: Dict[str, Resource] = field(default_factory=dict)
    inputs: Dict[str, float] = field(default_factory=dict)
    outputs: Dict[str, float] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    kpis: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, step: ProcessStep) -> None:
        """
        Añade un paso al proceso.
        
        Args:
            step: Paso a añadir
        """
        # Verificar que no exista otro paso con el mismo ID
        if any(s.id == step.id for s in self.steps):
            raise ValueError(f"Ya existe un paso con ID {step.id}")
        
        # Verificar que los predecesores existen
        for pred_id in step.predecessors:
            if not any(s.id == pred_id for s in self.steps):
                raise ValueError(f"El predecesor {pred_id} no existe en el proceso")
        
        self.steps.append(step)
    
    def add_resource(self, resource: Resource) -> None:
        """
        Añade un recurso al proceso.
        
        Args:
            resource: Recurso a añadir
        """
        if resource.id in self.resources:
            raise ValueError(f"Ya existe un recurso con ID {resource.id}")
        
        self.resources[resource.id] = resource
    
    def validate(self) -> bool:
        """
        Valida que el proceso sea coherente y viable.
        
        Returns:
            True si el proceso es válido
        """
        # Verificar que no hay ciclos en las dependencias
        try:
            self._check_cycles()
        except ValueError as e:
            logger.error(f"Validación fallida: {e}")
            return False
        
        # Verificar que todos los recursos referenciados existen
        for step in self.steps:
            for resource_id, _ in step.resources:
                if resource_id not in self.resources:
                    logger.error(f"El paso {step.id} requiere el recurso {resource_id} que no existe")
                    return False
        
        # Verificar entradas y salidas
        all_outputs = set()
        for step in self.steps:
            all_outputs.update(step.outputs.keys())
        
        for output_id in self.outputs:
            if output_id not in all_outputs:
                logger.error(f"El output {output_id} no es producido por ningún paso")
                return False
        
        return True
    
    def _check_cycles(self) -> None:
        """
        Verifica que no haya ciclos en las dependencias entre pasos.
        
        Raises:
            ValueError: Si se detecta un ciclo
        """
        # Construir grafo de dependencias
        graph = {step.id: set(step.predecessors) for step in self.steps}
        
        # Detectar ciclos con DFS
        visited = set()
        temp_visited = set()
        
        def has_cycle(node):
            if node in temp_visited:
                return True
            
            if node in visited:
                return False
            
            temp_visited.add(node)
            
            for neighbor in graph.get(node, set()):
                if has_cycle(neighbor):
                    return True
            
            temp_visited.remove(node)
            visited.add(node)
            return False
        
        # Comprobar cada nodo
        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    raise ValueError(f"Se detectó un ciclo en las dependencias que involucra a {node}")
    
    def get_critical_path(self) -> Tuple[List[str], float]:
        """
        Calcula la ruta crítica del proceso.
        
        Returns:
            Tupla con (lista de IDs de pasos en la ruta crítica, duración total)
        """
        # Algoritmo forward-backward pass
        
        # Earliest start/finish times
        earliest_start = {}
        earliest_finish = {}
        
        # Calcular earliest times (forward pass)
        sorted_steps = self._topological_sort()
        
        for step in sorted_steps:
            if not step.predecessors:
                earliest_start[step.id] = 0
            else:
                earliest_start[step.id] = max(earliest_finish[pred] for pred in step.predecessors)
            
            earliest_finish[step.id] = earliest_start[step.id] + step.duration
        
        # Latest start/finish times
        latest_start = {}
        latest_finish = {}
        
        # Calcular latest times (backward pass)
        completion_time = max(earliest_finish.values())
        
        for step in reversed(sorted_steps):
            # Encontrar sucesores
            successors = []
            for s in self.steps:
                if step.id in s.predecessors:
                    successors.append(s.id)
            
            if not successors:
                latest_finish[step.id] = completion_time
            else:
                latest_finish[step.id] = min(latest_start[succ] for succ in successors)
            
            latest_start[step.id] = latest_finish[step.id] - step.duration
        
        # Calcular holguras
        slacks = {step.id: latest_start[step.id] - earliest_start[step.id] for step in self.steps}
        
        # La ruta crítica consiste en los pasos con holgura cero
        critical_path = [step.id for step in self.steps if slacks[step.id] < 1e-6]
        
        return critical_path, completion_time
    
    def _topological_sort(self) -> List[ProcessStep]:
        """
        Ordena los pasos topológicamente (respetando dependencias).
        
        Returns:
            Lista ordenada de pasos
        """
        # Construir grafo de dependencias
        graph = {step.id: set(step.predecessors) for step in self.steps}
        
        # Mapeo de IDs a objetos Step
        id_to_step = {step.id: step for step in self.steps}
        
        # Algoritmo de Kahn para ordenamiento topológico
        result = []
        no_incoming = [step.id for step in self.steps if not step.predecessors]
        
        while no_incoming:
            n = no_incoming.pop(0)
            result.append(id_to_step[n])
            
            # Para cada nodo que tiene a n como predecesor
            for step in self.steps:
                if n in step.predecessors:
                    # Eliminar la dependencia
                    new_preds = [p for p in step.predecessors if p != n]
                    
                    # Si no quedan predecesores, agregar a la lista
                    if not new_preds:
                        no_incoming.append(step.id)
        
        # Verificar que se incluyeron todos los nodos
        if len(result) != len(self.steps):
            raise ValueError("El grafo tiene ciclos, no se puede ordenar topológicamente")
        
        return result
    
    def calculate_total_cost(self) -> float:
        """
        Calcula el costo total del proceso.
        
        Returns:
            Costo total
        """
        return sum(step.get_total_cost(self.resources) for step in self.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el proceso a un diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'type': str(self.type),
            'steps': [step.to_dict() for step in self.steps],
            'resources': {k: v.to_dict() for k, v in self.resources.items()},
            'inputs': self.inputs,
            'outputs': self.outputs,
            'constraints': self.constraints,
            'kpis': self.kpis
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Process':
        """Crea un proceso a partir de un diccionario."""
        process_type = next(pt for pt in ProcessType if str(pt) == data['type'])
        
        process = cls(
            id=data['id'],
            name=data['name'],
            type=process_type,
            inputs=data.get('inputs', {}),
            outputs=data.get('outputs', {}),
            constraints=data.get('constraints', {}),
            kpis=data.get('kpis', {})
        )
        
        # Añadir recursos
        for resource_data in data.get('resources', {}).values():
            process.add_resource(Resource.from_dict(resource_data))
        
        # Añadir pasos
        for step_data in data.get('steps', []):
            process.add_step(ProcessStep.from_dict(step_data))
        
        return process
    
    def save_to_file(self, filename: str) -> None:
        """
        Guarda el proceso a un archivo JSON.
        
        Args:
            filename: Ruta del archivo
        """
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'Process':
        """
        Carga un proceso desde un archivo JSON.
        
        Args:
            filename: Ruta del archivo
            
        Returns:
            Proceso cargado
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data)

class ProcessOptimizer:
    """
    Clase base para optimizadores de procesos.
    
    Esta clase proporciona la estructura básica para implementar
    algoritmos de optimización de procesos productivos.
    """
    
    def __init__(self, process: Process):
        """
        Inicializa el optimizador.
        
        Args:
            process: Proceso a optimizar
        """
        self.process = process
        
        # Verificar que el proceso es válido
        if not process.validate():
            raise ValueError("El proceso no es válido para optimización")
    
    def optimize(self, **kwargs) -> Dict[str, Any]:
        """
        Método abstracto para optimizar el proceso.
        
        Args:
            **kwargs: Parámetros de optimización
            
        Returns:
            Resultados de la optimización
        """
        raise NotImplementedError("Debe ser implementado por una subclase")
    
    def evaluate(self, solution: Any) -> Dict[str, float]:
        """
        Evalúa una solución candidata.
        
        Args:
            solution: Solución a evaluar
            
        Returns:
            Diccionario con valores de los objetivos
        """
        raise NotImplementedError("Debe ser implementado por una subclase")

class ResourceAllocation:
    """
    Gestor de asignación de recursos para simulación de procesos.
    """
    
    def __init__(self, resources: Dict[str, Resource]):
        """
        Inicializa el gestor de recursos.
        
        Args:
            resources: Diccionario de recursos disponibles
        """
        self.resources = resources
        self.available = {id: resource.capacity for id, resource in resources.items()}
    
    def allocate(self, resource_id: str, amount: float) -> bool:
        """
        Asigna recursos si hay disponibilidad.
        
        Args:
            resource_id: ID del recurso
            amount: Cantidad a asignar
            
        Returns:
            True si la asignación fue exitosa
        """
        if resource_id not in self.available:
            return False
        
        if self.available[resource_id] < amount:
            return False
        
        self.available[resource_id] -= amount
        return True
    
    def release(self, resource_id: str, amount: float) -> None:
        """
        Libera recursos previamente asignados.
        
        Args:
            resource_id: ID del recurso
            amount: Cantidad a liberar
        """
        if resource_id in self.available:
            self.available[resource_id] += amount
    
    def get_availability(self, resource_id: str) -> float:
        """
        Obtiene la disponibilidad actual de un recurso.
        
        Args:
            resource_id: ID del recurso
            
        Returns:
            Cantidad disponible
        """
        return self.available.get(resource_id, 0.0)
    
    def reset(self) -> None:
        """Reinicia las disponibilidades a sus valores iniciales."""
        self.available = {id: resource.capacity for id, resource in self.resources.items()}

@dataclass
class SimulationEvent:
    """
    Evento para simulación de procesos.
    
    Attributes:
        time: Momento de ocurrencia
        type: Tipo de evento
        step_id: ID del paso relacionado
        data: Datos adicionales del evento
    """
    time: float
    type: str  # 'start', 'finish', 'failure'
    step_id: str
    data: Dict[str, Any] = field(default_factory=dict)

class ProcessSimulator:
    """
    Simulador de procesos para evaluar desempeño.
    """
    
    def __init__(self, process: Process):
        """
        Inicializa el simulador.
        
        Args:
            process: Proceso a simular
        """
        self.process = process
        self.events = []
        self.current_time = 0.0
        self.resource_manager = ResourceAllocation(process.resources)
        self.step_states = {}  # Por definir
    
    def reset(self) -> None:
        """Reinicia el estado del simulador."""
        self.events = []
        self.current_time = 0.0
        self.resource_manager.reset()
        self.step_states = {}
    
    def run_simulation(self, 
                      max_time: float = float('inf'), 
                      seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Ejecuta una simulación del proceso.
        
        Args:
            max_time: Tiempo máximo de simulación
            seed: Semilla para generador aleatorio
            
        Returns:
            Resultados de la simulación
        """
        raise NotImplementedError("Implementar en subclase específica")
    
    def get_execution_times(self) -> Dict[str, Tuple[float, float]]:
        """
        Obtiene los tiempos de inicio y fin de cada paso.
        
        Returns:
            Diccionario con pares (tiempo_inicio, tiempo_fin)
        """
        start_times = {}
        end_times = {}
        
        for event in self.events:
            if event.type == 'start':
                start_times[event.step_id] = event.time
            elif event.type == 'finish':
                end_times[event.step_id] = event.time
        
        return {
            step_id: (start_times.get(step_id, 0.0), end_times.get(step_id, 0.0))
            for step_id in set(start_times.keys()) | set(end_times.keys())
        }
    
    def calculate_kpis(self) -> Dict[str, float]:
        """
        Calcula los KPIs basados en la simulación.
        
        Returns:
            Diccionario con valores de KPI
        """
        # Implementar cálculos específicos de KPI
        execution_times = self.get_execution_times()
        
        # Tiempo total
        if execution_times:
            total_time = max(end for _, end in execution_times.values())
        else:
            total_time = 0.0
        
        # Utilización de recursos
        # TODO: Implementar cálculo de utilización
        
        return {
            'total_time': total_time,
            'total_cost': self.process.calculate_total_cost(),
            # Otros KPIs
        } 