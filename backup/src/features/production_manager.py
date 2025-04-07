from typing import Dict, List

from pydantic import BaseModel


class ProductionEquipment(BaseModel):
    name: str
    capacity: float
    cost: float
    energy_consumption: float
    maintenance_frequency: str


class ProductionProcess(BaseModel):
    steps: List[Dict[str, str]]
    temperature_requirements: Dict[str, float]
    time_requirements: Dict[str, float]
    equipment_needed: List[str]


class ProductionManager:
    def __init__(self):
        self.equipment_db = self._load_equipment()
        self.process_templates = self._load_process_templates()

    def _load_equipment(self) -> Dict[str, ProductionEquipment]:
        """
        Cargar base de datos de equipamiento
        """
        return {
            "mixer": ProductionEquipment(
                name="Mixer Industrial",
                capacity=50.0,  # kg
                cost=5000.0,
                energy_consumption=2.5,  # kW
                maintenance_frequency="monthly",
            ),
            "kneader": ProductionEquipment(
                name="Amasadora",
                capacity=30.0,
                cost=8000.0,
                energy_consumption=3.0,
                maintenance_frequency="weekly",
            ),
            "proofer": ProductionEquipment(
                name="Fermentadora",
                capacity=100.0,
                cost=12000.0,
                energy_consumption=1.5,
                maintenance_frequency="monthly",
            ),
            "baker": ProductionEquipment(
                name="Horno Industrial",
                capacity=200.0,
                cost=15000.0,
                energy_consumption=5.0,
                maintenance_frequency="weekly",
            ),
        }

    def _load_process_templates(self) -> Dict[str, ProductionProcess]:
        """
        Cargar plantillas de procesos de producción
        """
        return {
            "pizza": ProductionProcess(
                steps=[
                    {"name": "Mezclado", "description": "Mezclar ingredientes secos y húmedos"},
                    {"name": "Amasado", "description": "Amasar hasta obtener la textura deseada"},
                    {"name": "Fermentación", "description": "Dejar fermentar la masa"},
                    {"name": "Formado", "description": "Dar forma a la pizza"},
                    {"name": "Horneado", "description": "Hornear a temperatura alta"},
                ],
                temperature_requirements={"fermentación": 25.0, "horneado": 250.0},
                time_requirements={"fermentación": 120.0, "horneado": 10.0},  # minutos
                equipment_needed=["mixer", "kneader", "proofer", "baker"],
            )
        }

    def optimize_production(self, formulation: Dict[str, float], scale: str) -> Dict[str, any]:
        """
        Optimizar el proceso de producción para una formulación específica.

        Args:
            formulation: Diccionario con los ingredientes y sus cantidades
            scale: Escala de producción ('small', 'medium', 'large')

        Returns:
            Dict con la configuración optimizada de producción
        """
        equipment = self._load_equipment()
        process = self._load_process_templates()

        # Calcular capacidad necesaria basada en la escala
        total_volume = sum(formulation.values())
        scale_factors = {"small": 1, "medium": 2, "large": 5}
        required_capacity = total_volume * scale_factors[scale]

        # Seleccionar equipamiento óptimo
        optimal_equipment = {}
        for eq_name, eq in equipment.items():
            if eq.capacity >= required_capacity:
                optimal_equipment[eq_name] = eq

        # Optimizar secuencia de producción
        optimized_steps = []
        current_temp = 25.0  # temperatura ambiente

        for step in process["pizza"].steps:
            energy_cost = abs(current_temp - step["temperature"]) * 0.1
            time_cost = step["time"] * 1.0
            total_cost = energy_cost + time_cost

            optimized_steps.append(
                {
                    "step_name": step["name"],
                    "equipment": min(
                        optimal_equipment.keys(), key=lambda x: equipment[x].energy_consumption
                    ),
                    "temperature": step["temperature"],
                    "time": step["time"],
                    "energy_cost": energy_cost,
                    "total_cost": total_cost,
                }
            )
            current_temp = step["temperature"]

        return {
            "optimized_steps": optimized_steps,
            "total_capacity": required_capacity,
            "selected_equipment": list(optimal_equipment.keys()),
        }

    def calculate_production_costs(
        self, formulation: Dict[str, float], scale: str
    ) -> Dict[str, float]:
        """
        Calcular costos de producción para una formulación específica.

        Args:
            formulation: Diccionario con los ingredientes y sus cantidades
            scale: Escala de producción ('small', 'medium', 'large')

        Returns:
            Dict con el desglose de costos
        """
        # Obtener optimización de producción
        optimization = self.optimize_production(formulation, scale)

        # Costos de ingredientes (ejemplo)
        ingredient_costs = {
            "flour": 2.5,  # por kg
            "water": 0.1,  # por litro
            "yeast": 15.0,  # por kg
            "salt": 1.0,  # por kg
        }

        # Calcular costos de materiales
        material_cost = sum(
            formulation.get(ing, 0) * cost for ing, cost in ingredient_costs.items()
        )

        # Calcular costos de energía
        energy_cost = sum(step["energy_cost"] for step in optimization["optimized_steps"])

        # Costos de mano de obra (ejemplo: $15 por hora)
        labor_hours = self.estimate_production_time(formulation, scale)
        labor_cost = labor_hours * 15.0

        # Costos de mantenimiento
        maintenance_cost = len(optimization["selected_equipment"]) * 10.0

        return {
            "material_cost": material_cost,
            "energy_cost": energy_cost,
            "labor_cost": labor_cost,
            "maintenance_cost": maintenance_cost,
            "total_cost": material_cost + energy_cost + labor_cost + maintenance_cost,
        }

    def estimate_production_time(self, formulation: Dict[str, float], scale: str) -> float:
        """
        Estimar tiempo total de producción para una formulación específica.

        Args:
            formulation: Diccionario con los ingredientes y sus cantidades
            scale: Escala de producción ('small', 'medium', 'large')

        Returns:
            Tiempo estimado en horas
        """
        # Obtener optimización de producción
        optimization = self.optimize_production(formulation, scale)

        # Tiempo base de los pasos de producción
        base_time = sum(step["time"] for step in optimization["optimized_steps"])

        # Factores de escala para el tiempo
        scale_factors = {
            "small": 1.0,
            "medium": 1.5,  # 50% más de tiempo para escala media
            "large": 2.0,  # Doble de tiempo para escala grande
        }

        # Tiempo de setup y limpieza
        setup_time = 0.5  # 30 minutos
        cleanup_time = 0.5  # 30 minutos

        # Calcular tiempo total en horas
        total_time = base_time * scale_factors[scale] + setup_time + cleanup_time

        return total_time
