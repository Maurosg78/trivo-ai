"""
Rutas relacionadas con ingredientes y sus precios
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.utils.price_history_utils import prepare_price_history_data
from app.models.ingredients import get_ingredient_price_history, update_ingredient_price, get_suppliers
from datetime import datetime

# Crear el blueprint
ingredient_bp = Blueprint('ingredient', __name__)

@ingredient_bp.route('/ingredient/price-history/<ingredient>')
def ingredient_price_history(ingredient):
    """
    Muestra el historial de precios de un ingrediente
    
    Args:
        ingredient: Nombre del ingrediente
    """
    # Obtener historial de precios (implementación depende de tus modelos)
    price_history = get_ingredient_price_history(ingredient)
    
    # Obtener datos del proveedor actual (si existe)
    suppliers = get_suppliers()
    
    # Preparar datos para la vista
    data = prepare_price_history_data(price_history)
    
    # Datos actuales (último registro)
    current_price = data["prices"][0] if data["prices"] else 0
    current_unit = data["units"][0] if data["units"] else "kg"
    current_supplier = data["suppliers"][0] if data["suppliers"] else "No especificado"
    last_updated = data["dates"][0] if data["dates"] else "N/A"
    
    # Buscar el ID del proveedor actual
    current_supplier_id = None
    for supplier_id, supplier in suppliers.items():
        if supplier.get('name') == current_supplier:
            current_supplier_id = supplier_id
            break
    
    # Renderizar plantilla con todos los datos necesarios
    return render_template(
        'ingredient_price_history.html',
        ingredient=ingredient,
        price_history=price_history,
        price_history_dates=data["dates"],
        price_history_prices=data["prices"],
        current_price=current_price,
        current_unit=current_unit,
        current_supplier=current_supplier,
        current_supplier_id=current_supplier_id,
        last_updated=last_updated,
        min_price=data["min_price"],
        max_price=data["max_price"],
        avg_price=data["avg_price"],
        suppliers=suppliers
    )

@ingredient_bp.route('/ingredient/update-price', methods=['POST'])
def update_ingredient_price_route():
    """
    Actualiza el precio de un ingrediente
    """
    if request.method == 'POST':
        ingredient = request.form.get('ingredient')
        price = request.form.get('price')
        unit = request.form.get('unit')
        supplier_id = request.form.get('supplier_id')
        notes = request.form.get('notes', '')
        
        # Validar datos
        if not ingredient or not price or not unit:
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            return redirect(request.referrer or url_for('ingredient.ingredient_price_history', ingredient=ingredient))
        
        try:
            # Actualizar precio
            update_ingredient_price(
                ingredient=ingredient,
                price=float(price),
                unit=unit,
                supplier_id=supplier_id,
                notes=notes,
                source='manual'
            )
            flash(f'Precio de {ingredient} actualizado correctamente.', 'success')
        except Exception as e:
            flash(f'Error al actualizar el precio: {str(e)}', 'error')
        
        return redirect(url_for('ingredient.ingredient_price_history', ingredient=ingredient))

@ingredient_bp.route('/ingredient/update-price-from-api/<ingredient>')
def update_price_from_api(ingredient):
    """
    Actualiza el precio de un ingrediente desde una API externa
    """
    try:
        # Aquí se implementaría la lógica para consultar una API externa
        # Por ahora, simulamos una actualización exitosa
        price = 0  # Precio obtenido de la API
        unit = "kg"  # Unidad por defecto
        
        # Actualizar precio
        update_ingredient_price(
            ingredient=ingredient,
            price=price,
            unit=unit,
            supplier_id=None,
            notes='Actualización automática desde API',
            source='api'
        )
        
        flash(f'Precio de {ingredient} actualizado desde API.', 'success')
    except Exception as e:
        flash(f'Error al actualizar el precio desde API: {str(e)}', 'error')
    
    return redirect(url_for('ingredient.ingredient_price_history', ingredient=ingredient))

# Registrar el blueprint en app.py
# from app.routes.ingredient_routes import ingredient_bp
# app.register_blueprint(ingredient_bp) 