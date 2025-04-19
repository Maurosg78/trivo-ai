"""
Gestor de precios y costos para el PLM de masas
Funcionalidades:
- Cálculo de costos por ingrediente
- Cálculo de costos por receta
- Escalabilidad de recetas con ajuste de costos
- Análisis de rentabilidad
"""
import json
import os
import logging
import requests
from datetime import datetime
import pandas as pd
from config import DATA_DIR
from typing import Dict, List, Optional, Tuple, Any, Union

logger = logging.getLogger(__name__)

class PriceManager:
    """
    Gestor de precios de ingredientes para el sistema PizzaAI.
    Soporta consultas a APIs externas y actualizaciones manuales.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Inicializa el gestor de precios.
        
        Args:
            data_dir: Directorio donde se almacenan los datos de precios
        """
        self.data_dir = data_dir
        self.ingredients_db_path = os.path.join(data_dir, "ingredients_prices.json")
        self.price_history_path = os.path.join(data_dir, "price_history.json")
        self.suppliers_file = os.path.join(data_dir, "suppliers.json")
        self.logger = logging.getLogger("price_manager")
        
        # Asegurar que el directorio de datos existe
        os.makedirs(data_dir, exist_ok=True)
        
        # Inicializar bases de datos si no existen
        if not os.path.exists(self.ingredients_db_path):
            self._initialize_ingredients_db()
        
        if not os.path.exists(self.price_history_path):
            self._initialize_price_history()
        
        # Cargar bases de datos
        self.ingredients_db = self._load_ingredients_db()
        self.price_history = self._load_price_history()
        self.suppliers = self._load_suppliers()
        
        # API endpoints configurables
        self.api_endpoints = {
            "commodity_prices": "https://api.example.com/commodity_prices",
            "agricultural_prices": "https://api.example.com/agricultural_prices"
        }
        
        # Configurar claves API desde variables de entorno
        self.api_keys = {
            "commodity_prices": os.environ.get("COMMODITY_API_KEY", ""),
            "agricultural_prices": os.environ.get("AGRICULTURAL_API_KEY", "")
        }
    
    def _initialize_ingredients_db(self) -> None:
        """Crea la base de datos de ingredientes con algunos valores iniciales"""
        initial_db = {
            "harinas": {
                "harina_trigo_000": {"price": 0.8, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "harina_trigo_integral": {"price": 1.2, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "harina_centeno": {"price": 1.5, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "harina_maiz": {"price": 1.3, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "harina_arroz": {"price": 2.0, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "almidon_tapioca": {"price": 3.5, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "harina_sorgo": {"price": 2.8, "unit": "kg", "updated_at": datetime.now().isoformat()},
            },
            "liquidos": {
                "agua": {"price": 0.001, "unit": "l", "updated_at": datetime.now().isoformat()},
                "leche": {"price": 1.2, "unit": "l", "updated_at": datetime.now().isoformat()},
                "aceite_oliva": {"price": 8.0, "unit": "l", "updated_at": datetime.now().isoformat()},
                "aceite_girasol": {"price": 3.0, "unit": "l", "updated_at": datetime.now().isoformat()},
            },
            "fermentos": {
                "levadura_fresca": {"price": 4.0, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "levadura_seca": {"price": 12.0, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "masa_madre": {"price": 2.0, "unit": "kg", "updated_at": datetime.now().isoformat()},
            },
            "aditivos": {
                "sal": {"price": 0.8, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "azucar": {"price": 1.0, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "mantequilla": {"price": 10.0, "unit": "kg", "updated_at": datetime.now().isoformat()},
                "huevo": {"price": 0.2, "unit": "unit", "updated_at": datetime.now().isoformat()},
                "goma_xantana": {"price": 45.0, "unit": "kg", "updated_at": datetime.now().isoformat()},
            }
        }
        
        with open(self.ingredients_db_path, 'w') as f:
            json.dump(initial_db, f, indent=2)
    
    def _initialize_price_history(self) -> None:
        """Crea la base de datos de historial de precios"""
        initial_history = {
            "last_updated": datetime.now().isoformat(),
            "history": {}
        }
        
        with open(self.price_history_path, 'w') as f:
            json.dump(initial_history, f, indent=2)
    
    def _load_ingredients_db(self) -> Dict:
        """Carga la base de datos de ingredientes"""
        try:
            with open(self.ingredients_db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error al cargar la base de datos de ingredientes: {e}")
            return {}
    
    def _load_price_history(self) -> Dict:
        """Carga el historial de precios"""
        try:
            with open(self.price_history_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error al cargar el historial de precios: {e}")
            return {"last_updated": datetime.now().isoformat(), "history": {}}
    
    def _save_ingredients_db(self) -> None:
        """Guarda la base de datos de ingredientes"""
        try:
            with open(self.ingredients_db_path, 'w') as f:
                json.dump(self.ingredients_db, f, indent=2)
        except Exception as e:
            logger.error(f"Error al guardar la base de datos de ingredientes: {e}")
    
    def _save_price_history(self) -> None:
        """Guarda el historial de precios"""
        try:
            with open(self.price_history_path, 'w') as f:
                json.dump(self.price_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error al guardar el historial de precios: {e}")
    
    def get_ingredient_price(self, ingredient_name: str) -> Optional[Dict]:
        """
        Obtiene el precio actual de un ingrediente
        
        Args:
            ingredient_name: Nombre del ingrediente
            
        Returns:
            Diccionario con el precio y unidad, o None si no se encuentra
        """
        # Buscar en todas las categorías
        for category, ingredients in self.ingredients_db.items():
            if ingredient_name in ingredients:
                return ingredients[ingredient_name]
        
        # Buscar coincidencias parciales si no se encuentra exacto
        for category, ingredients in self.ingredients_db.items():
            for ing_name, ing_data in ingredients.items():
                if ingredient_name.lower() in ing_name.lower():
                    return ing_data
        
        return None
    
    def add_ingredient(self, category: str, name: str, price: float, unit: str) -> bool:
        """
        Añade un nuevo ingrediente a la base de datos
        
        Args:
            category: Categoría del ingrediente
            name: Nombre del ingrediente
            price: Precio del ingrediente
            unit: Unidad de medida
            
        Returns:
            True si se añadió correctamente, False en caso contrario
        """
        try:
            # Crear la categoría si no existe
            if category not in self.ingredients_db:
                self.ingredients_db[category] = {}
            
            # Añadir el ingrediente
            self.ingredients_db[category][name] = {
                "price": float(price),
                "unit": unit,
                "updated_at": datetime.now().isoformat()
            }
            
            # Guardar en la base de datos
            self._save_ingredients_db()
            return True
        except Exception as e:
            logger.error(f"Error al añadir ingrediente: {e}")
            return False
    
    def update_ingredient_price(self, name: str, new_price: float) -> bool:
        """
        Actualiza el precio de un ingrediente
        
        Args:
            name: Nombre del ingrediente
            new_price: Nuevo precio
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Buscar el ingrediente en todas las categorías
            for category, ingredients in self.ingredients_db.items():
                if name in ingredients:
                    # Guardar el precio anterior en el historial
                    old_price = ingredients[name]["price"]
                    timestamp = datetime.now().isoformat()
                    
                    if name not in self.price_history["history"]:
                        self.price_history["history"][name] = []
                    
                    self.price_history["history"][name].append({
                        "old_price": old_price,
                        "new_price": new_price,
                        "date": timestamp
                    })
                    
                    # Actualizar el precio
                    ingredients[name]["price"] = float(new_price)
                    ingredients[name]["updated_at"] = timestamp
                    
                    # Actualizar la fecha del historial
                    self.price_history["last_updated"] = timestamp
                    
                    # Guardar los cambios
                    self._save_ingredients_db()
                    self._save_price_history()
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error al actualizar precio: {e}")
            return False
    
    def get_price_history(self, ingredient_name: str) -> List[Dict]:
        """
        Obtiene el historial de precios de un ingrediente
        
        Args:
            ingredient_name: Nombre del ingrediente
            
        Returns:
            Lista con el historial de precios
        """
        if ingredient_name in self.price_history["history"]:
            return self.price_history["history"][ingredient_name]
        return []
    
    def calculate_recipe_cost(self, ingredients: List[Dict[str, Union[str, float]]]) -> Dict:
        """
        Calcula el costo total de una receta
        
        Args:
            ingredients: Lista de ingredientes con sus cantidades
                [
                    {"name": "harina_trigo_000", "amount": 1000, "unit": "g"},
                    {"name": "agua", "amount": 650, "unit": "ml"},
                    ...
                ]
                
        Returns:
            Diccionario con el desglose de costos y totales
        """
        total_cost = 0.0
        ingredients_cost = []
        missing_prices = []
        
        for ingredient in ingredients:
            name = ingredient["name"]
            amount = float(ingredient["amount"])
            unit = ingredient["unit"]
            
            # Obtener precio del ingrediente
            price_data = self.get_ingredient_price(name)
            
            if price_data:
                # Convertir unidades si es necesario
                base_amount, base_unit = self._convert_units(amount, unit, price_data["unit"])
                
                # Calcular costo
                ingredient_cost = base_amount * price_data["price"]
                total_cost += ingredient_cost
                
                # Registrar desglose
                ingredients_cost.append({
                    "ingredient": name,
                    "quantity": amount,
                    "unit": unit,
                    "unit_price": price_data["price"],
                    "price_unit": price_data["unit"],
                    "cost": round(ingredient_cost, 2)
                })
            else:
                missing_prices.append(name)
                ingredients_cost.append({
                    "ingredient": name,
                    "quantity": amount,
                    "unit": unit,
                    "unit_price": None,
                    "price_unit": None,
                    "cost": 0
                })
        
        # Calcular total de masa (usado para costo por kg)
        total_weight_g = self._calculate_total_weight(ingredients)
        cost_per_kg = 0
        
        if total_weight_g > 0:
            cost_per_kg = (total_cost / total_weight_g) * 1000
        
        return {
            "ingredient_costs": ingredients_cost,
            "total_cost": round(total_cost, 2),
            "missing_prices": missing_prices,
            "total_weight_g": total_weight_g,
            "cost_per_kg": round(cost_per_kg, 2)
        }
    
    def calculate_scaled_recipe(self, ingredients: List[Dict], scale_factor: float) -> Tuple[List[Dict], Dict]:
        """
        Escala una receta por un factor dado y calcula los nuevos costos
        
        Args:
            ingredients: Lista de ingredientes con sus cantidades
            scale_factor: Factor de escala (2.0 = duplicar, 0.5 = reducir a la mitad)
            
        Returns:
            Tupla con la lista de ingredientes escalados y el desglose de costos
        """
        scaled_ingredients = []
        
        for ingredient in ingredients:
            scaled_ingredient = ingredient.copy()
            scaled_ingredient["amount"] = float(ingredient["amount"]) * scale_factor
            scaled_ingredients.append(scaled_ingredient)
        
        # Calcular costos de la receta escalada
        cost_data = self.calculate_recipe_cost(scaled_ingredients)
        
        return scaled_ingredients, cost_data
    
    def calculate_production_costs(self, recipe_cost: Dict, batch_size: int = 1, 
                                  labor_cost: float = 0, overhead: float = 0) -> Dict:
        """
        Calcula los costos de producción para diferentes escalas
        
        Args:
            recipe_cost: Datos de costo de la receta base
            batch_size: Tamaño del lote (número de unidades)
            labor_cost: Costo de mano de obra por hora
            overhead: Gastos generales por lote
            
        Returns:
            Diccionario con análisis de costos para diferentes escalas
        """
        # Costo base por kg
        base_cost_per_kg = recipe_cost["cost_per_kg"]
        
        # Economía de escala: a mayor volumen, menor costo unitario
        small_batch = {
            "batch_size": "10 kg",
            "unit_cost": round(base_cost_per_kg * 0.95, 2),  # 5% de descuento
            "labor_cost": labor_cost * 2,  # Duplicamos porque pequeños lotes son menos eficientes
            "overhead": overhead,
            "setup_time": "1 hora"
        }
        
        medium_batch = {
            "batch_size": "100 kg",
            "unit_cost": round(base_cost_per_kg * 0.85, 2),  # 15% de descuento
            "labor_cost": labor_cost * 5,  # 5 horas de trabajo para lote mediano
            "overhead": overhead * 3,  # Más gastos generales
            "setup_time": "3 horas"
        }
        
        industrial = {
            "batch_size": "1000 kg",
            "unit_cost": round(base_cost_per_kg * 0.70, 2),  # 30% de descuento
            "labor_cost": labor_cost * 10,  # 10 horas de trabajo para producción industrial
            "overhead": overhead * 8,  # Gastos generales significativamente mayores
            "setup_time": "8 horas"
        }
        
        return {
            "base_cost_per_kg": base_cost_per_kg,
            "small_batch": small_batch,
            "medium_batch": medium_batch,
            "industrial": industrial
        }
    
    def calculate_margin_analysis(self, recipe_cost: Dict, sale_price_per_kg: float) -> Dict:
        """
        Realiza un análisis de márgenes de beneficio
        
        Args:
            recipe_cost: Datos de costo de la receta
            sale_price_per_kg: Precio de venta por kg
            
        Returns:
            Diccionario con análisis de márgenes y rentabilidad
        """
        cost_per_kg = recipe_cost["cost_per_kg"]
        
        # Cálculo de márgenes
        gross_profit = sale_price_per_kg - cost_per_kg
        margin_percentage = (gross_profit / sale_price_per_kg) * 100 if sale_price_per_kg > 0 else 0
        
        # Análisis de rentabilidad para diferentes escalas
        production_costs = self.calculate_production_costs(recipe_cost)
        
        small_batch_margin = ((sale_price_per_kg - production_costs["small_batch"]["unit_cost"]) / 
                             sale_price_per_kg) * 100 if sale_price_per_kg > 0 else 0
                             
        medium_batch_margin = ((sale_price_per_kg - production_costs["medium_batch"]["unit_cost"]) / 
                              sale_price_per_kg) * 100 if sale_price_per_kg > 0 else 0
                              
        industrial_margin = ((sale_price_per_kg - production_costs["industrial"]["unit_cost"]) / 
                            sale_price_per_kg) * 100 if sale_price_per_kg > 0 else 0
        
        # Punto de equilibrio (cantidades necesarias para cubrir costos)
        fixed_costs = 1000  # Ejemplo de costos fijos mensuales
        break_even_kg = fixed_costs / gross_profit if gross_profit > 0 else float('inf')
        
        return {
            "sale_price_per_kg": sale_price_per_kg,
            "cost_per_kg": cost_per_kg,
            "gross_profit_per_kg": round(gross_profit, 2),
            "margin_percentage": round(margin_percentage, 2),
            "margins_by_scale": {
                "small_batch": round(small_batch_margin, 2),
                "medium_batch": round(medium_batch_margin, 2),
                "industrial": round(industrial_margin, 2)
            },
            "break_even": {
                "fixed_costs": fixed_costs,
                "break_even_kg": round(break_even_kg, 2),
                "break_even_revenue": round(break_even_kg * sale_price_per_kg, 2)
            }
        }
    
    def _convert_units(self, amount: float, unit: str, base_unit: str) -> Tuple[float, str]:
        """
        Convierte entre diferentes unidades de medida
        
        Args:
            amount: Cantidad
            unit: Unidad original
            base_unit: Unidad base
            
        Returns:
            Tupla con la cantidad convertida y la unidad base
        """
        # Conversión de unidades de peso
        weight_conversions = {
            "kg": 1,
            "g": 0.001,
            "mg": 0.000001
        }
        
        # Conversión de unidades de volumen
        volume_conversions = {
            "l": 1,
            "ml": 0.001
        }
        
        # Si ya están en la misma unidad
        if unit == base_unit:
            return amount, base_unit
        
        # Conversiones de peso
        if unit in weight_conversions and base_unit in weight_conversions:
            return amount * (weight_conversions[unit] / weight_conversions[base_unit]), base_unit
        
        # Conversiones de volumen
        if unit in volume_conversions and base_unit in volume_conversions:
            return amount * (volume_conversions[unit] / volume_conversions[base_unit]), base_unit
        
        # Algunas conversiones especiales
        if unit == "g" and base_unit == "unit":  # Por ejemplo, huevos
            return amount / 50, base_unit  # Asumimos que un huevo pesa aproximadamente 50g
        
        # Si no se puede convertir, devolver como está
        logger.warning(f"No se puede convertir de {unit} a {base_unit}")
        return amount, unit
    
    def _calculate_total_weight(self, ingredients: List[Dict]) -> float:
        """
        Calcula el peso total de una receta en gramos
        
        Args:
            ingredients: Lista de ingredientes
            
        Returns:
            Peso total en gramos
        """
        total_weight_g = 0
        
        for ingredient in ingredients:
            amount = float(ingredient["amount"])
            unit = ingredient["unit"]
            
            # Convertir todo a gramos para el cálculo
            if unit == "g":
                total_weight_g += amount
            elif unit == "kg":
                total_weight_g += amount * 1000
            elif unit == "ml" or unit == "l":
                # Asumimos densidad 1g/ml para líquidos como agua
                if unit == "l":
                    amount *= 1000
                total_weight_g += amount
            # Otros casos especiales
            elif unit == "unit" and ingredient["name"] == "huevo":
                total_weight_g += amount * 50  # Aproximadamente 50g por huevo
        
        return total_weight_g
    
    def _load_suppliers(self) -> Dict[str, Dict[str, Any]]:
        """Carga la información de proveedores desde el archivo JSON"""
        if not os.path.exists(self.suppliers_file):
            return {}
            
        try:
            with open(self.suppliers_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Error loading suppliers: {e}")
            return {}
    
    def _save_suppliers(self) -> bool:
        """Guarda la información de proveedores en el archivo JSON"""
        try:
            with open(self.suppliers_file, 'w', encoding='utf-8') as f:
                json.dump(self.suppliers, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error saving suppliers: {e}")
            return False

# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar gestor de precios
    price_manager = PriceManager()
    
    # Ejemplo de una receta de pan básica
    ingredients = [
        {"name": "harina_trigo_000", "amount": 1000, "unit": "g"},
        {"name": "agua", "amount": 650, "unit": "ml"},
        {"name": "sal", "amount": 20, "unit": "g"},
        {"name": "levadura_fresca", "amount": 20, "unit": "g"}
    ]
    
    # Calcular costos
    recipe_cost = price_manager.calculate_recipe_cost(ingredients)
    print(f"Costo total: ${recipe_cost['total_cost']}")
    print(f"Costo por kg: ${recipe_cost['cost_per_kg']}")
    
    # Escalar receta
    scaled_recipe, scaled_cost = price_manager.calculate_scaled_recipe(ingredients, 2.0)
    print(f"Costo de receta escalada (x2): ${scaled_cost['total_cost']}")
    
    # Análisis de producción
    production_analysis = price_manager.calculate_production_costs(recipe_cost)
    print(f"Costo por kg en producción industrial: ${production_analysis['industrial']['unit_cost']}")
    
    # Análisis de margen
    margin_analysis = price_manager.calculate_margin_analysis(recipe_cost, 5.0)
    print(f"Margen bruto: {margin_analysis['margin_percentage']}%")
    print(f"Punto de equilibrio: {margin_analysis['break_even']['break_even_kg']} kg") 