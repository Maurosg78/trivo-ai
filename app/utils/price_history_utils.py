"""
Utilidades para el historial de precios de ingredientes
"""

def prepare_price_history_data(price_history):
    """
    Prepara los datos del historial de precios para ser utilizados en gráficos
    
    Args:
        price_history: Lista de entradas de historial de precios
        
    Returns:
        dict: Diccionario con las fechas, precios y otra información relevante
    """
    if not price_history:
        return {
            "dates": [],
            "prices": [],
            "suppliers": [],
            "units": [],
            "sources": [],
            "min_price": 0,
            "max_price": 0,
            "avg_price": 0
        }
    
    # Extraer fechas y precios para el gráfico
    dates = [entry.get('date', '') for entry in price_history]
    prices = [float(entry.get('price', 0)) for entry in price_history]
    suppliers = [entry.get('supplier', 'No especificado') for entry in price_history]
    units = [entry.get('unit', '') for entry in price_history]
    sources = [entry.get('source', 'manual') for entry in price_history]
    
    # Calcular estadísticas
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    avg_price = sum(prices) / len(prices) if prices else 0
    
    return {
        "dates": dates,
        "prices": prices,
        "suppliers": suppliers,
        "units": units,
        "sources": sources,
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2),
        "avg_price": round(avg_price, 2)
    } 