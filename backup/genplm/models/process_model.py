"""
Modelo de Procesos Productivos para PLM en PYMES.

Este módulo define las estructuras de datos y lógica para representar
procesos productivos en pequeñas y medianas empresas, con un enfoque
en la flexibilidad y optimización.
"""

from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import json

@dataclass
class Resource:
    """Representa un recurso utilizado en un proceso productivo (máquina, herramienta, persona)."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = ""  # machine, tool, human, material
    cost_per_hour: float = 0.0
    availability: float = 1.0  # entre 0 y 1, porcentaje de tiempo disponible
    skills: List[str] = field(default_factory=list)  # habilidades o capacidades
    maintenance_schedule: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)  # propiedades adicionales
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el recurso a un diccionario para serialización."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "cost_per_hour": self.cost_per_hour,
            "availability": self.availability,
            "skills": self.skills,
            "maintenance_schedule": self.maintenance_schedule,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        """Crea un recurso a partir de un diccionario."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            type=data.get("type", ""),
            cost_per_hour=data.get("cost_per_hour", 0.0),
            availability=data.get("availability", 1.0),
            skills=data.get("skills", []),
            maintenance_schedule=data.get("maintenance_schedule", {}),
            properties=data.get("properties", {})
        )

@dataclass
class ProcessStep:
    """Representa un paso en un proceso productivo."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    required_resources: List[str] = field(default_factory=list)  # IDs de recursos necesarios
    duration_min: float = 0.0  # Duración mínima en minutos
    duration_max: float = 0.0  # Duración máxima en minutos
    cost: float = 0.0  # Costo directo del paso (materiales, etc.)
    input_parameters: Dict[str, Tuple] = field(default_factory=dict)  # Parámetros de entrada y sus rangos
    output_parameters: Dict[str, Any] = field(default_factory=dict)  # Parámetros de salida y sus valores esperados
    dependencies: List[str] = field(default_factory=list)  # IDs de pasos que deben completarse antes
    risk_factors: Dict[str, float] = field(default_factory=dict)  # Factores de riesgo y sus probabilidades
    quality_factors: Dict[str, float] = field(default_factory=dict)  # Factores de calidad y sus impactos
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el paso del proceso a un diccionario para serialización."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "required_resources": self.required_resources,
            "duration_min": self.duration_min,
            "duration_max": self.duration_max,
            "cost": self.cost,
            "input_parameters": self.input_parameters,
            "output_parameters": self.output_parameters,
            "dependencies": self.dependencies,
            "risk_factors": self.risk_factors,
            "quality_factors": self.quality_factors
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessStep':
        """Crea un paso del proceso a partir de un diccionario."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            required_resources=data.get("required_resources", []),
            duration_min=data.get("duration_min", 0.0),
            duration_max=data.get("duration_max", 0.0),
            cost=data.get("cost", 0.0),
            input_parameters=data.get("input_parameters", {}),
            output_parameters=data.get("output_parameters", {}),
            dependencies=data.get("dependencies", []),
            risk_factors=data.get("risk_factors", {}),
            quality_factors=data.get("quality_factors", {})
        )

@dataclass
class Product:
    """Representa un producto fabricado mediante un proceso productivo."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    creation_date: datetime = field(default_factory=datetime.now)
    components: List[Dict[str, Any]] = field(default_factory=list)  # Lista de componentes
    attributes: Dict[str, Any] = field(default_factory=dict)  # Atributos del producto
    quality_metrics: Dict[str, Tuple[float, float]] = field(default_factory=dict)  # Métricas de calidad (valor mínimo, valor máximo)
    cost_target: float = 0.0  # Costo objetivo
    formula: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # Fórmula del producto
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el producto a un diccionario para serialización."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "creation_date": self.creation_date.isoformat(),
            "components": self.components,
            "attributes": self.attributes,
            "quality_metrics": self.quality_metrics,
            "cost_target": self.cost_target,
            "formula": self.formula
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Crea un producto a partir de un diccionario."""
        creation_date = data.get("creation_date")
        if isinstance(creation_date, str):
            creation_date = datetime.fromisoformat(creation_date)
        else:
            creation_date = datetime.now()
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            creation_date=creation_date,
            components=data.get("components", []),
            attributes=data.get("attributes", {}),
            quality_metrics=data.get("quality_metrics", {}),
            cost_target=data.get("cost_target", 0.0),
            formula=data.get("formula", {})
        )

@dataclass
class Process:
    """Representa un proceso productivo completo."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    creation_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    product_id: str = ""  # ID del producto que se fabrica
    steps: List[ProcessStep] = field(default_factory=list)
    resources: Dict[str, Resource] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)  # Parámetros globales del proceso
    kpis: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # KPIs del proceso y sus objetivos
    
    def add_step(self, step: ProcessStep) -> None:
        """Añade un paso al proceso."""
        self.steps.append(step)
        self.last_modified = datetime.now()
    
    def add_resource(self, resource: Resource) -> None:
        """Añade un recurso al proceso."""
        self.resources[resource.id] = resource
        self.last_modified = datetime.now()
    
    def calculate_total_cost(self) -> float:
        """Calcula el costo total estimado del proceso."""
        # Costo de pasos directos
        step_costs = sum(step.cost for step in self.steps)
        
        # Costo de recursos por tiempo utilizado (estimación)
        resource_costs = 0.0
        for step in self.steps:
            duration_avg = (step.duration_min + step.duration_max) / 2 / 60  # Convertir a horas
            for resource_id in step.required_resources:
                if resource_id in self.resources:
                    resource_costs += self.resources[resource_id].cost_per_hour * duration_avg
        
        return step_costs + resource_costs
    
    def calculate_estimated_duration(self) -> timedelta:
        """Calcula la duración estimada total del proceso."""
        # Esta es una implementación simplificada que no tiene en cuenta dependencias o paralelismo
        total_minutes = 0.0
        for step in self.steps:
            # Usar el promedio de duración mínima y máxima
            total_minutes += (step.duration_min + step.duration_max) / 2
        
        return timedelta(minutes=total_minutes)
    
    def get_optimization_parameters(self) -> Dict[str, Tuple]:
        """
        Obtiene los parámetros que pueden ser optimizados en el proceso.
        
        Returns:
            Diccionario con nombres de parámetros y sus rangos (min, max) o valores posibles
        """
        optimization_params = {}
        
        # Obtener parámetros de todos los pasos
        for step in self.steps:
            for param_name, param_range in step.input_parameters.items():
                # Usar ID del paso como prefijo para evitar colisiones
                full_param_name = f"{step.id}_{param_name}"
                optimization_params[full_param_name] = param_range
        
        # Añadir parámetros globales del proceso
        for param_name, param_value in self.parameters.items():
            if isinstance(param_value, dict) and "range" in param_value:
                optimization_params[param_name] = param_value["range"]
        
        return optimization_params
    
    def apply_optimized_parameters(self, optimized_params: Dict[str, Any]) -> None:
        """
        Aplica los parámetros optimizados al proceso.
        
        Args:
            optimized_params: Diccionario con nombres de parámetros y sus valores optimizados
        """
        # Aplicar parámetros a pasos
        for param_name, param_value in optimized_params.items():
            if "_" in param_name:
                # Parámetro de un paso
                step_id, step_param = param_name.split("_", 1)
                for step in self.steps:
                    if step.id == step_id and step_param in step.input_parameters:
                        step.input_parameters[step_param] = (param_value, param_value)  # Convertir a rango fijo
            else:
                # Parámetro global
                if param_name in self.parameters:
                    if isinstance(self.parameters[param_name], dict):
                        self.parameters[param_name]["value"] = param_value
                    else:
                        self.parameters[param_name] = param_value
        
        self.last_modified = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el proceso a un diccionario para serialización."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "creation_date": self.creation_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "product_id": self.product_id,
            "steps": [step.to_dict() for step in self.steps],
            "resources": {k: v.to_dict() for k, v in self.resources.items()},
            "parameters": self.parameters,
            "kpis": self.kpis
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Process':
        """Crea un proceso a partir de un diccionario."""
        creation_date = data.get("creation_date")
        if isinstance(creation_date, str):
            creation_date = datetime.fromisoformat(creation_date)
        else:
            creation_date = datetime.now()
        
        last_modified = data.get("last_modified")
        if isinstance(last_modified, str):
            last_modified = datetime.fromisoformat(last_modified)
        else:
            last_modified = datetime.now()
        
        process = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            creation_date=creation_date,
            last_modified=last_modified,
            product_id=data.get("product_id", ""),
            parameters=data.get("parameters", {}),
            kpis=data.get("kpis", {})
        )
        
        # Añadir recursos
        for resource_id, resource_data in data.get("resources", {}).items():
            process.resources[resource_id] = Resource.from_dict(resource_data)
        
        # Añadir pasos
        for step_data in data.get("steps", []):
            process.steps.append(ProcessStep.from_dict(step_data))
        
        return process
    
    def to_json(self, filepath: str) -> None:
        """Guarda el proceso en un archivo JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_json(cls, filepath: str) -> 'Process':
        """Carga un proceso desde un archivo JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

# Ejemplo de definición de métricas de calidad para procesos
QUALITY_METRICS = {
    "efficiency": {
        "description": "Eficiencia del proceso (output/input)",
        "unit": "ratio",
        "target_min": 0.7,
        "target_max": 1.0,
        "weight": 0.3
    },
    "defect_rate": {
        "description": "Tasa de defectos en productos finales",
        "unit": "percentage",
        "target_min": 0.0,
        "target_max": 0.05,
        "weight": 0.2
    },
    "cycle_time": {
        "description": "Tiempo total del ciclo productivo",
        "unit": "hours",
        "target_min": None,
        "target_max": 48.0,
        "weight": 0.2
    },
    "resource_utilization": {
        "description": "Porcentaje de utilización de recursos",
        "unit": "percentage",
        "target_min": 0.6,
        "target_max": 0.9,
        "weight": 0.15
    },
    "energy_consumption": {
        "description": "Consumo energético por unidad producida",
        "unit": "kWh/unit",
        "target_min": None,
        "target_max": 50.0,
        "weight": 0.15
    }
} 