import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class Order:
    """Clase que representa un pedido."""

    id: int
    location: Dict[str, float]
    items: List[Dict]
    created_at: datetime


@dataclass
class DeliveryRoute:
    """Clase que representa una ruta de entrega."""

    zone: str
    orders: List[Order]
    estimated_time: float


class StorageRequirements(BaseModel):
    temperature: float
    humidity: float
    shelf_life_days: int
    packaging_type: str


class DistributionChannel(BaseModel):
    name: str
    cost_per_unit: float
    delivery_time_days: int
    minimum_order: int
    maximum_distance_km: float


class LogisticsManager:
    """Gestiona la logística de entregas."""

    def __init__(self):
        self.zones = {}
        self.storage_requirements = self._load_storage_requirements()
        self.distribution_channels = self._load_distribution_channels()

    def _load_storage_requirements(self) -> Dict[str, StorageRequirements]:
        """
        Cargar requisitos de almacenamiento para diferentes tipos de productos
        """
        return {
            "frozen": StorageRequirements(
                temperature=-18.0, humidity=0.0, shelf_life_days=90, packaging_type="vacuum_sealed"
            ),
            "refrigerated": StorageRequirements(
                temperature=4.0,
                humidity=0.7,
                shelf_life_days=7,
                packaging_type="modified_atmosphere",
            ),
            "room_temperature": StorageRequirements(
                temperature=20.0, humidity=0.5, shelf_life_days=3, packaging_type="standard"
            ),
        }

    def _load_distribution_channels(self) -> Dict[str, DistributionChannel]:
        """
        Cargar canales de distribución disponibles
        """
        return {
            "local_delivery": DistributionChannel(
                name="Entrega Local",
                cost_per_unit=2.0,
                delivery_time_days=1,
                minimum_order=10,
                maximum_distance_km=50.0,
            ),
            "regional_shipping": DistributionChannel(
                name="Envío Regional",
                cost_per_unit=5.0,
                delivery_time_days=3,
                minimum_order=50,
                maximum_distance_km=500.0,
            ),
            "national_shipping": DistributionChannel(
                name="Envío Nacional",
                cost_per_unit=10.0,
                delivery_time_days=5,
                minimum_order=100,
                maximum_distance_km=2000.0,
            ),
        }

    def optimize_distribution(self, product: Dict[str, any], target_market: str) -> Dict[str, any]:
        """
        Optimizar la distribución del producto basado en el mercado objetivo.
        
        Args:
            product: Diccionario con información del producto
            target_market: Mercado objetivo para la distribución
            
        Returns:
            Dict con la estrategia de distribución optimizada
        """
        channels = self._load_distribution_channels()
        requirements = self._load_storage_requirements()
        
        # Filtrar canales disponibles para el mercado objetivo
        available_channels = {
            name: channel for name, channel in channels.items()
            if channel.maximum_distance_km >= self._calculate_market_distance(target_market)
        }
        
        # Seleccionar el canal más eficiente
        optimal_channel = min(
            available_channels.values(),
            key=lambda c: c.cost_per_unit * product.get("weight", 1)
        )
        
        return {
            "channel": optimal_channel.name,
            "estimated_cost": optimal_channel.cost_per_unit * product.get("weight", 1),
            "delivery_time": optimal_channel.delivery_time_days,
            "storage_requirements": requirements.get(product.get("type", "default"), {})
        }

    def calculate_shipping_costs(
        self, product: Dict[str, any], quantity: int, destination: str
    ) -> float:
        """
        Calcular costos de envío basado en el producto, cantidad y destino.
        
        Args:
            product: Diccionario con información del producto
            quantity: Cantidad de productos a enviar
            destination: Destino del envío
            
        Returns:
            float con el costo total de envío
        """
        base_cost = 10.0  # Costo base por envío
        weight_cost = product.get("weight", 1) * 2.0  # $2 por kg
        distance_cost = self._calculate_market_distance(destination) * 0.1  # $0.1 por km
        
        # Aplicar descuentos por cantidad
        quantity_discount = 0
        if quantity > 100:
            quantity_discount = 0.2  # 20% de descuento
        elif quantity > 50:
            quantity_discount = 0.1  # 10% de descuento
            
        total_cost = (base_cost + weight_cost + distance_cost) * quantity
        return total_cost * (1 - quantity_discount)

    def estimate_delivery_time(self, product: Dict[str, any], destination: str) -> timedelta:
        """
        Estimar tiempo de entrega basado en el producto y destino.
        
        Args:
            product: Diccionario con información del producto
            destination: Destino del envío
            
        Returns:
            timedelta con el tiempo estimado de entrega
        """
        base_days = 2  # Días base para procesamiento
        distance_days = self._calculate_market_distance(destination) / 500  # 500km por día
        product_days = 0
        
        # Tiempo adicional según tipo de producto
        if product.get("type") == "perishable":
            product_days = 0.5
        elif product.get("type") == "fragile":
            product_days = 1
            
        total_days = base_days + distance_days + product_days
        return timedelta(days=total_days)

    def optimize_delivery_routes(self, orders: List[Order]) -> List[DeliveryRoute]:
        """Optimiza las rutas de entrega para un conjunto de pedidos."""
        if not orders:
            return []

        # Agrupar pedidos por zona
        zones = self._group_orders_by_zone(orders)

        # Optimizar rutas por zona
        optimized_routes = []
        for zone, zone_orders in zones.items():
            route = self._optimize_zone_route(zone, zone_orders)
            if route:
                optimized_routes.append(route)

        return optimized_routes

    def _group_orders_by_zone(self, orders: List[Order]) -> Dict[str, List[Order]]:
        """Agrupa pedidos por zona geográfica."""
        zones = {}
        for order in orders:
            zone = self._get_order_zone(order)
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(order)
        return zones

    def _optimize_zone_route(self, zone: str, orders: List[Order]) -> Optional[DeliveryRoute]:
        """Optimiza la ruta para una zona específica."""
        if not orders:
            return None

        # Calcular centroide de la zona
        centroid = self._calculate_zone_centroid(orders)

        # Ordenar pedidos por distancia al centroide
        sorted_orders = sorted(orders, key=lambda o: self._calculate_distance(o.location, centroid))

        # Crear ruta optimizada
        return DeliveryRoute(
            zone=zone,
            orders=sorted_orders,
            estimated_time=self._calculate_route_time(sorted_orders),
        )

    def _get_order_zone(self, order: Order) -> str:
        """Determina la zona de un pedido."""
        # Implementación básica - dividir por cuadrantes
        lat, lon = order.location["lat"], order.location["lon"]
        if lat >= 0 and lon >= 0:
            return "NE"
        elif lat >= 0 and lon < 0:
            return "NW"
        elif lat < 0 and lon >= 0:
            return "SE"
        else:
            return "SW"

    def _calculate_zone_centroid(self, orders: List[Order]) -> Dict[str, float]:
        """Calcula el centroide de una zona."""
        if not orders:
            return {"lat": 0, "lon": 0}

        total_lat = sum(order.location["lat"] for order in orders)
        total_lon = sum(order.location["lon"] for order in orders)
        count = len(orders)

        return {"lat": total_lat / count, "lon": total_lon / count}

    def _calculate_distance(self, point1: Dict[str, float], point2: Dict[str, float]) -> float:
        """Calcula la distancia entre dos puntos."""
        # Implementación básica - distancia euclidiana
        lat_diff = point1["lat"] - point2["lat"]
        lon_diff = point1["lon"] - point2["lon"]
        return (lat_diff**2 + lon_diff**2) ** 0.5

    def _calculate_route_time(self, orders: List[Order]) -> float:
        """Calcula el tiempo estimado para una ruta."""
        # Implementación básica - 5 minutos por pedido
        return len(orders) * 5
