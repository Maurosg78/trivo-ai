"""
Modelo para el manejo de datos de ingredientes
"""
import json
import os
from datetime import datetime

# Rutas a los archivos de datos (simulando una base de datos)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
INGREDIENTS_FILE = os.path.join(DATA_DIR, 'ingredients.json')
PRICE_HISTORY_FILE = os.path.join(DATA_DIR, 'price_history.json')
SUPPLIERS_FILE = os.path.join(DATA_DIR, 'suppliers.json')

# Asegurar que el directorio de datos existe
os.makedirs(DATA_DIR, exist_ok=True)

def _load_json_file(file_path, default=None):
    """Carga un archivo JSON o devuelve un valor por defecto si no existe"""
    if default is None:
        default = {}
    
    if not os.path.exists(file_path):
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default

def _save_json_file(file_path, data):
    """Guarda datos en un archivo JSON"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False

def get_ingredient_price_history(ingredient_name):
    """
    Obtiene el historial de precios de un ingrediente
    
    Args:
        ingredient_name: Nombre del ingrediente
        
    Returns:
        list: Lista de entradas de historial ordenadas por fecha (más reciente primero)
    """
    price_history_data = _load_json_file(PRICE_HISTORY_FILE, {"ingredients": {}})
    ingredient_history = price_history_data.get("ingredients", {}).get(ingredient_name, [])
    
    # Ordenar por fecha (más reciente primero)
    return sorted(ingredient_history, key=lambda x: x.get('date', ''), reverse=True)

def update_ingredient_price(ingredient, price, unit, supplier_id=None, notes="", source="manual"):
    """
    Actualiza el precio de un ingrediente y agrega una entrada al historial
    
    Args:
        ingredient: Nombre del ingrediente
        price: Nuevo precio
        unit: Unidad de medida
        supplier_id: ID del proveedor (opcional)
        notes: Notas adicionales
        source: Fuente de la actualización ('manual', 'api', 'import')
        
    Returns:
        bool: True si la actualización fue exitosa
    """
    # Cargar datos actuales
    price_history_data = _load_json_file(PRICE_HISTORY_FILE, {"ingredients": {}})
    
    # Asegurar que existe la estructura para el ingrediente
    if "ingredients" not in price_history_data:
        price_history_data["ingredients"] = {}
    
    if ingredient not in price_history_data["ingredients"]:
        price_history_data["ingredients"][ingredient] = []
    
    # Obtener nombre del proveedor si se proporciona ID
    supplier_name = "No especificado"
    if supplier_id:
        suppliers = get_suppliers()
        if supplier_id in suppliers:
            supplier_name = suppliers[supplier_id].get('name', 'No especificado')
    
    # Crear nueva entrada en el historial
    today = datetime.now().strftime('%Y-%m-%d')
    new_entry = {
        "date": today,
        "price": price,
        "unit": unit,
        "supplier": supplier_name,
        "supplier_id": supplier_id,
        "notes": notes,
        "source": source
    }
    
    # Agregar al inicio del historial
    price_history_data["ingredients"][ingredient].insert(0, new_entry)
    
    # Guardar cambios
    return _save_json_file(PRICE_HISTORY_FILE, price_history_data)

def get_suppliers():
    """
    Obtiene la lista de proveedores
    
    Returns:
        dict: Diccionario de proveedores {id: datos_proveedor}
    """
    return _load_json_file(SUPPLIERS_FILE, {})

def get_ingredients():
    """
    Obtiene la lista de ingredientes
    
    Returns:
        dict: Diccionario de ingredientes {nombre: datos_ingrediente}
    """
    return _load_json_file(INGREDIENTS_FILE, {}) 