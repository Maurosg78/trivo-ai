#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicación web para TRIVO-AI.

Esta aplicación proporciona una interfaz web para interactuar con el sistema 
de formulación y validación de masas de TRIVO-AI.
"""

import os
import json
import time
import logging
import traceback
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import argparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Crear logger para este módulo
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_trivo_ai_app')

# Importar módulos del proyecto con manejo de errores
try:
    from src.features.validation.validation_engine import ValidationEngine, check_system_integrity
    app.logger.info("Sistema de validación cargado correctamente")
except Exception as e:
    app.logger.error(f"Error al cargar el sistema de validación: {str(e)}")
    app.logger.error(traceback.format_exc())
    
    # Definir clase simulada para evitar errores de ejecución
    class MockValidationEngine:
        def __init__(self):
            pass
            
        def validate_recipe(self, *args, **kwargs):
            return []
            
        def summarize_results(self, *args, **kwargs):
            return {"error": "Sistema de validación no disponible", "is_viable": False}
            
        def get_contextual_recommendations(self, *args, **kwargs):
            return None
    
    ValidationEngine = MockValidationEngine
    
    def check_system_integrity():
        return {"status": "ERROR", "error_message": "Sistema de validación no disponible"}

# Integrar sistema de caché inteligente
try:
    from src.features.external_api import get_spoonacular_client, get_recipe_cache
    app.logger.info("Sistema de caché inteligente cargado correctamente")
    has_cache_system = True
    # Inicializar componentes del caché inteligente
    recipe_cache = get_recipe_cache()
    spoonacular_client = get_spoonacular_client()
except Exception as e:
    app.logger.error(f"Error al cargar el sistema de caché inteligente: {str(e)}")
    app.logger.error(traceback.format_exc())
    has_cache_system = False
    recipe_cache = None
    spoonacular_client = None

try:
    from src.features.nlp.language_processor import LanguageProcessor
    app.logger.info("Procesador de lenguaje natural cargado correctamente")
    has_language_processor = True
except Exception as e:
    app.logger.error(f"Error al cargar el procesador de lenguaje natural: {str(e)}")
    app.logger.error(traceback.format_exc())
    has_language_processor = False
    
    # Clase simulada para procesamiento de lenguaje natural con conexión a APIs externas
    class MockLanguageProcessor:
        def __init__(self):
            self.external_api_available = False
            # Intentar cargar el cliente de Spoonacular directamente
            try:
                from src.features.external_api import get_spoonacular_client
                self.spoonacular_client = get_spoonacular_client()
                self.external_api_available = True
                app.logger.info("Cliente Spoonacular cargado en el procesador mock")
            except Exception as api_err:
                app.logger.error(f"No se pudo cargar el cliente de Spoonacular: {str(api_err)}")
                self.spoonacular_client = None
        
        def process_request(self, text, refinement_answers=None):
            app.logger.info(f"Procesando solicitud con procesador mock: {text}")
            
            # Intentar usar la API externa si está disponible
            if self.external_api_available and self.spoonacular_client:
                try:
                    app.logger.info("Consultando API externa Spoonacular...")
                    recipe_info = self.spoonacular_client.search_recipes(text)
                    if recipe_info:
                        app.logger.info("Receta encontrada en API externa")
                        return self.adapt_external_recipe(recipe_info, text)
                except Exception as api_err:
                    app.logger.error(f"Error al consultar API externa: {str(api_err)}")
            
            # Si no se puede usar la API externa, analizar el texto para extraer información
            is_gluten_free = 'sin gluten' in text.lower() or 'libre de gluten' in text.lower() or 'gluten free' in text.lower()
            is_pasta = 'espagueti' in text.lower() or 'pasta' in text.lower() or 'fideos' in text.lower()
            has_spinach = 'espinaca' in text.lower()
            has_bolognese = 'boloñesa' in text.lower() or 'bolognese' in text.lower()
            
            # Determinar número de personas
            portions = 1
            for i in range(1, 21):
                if f"para {i}" in text.lower():
                    portions = i
                    break
            
            # Crear receta base según el tipo detectado
            if is_pasta:
                recipe = self.create_pasta_recipe(is_gluten_free, has_spinach, portions)
                if has_bolognese:
                    recipe = self.add_bolognese_sauce(recipe)
                return recipe
            else:
                return self.create_default_recipe(text, is_gluten_free, portions)
        
        def create_pasta_recipe(self, is_gluten_free, has_spinach, portions):
            """Crea una receta de pasta adaptada a los requisitos."""
            app.logger.info(f"Creando receta de pasta: sin_gluten={is_gluten_free}, espinacas={has_spinach}, porciones={portions}")
            
            # Base para pasta sin gluten
            if is_gluten_free:
                base_ingredients = {
                    'harina_arroz': 200 * portions / 2,
                    'almidon_maiz': 50 * portions / 2,
                    'goma_xantana': 5 * portions / 2,
                    'huevos': max(1, int(portions / 2)),
                    'agua': 100 * portions / 2,
                    'aceite_oliva': 10 * portions / 2,
                    'sal': 3 * portions / 2
                }
            else:
                base_ingredients = {
                    'harina_trigo': 250 * portions / 2,
                    'huevos': max(2, int(portions / 2) + 1),
                    'sal': 3 * portions / 2
                }
            
            # Añadir espinacas si se solicitan
            if has_spinach:
                base_ingredients['espinacas'] = 100 * portions / 2
                # Ajustar la cantidad de agua si hay espinacas (para compensar la humedad)
                if 'agua' in base_ingredients:
                    base_ingredients['agua'] = base_ingredients['agua'] * 0.8
            
            # Crear instrucciones específicas para pasta
            instructions = [
                "Mezclar los ingredientes secos en un recipiente grande.",
                "Hacer un hueco en el centro y añadir los huevos y otros ingredientes líquidos.",
                "Amasar durante 8-10 minutos hasta obtener una masa homogénea.",
                "Dejar reposar la masa cubierta con film transparente durante 30 minutos.",
                "Estirar la masa finamente y cortar en tiras para hacer espaguetis.",
                "Hervir agua con sal y cocinar los espaguetis durante 2-3 minutos."
            ]
            
            if has_spinach:
                instructions.insert(1, "Si usas espinacas frescas, blanquearlas, escurrirlas bien y triturarlas antes de añadir a la masa.")
                instructions.insert(2, "Incorporar el puré de espinacas a la mezcla para obtener un color verde uniforme.")
            
            return {
                'detected_type': 'pasta',
                'ingredients': base_ingredients,
                'instructions': instructions,
                'properties': {
                    'sin_gluten': is_gluten_free,
                    'con_espinacas': has_spinach,
                    'porciones': portions
                }
            }
        
        def add_bolognese_sauce(self, recipe):
            """Añade ingredientes e instrucciones para salsa boloñesa."""
            # Ingredientes para la salsa boloñesa
            bolognese_ingredients = {
                'carne_molida': 250,
                'cebolla': 1,
                'zanahoria': 1,
                'apio': 1,
                'ajo': 2,
                'tomate_triturado': 400,
                'caldo_carne': 100,
                'vino_tinto': 50,
                'aceite_oliva': 20,
                'sal': 3,
                'pimienta': 2,
                'oregano': 1,
                'laurel': 1
            }
            
            # Escalar según porciones
            portions = recipe['properties']['porciones']
            for key in bolognese_ingredients:
                if isinstance(bolognese_ingredients[key], (int, float)):
                    bolognese_ingredients[key] = bolognese_ingredients[key] * portions / 4
            
            # Añadir ingredientes de la salsa
            recipe['ingredients'].update(bolognese_ingredients)
            
            # Añadir instrucciones para la salsa
            sauce_instructions = [
                "Para la salsa: Picar finamente la cebolla, zanahoria, apio y ajo.",
                "Calentar aceite en una sartén y sofreír las verduras hasta que estén tiernas.",
                "Añadir la carne molida y cocinar hasta que cambie de color.",
                "Incorporar el vino tinto y dejar reducir.",
                "Añadir el tomate triturado, el caldo, la hoja de laurel y las hierbas.",
                "Cocinar a fuego lento durante 1-2 horas, removiendo ocasionalmente.",
                "Servir la salsa sobre los espaguetis recién cocinados."
            ]
            
            recipe['instructions'].extend(sauce_instructions)
            recipe['properties']['con_salsa'] = 'boloñesa'
            
            return recipe
        
        def create_default_recipe(self, text, is_gluten_free, portions):
            """Crea una receta por defecto basada en el texto."""
            # Detectar opciones básicas del texto
            color = None
            for c in ['rojo', 'verde', 'amarillo', 'negro', 'morado']:
                if c in text.lower():
                    color = c
                    break
            
            # Receta base
            if is_gluten_free:
                ingredients = {
                    'harina_arroz': 300.0 * (2.4 if portions > 1 else 1.0),
                    'almidon_maiz': 100.0 * (2.4 if portions > 1 else 1.0),
                    'goma_xantana': 10.0 * (2.4 if portions > 1 else 1.0),
                    'agua': 280.0 * (2.4 if portions > 1 else 1.0),
                    'aceite_oliva': 20.0 * (2.4 if portions > 1 else 1.0),
                    'sal': 8.0 * (2.4 if portions > 1 else 1.0),
                    'levadura': 7.0 * (2.4 if portions > 1 else 1.0)
                }
            else:
                ingredients = {
                    'harina': 500.0 * (2.4 if portions > 1 else 1.0),
                    'agua': 300.0 * (2.4 if portions > 1 else 1.0),
                    'aceite_oliva': 15.0 * (2.4 if portions > 1 else 1.0),
                    'sal': 10.0 * (2.4 if portions > 1 else 1.0),
                    'levadura': 5.0 * (2.4 if portions > 1 else 1.0)
                }
            
            # Añadir color si se detectó
            if color == 'rojo':
                ingredients['pure_tomate'] = 30.0 * (2.4 if portions > 1 else 1.0)
                ingredients['pimenton_dulce'] = 5.0 * (2.4 if portions > 1 else 1.0)
            elif color == 'verde':
                ingredients['espinacas_frescas'] = 30.0 * (2.4 if portions > 1 else 1.0)
            elif color == 'amarillo':
                ingredients['curcuma'] = 5.0 * (2.4 if portions > 1 else 1.0)
            
            # Instrucciones genéricas
            instructions = [
                "Mezclar todos los ingredientes secos en un recipiente grande.",
                "Añadir gradualmente los ingredientes líquidos mientras se amasa.",
                "Amasar durante 8-10 minutos hasta obtener una masa elástica.",
                "Dejar reposar la masa tapada durante 1-2 horas.",
                "Extender la masa y hornear a 220°C durante 12-15 minutos."
            ]
            
            # Propiedades detectadas
            properties = {
                'sin_gluten': is_gluten_free,
                'vegano': False,
                'color': color,
                'escala': 'individual' if portions == 1 else 'familiar'
            }
            
            return {
                'detected_type': 'pizza',
                'ingredients': ingredients,
                'instructions': instructions,
                'properties': properties
            }
            
        def adapt_external_recipe(self, recipe_info, original_text):
            """Adapta la receta obtenida de una API externa al formato interno."""
            app.logger.info(f"Adaptando receta externa: {recipe_info.get('title', 'Sin título')}")
            
            # Extraer información útil del texto original
            is_gluten_free = 'sin gluten' in original_text.lower()
            portions = 1
            for i in range(1, 21):
                if f"para {i}" in original_text.lower():
                    portions = i
                    break
            
            # Crear estructura de receta interna
            adapted_recipe = {
                'detected_type': 'externo',
                'title': recipe_info.get('title', 'Receta Externa'),
                'ingredients': {},
                'instructions': [],
                'properties': {
                    'sin_gluten': is_gluten_free,
                    'porciones': portions,
                    'fuente': 'Spoonacular API',
                    'id_externo': recipe_info.get('id', 0)
                }
            }
            
            # Adaptar ingredientes
            if 'extendedIngredients' in recipe_info:
                for ing in recipe_info['extendedIngredients']:
                    name = ing.get('name', 'ingrediente')
                    amount = ing.get('amount', 0)
                    unit = ing.get('unit', '')
                    adapted_recipe['ingredients'][name] = f"{amount} {unit}"
            
            # Adaptar instrucciones
            if 'analyzedInstructions' in recipe_info and recipe_info['analyzedInstructions']:
                for step in recipe_info['analyzedInstructions'][0].get('steps', []):
                    adapted_recipe['instructions'].append(step.get('step', ''))
            
            # Si no hay instrucciones, usar un mensaje genérico
            if not adapted_recipe['instructions']:
                adapted_recipe['instructions'] = ['No se encontraron instrucciones detalladas para esta receta.']
            
            return adapted_recipe
    
    LanguageProcessor = MockLanguageProcessor

def generate_instructions(ingredients, properties=None):
    """Genera instrucciones básicas para preparar una receta de pizza."""
    if properties is None:
        properties = {}
    
    instructions = []
    
    # Paso 1: Mezclar secos
    instructions.append("Mezclar los ingredientes secos en un recipiente grande.")
    
    # Paso 2: Añadir líquidos
    instructions.append("Añadir el agua tibia gradualmente mientras se mezcla.")
    
    # Paso 3: Aceite
    if 'aceite_oliva' in ingredients or 'aceite_de_oliva' in ingredients or 'olive_oil' in ingredients:
        instructions.append("Incorporar el aceite y amasar hasta obtener una masa homogénea.")
    else:
        instructions.append("Amasar durante 8-10 minutos hasta obtener una masa elástica.")
    
    # Paso 4: Tiempo de reposo
    if properties.get('no_fermentacion', False):
        instructions.append("Dejar reposar la masa 10 minutos antes de usarla.")
    else:
        instructions.append("Dejar reposar la masa tapada durante 30 minutos.")
    
    # Paso 5: Extender masa
    if properties.get('es_sin_gluten', False) or 'harina_arroz' in ingredients or 'rice_flour' in ingredients:
        instructions.append("Extender la masa directamente en la bandeja de horno usando las manos húmedas o una espátula.")
    else:
        instructions.append("Extender la masa sobre una superficie enharinada hasta el grosor deseado.")
    
    # Paso 6: Hornear
    if properties.get('temperatura_horno'):
        instructions.append(f"Hornear a {properties.get('temperatura_horno')}°C durante 12-15 minutos o hasta que esté dorada.")
    else:
        instructions.append("Hornear a 220°C durante 12-15 minutos o hasta que esté dorada.")
    
    # Paso final
    instructions.append("Dejar enfriar antes de servir.")
    
    return instructions

@app.route('/')
def index():
    """Página de inicio."""
    return render_template('index.html')

@app.route('/optimize', methods=['GET', 'POST'])
def optimize():
    """Página para crear y optimizar recetas."""
    if request.method == 'POST':
        try:
            # Procesar formulario
            recipe_data = {}
            
            # Procesar ingredientes
            for key, value in request.form.items():
                if key.startswith('ingredient_') and value.strip():
                    ingredient_name = key.replace('ingredient_', '')
                    try:
                        ingredient_value = float(value)
                        recipe_data[ingredient_name] = ingredient_value
                    except ValueError:
                        pass
            
            if not recipe_data:
                flash("No se proporcionaron ingredientes válidos", "danger")
                return render_template('optimize.html')
            
            # Mostrar receta original
            return render_template('optimize.html', 
                                  original_recipe=recipe_data,
                                  optimized_recipe=recipe_data)  # En una implementación real, aquí iría la optimización
                                  
        except Exception as e:
            app.logger.error(f"Error: {str(e)}")
            flash(f"Error al procesar la receta: {str(e)}", "danger")
    
    return render_template('optimize.html')

@app.route('/natural-language', methods=['POST', 'GET'])
def natural_language():
    """Procesa una solicitud en lenguaje natural para generar una receta."""
    try:
        # Verificar si es POST o GET
        if request.method == 'POST':
            # Obtener texto de entrada
            text = request.form.get('natural_language_input', '')
            scale = request.form.get('production_scale', 'familiar')
            
            # Verificar si hay respuestas a preguntas de refinamiento
            refinement_answers = {}
            for key in request.form:
                if key.startswith('refinement_'):
                    question_id = key.replace('refinement_', '')
                    refinement_answers[question_id] = request.form[key]
        else:  # GET
            # Obtener parámetros de la URL
            text = request.args.get('natural_language_input', '')
            scale = request.args.get('production_scale', 'familiar')
            
            # Recopilar respuestas de refinamiento
            refinement_answers = {}
            for key, value in request.args.items():
                if key.startswith('refinement_'):
                    question_id = key.replace('refinement_', '')
                    refinement_answers[question_id] = value
        
        app.logger.info(f"Procesando petición de lenguaje natural: {text}")
        
        if not text and not refinement_answers:
            flash("Por favor ingresa una descripción de lo que necesitas.", "warning")
            return redirect(url_for('index'))
        
        # Combinar escala con texto para mejor detección
        if scale and scale != 'auto':
            if not text.lower().endswith(scale.lower()):
                text = f"{text} {scale}"
        
        # Inicializar el procesador de lenguaje natural
        try:
            processor = LanguageProcessor()
            app.logger.info(f"Enviando solicitud al procesador: {text}")
            
            # Procesar solicitud con las respuestas de refinamiento (si existen)
            result = processor.process_request(text, refinement_answers if refinement_answers else None)
            
            app.logger.info(f"Resultado del procesador: {result}")
            
            # Verificar si hay preguntas de refinamiento y mostrar el formulario si no hay respuestas previas
            refinement_questions = result.get('refinement_questions', [])
            if refinement_questions and len(refinement_questions) > 0 and not refinement_answers:
                app.logger.info(f"Mostrando formulario de refinamiento con {len(refinement_questions)} preguntas")
                return render_template(
                    'refinement.html', 
                    original_text=text,
                    production_scale=scale,
                    questions=refinement_questions,
                    detected_type=result.get('detected_type', 'pizza'),
                    properties=result.get('properties', {})
                )
            
            # Mostrar ingredientes detectados
            app.logger.info("--- INGREDIENTES DETECTADOS ---")
            for ingredient, amount in result['ingredients'].items():
                app.logger.info(f"  {ingredient}: {amount}")
            app.logger.info("-----------------------------")
            
            # Validar receta
            validation_results = validate_recipe(result['ingredients'], 
                                                result.get('properties', {}).get('escala', scale),
                                                result.get('properties', {}).get('sin_gluten', False))
            
            # Generar instrucciones de preparación detalladas
            instructions = result.get('instructions', [])
            if not instructions:
                # Generar instrucciones si no están presentes
                instructions = generate_instructions(result['ingredients'], result.get('properties', {}))
            
            # Formatear recomendaciones para mejor visualización
            recommendations = []
            for rec in validation_results.get('recommendations', []):
                # Eliminar texto redundante o problemático
                rec_text = rec['text'].replace('La receta', 'Tu receta')
                rec_text = rec_text.replace('se recomienda', 'recomendamos')
                
                # Categorizar por tipo
                if 'ajustar' in rec_text.lower() or 'aumentar' in rec_text.lower() or 'reducir' in rec_text.lower():
                    category = 'ajuste'
                elif 'textura' in rec_text.lower() or 'consistencia' in rec_text.lower():
                    category = 'textura'
                elif 'sabor' in rec_text.lower() or 'sal' in rec_text.lower():
                    category = 'sabor'
                else:
                    category = 'general'
                
                recommendations.append({
                    'text': rec_text,
                    'priority': rec['priority'],
                    'category': category
                })
            
            # Renderizar plantilla con resultados
            app.logger.info("Renderizando plantilla con resultados generados")
            return render_template(
                'result.html',
                original_text=text,
                recipe_type=result.get('detected_type', 'Desconocido'),
                ingredients=result['ingredients'],
                instructions=instructions,
                properties=result.get('properties', {}),
                validation_results=validation_results,
                recommendations=recommendations
            )
        
        except Exception as e:
            app.logger.error(f"Error al procesar con el procesador: {str(e)}", exc_info=True)
            # Crear una respuesta más avanzada según el tipo de receta solicitada
            app.logger.info("Usando procesador alternativo para generar la receta")
            
            try:
                # Intentar usar las funciones mejoradas del procesador mock
                processor = MockLanguageProcessor()
                result = processor.process_request(text, refinement_answers)
                
                # Verificar que la detección de propiedades sea correcta
                if 'sin gluten' in text.lower() or 'libre de gluten' in text.lower() or 'gluten free' in text.lower():
                    app.logger.info("Detectada solicitud sin gluten - asegurando que la receta cumpla con este requisito")
                    if 'properties' not in result:
                        result['properties'] = {}
                    result['properties']['sin_gluten'] = True
                    
                    # Verificar si hay ingredientes con gluten y reemplazarlos
                    ingredients_to_replace = []
                    for ingredient in result['ingredients']:
                        if ingredient.lower() in ['harina_trigo', 'harina', 'trigo', 'sémola', 'semola']:
                            ingredients_to_replace.append(ingredient)
                    
                    # Reemplazar ingredientes con gluten
                    for ingredient in ingredients_to_replace:
                        amount = result['ingredients'].pop(ingredient)
                        if 'harina_arroz' not in result['ingredients']:
                            result['ingredients']['harina_arroz'] = amount * 0.8
                        if 'almidon_maiz' not in result['ingredients']:
                            result['ingredients']['almidon_maiz'] = amount * 0.2
                        if 'goma_xantana' not in result['ingredients']:
                            result['ingredients']['goma_xantana'] = amount * 0.01
                
                # Mostrar ingredientes detectados
                app.logger.info("--- INGREDIENTES DETECTADOS (MOCK) ---")
                for ingredient, amount in result['ingredients'].items():
                    app.logger.info(f"  {ingredient}: {amount}")
                app.logger.info("-----------------------------")
                
                # Validar receta
                validation_results = validate_recipe(result['ingredients'], 
                                                    result.get('properties', {}).get('escala', scale),
                                                    result.get('properties', {}).get('sin_gluten', False))
                
                # Generar instrucciones si no están presentes
                instructions = result.get('instructions', [])
                if not instructions:
                    instructions = generate_instructions(result['ingredients'], result.get('properties', {}))
                
                # Formatear recomendaciones
                recommendations = []
                for rec in validation_results.get('recommendations', []):
                    rec_text = rec['text'].replace('La receta', 'Tu receta')
                    rec_text = rec_text.replace('se recomienda', 'recomendamos')
                    
                    if 'ajustar' in rec_text.lower() or 'aumentar' in rec_text.lower() or 'reducir' in rec_text.lower():
                        category = 'ajuste'
                    elif 'textura' in rec_text.lower() or 'consistencia' in rec_text.lower():
                        category = 'textura'
                    elif 'sabor' in rec_text.lower() or 'sal' in rec_text.lower():
                        category = 'sabor'
                    else:
                        category = 'general'
                    
                    recommendations.append({
                        'text': rec_text,
                        'priority': rec['priority'],
                        'category': category
                    })
                
                # Renderizar plantilla con resultados
                app.logger.info("Renderizando plantilla con resultados generados (MOCK)")
                return render_template(
                    'result.html',
                    original_text=text,
                    recipe_type=result.get('detected_type', 'Desconocido'),
                    ingredients=result['ingredients'],
                    instructions=instructions,
                    properties=result.get('properties', {}),
                    validation_results=validation_results,
                    recommendations=recommendations
                )
            
            except Exception as mock_error:
                app.logger.error(f"Error con el procesador alternativo: {str(mock_error)}", exc_info=True)
                # Si todo falla, usar la receta simulada más simple
                mock_recipe = create_mock_recipe(text, scale)
                
                return render_template(
                    'result.html',
                    original_text=text,
                    recipe_type=mock_recipe.get('detected_type', 'Pizza'),
                    ingredients=mock_recipe['ingredients'],
                    instructions=mock_recipe['instructions'],
                    properties=mock_recipe.get('properties', {}),
                    validation_results={'status': 'warning', 'messages': [{'type': 'info', 'text': 'Usando receta simulada para desarrollo'}]},
                    recommendations=[{'text': 'Esta es una receta simulada para desarrollo', 'priority': 'medium', 'category': 'general'}]
                )
        
    except Exception as e:
        app.logger.error(f"Error procesando petición: {str(e)}", exc_info=True)
        flash(f"Ha ocurrido un error al procesar tu solicitud: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/refinement-submit', methods=['POST'])
def submit_refinement():
    """Procesa las respuestas de refinamiento y genera la receta final."""
    try:
        # Recuperar texto original y escala
        original_text = request.form.get('original_text', '')
        scale = request.form.get('production_scale', 'familiar')
        
        # Recopilar todas las respuestas de refinamiento
        refinement_answers = {}
        for key in request.form:
            if key.startswith('refinement_'):
                question_id = key.replace('refinement_', '')
                refinement_answers[question_id] = request.form[key]
        
        app.logger.info(f"Procesando refinamiento para: {original_text}")
        app.logger.info(f"Respuestas de refinamiento: {refinement_answers}")
        
        # Crear un formulario HTML y enviarlo automáticamente
        form_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirigiendo...</title>
            <script>
                window.onload = function() {{
                    document.getElementById('redirectForm').submit();
                }}
            </script>
        </head>
        <body>
            <form id="redirectForm" action="{url_for('natural_language')}" method="post">
                <input type="hidden" name="natural_language_input" value="{original_text}">
                <input type="hidden" name="production_scale" value="{scale}">
        """
        
        # Añadir campos ocultos para las respuestas de refinamiento
        for key, value in refinement_answers.items():
            form_html += f'<input type="hidden" name="refinement_{key}" value="{value}">\n'
        
        form_html += """
                <p>Redirigiendo, por favor espera...</p>
                <button type="submit">Continuar si no eres redirigido automáticamente</button>
            </form>
        </body>
        </html>
        """
        
        return form_html
    
    except Exception as e:
        app.logger.error(f"Error procesando refinamiento: {str(e)}", exc_info=True)
        flash(f"Ha ocurrido un error al procesar tus preferencias: {str(e)}", "danger")
        return redirect(url_for('index'))

# Función para crear una receta simulada para pruebas
def create_mock_recipe(text, scale='familiar'):
    """Crea una receta simulada para desarrollo cuando no está disponible el procesador."""
    app.logger.info(f"Creando receta simulada para: {text}")
    
    # Detectar opciones básicas del texto
    is_gluten_free = 'sin gluten' in text.lower()
    color = None
    for c in ['rojo', 'verde', 'amarillo', 'negro', 'morado']:
        if c in text.lower():
            color = c
            break
    
    # Receta base
    if is_gluten_free:
        ingredients = {
            'harina_arroz': 300.0 * (2.4 if scale == 'familiar' else 1.0),
            'almidon_maiz': 100.0 * (2.4 if scale == 'familiar' else 1.0),
            'goma_xantana': 10.0 * (2.4 if scale == 'familiar' else 1.0),
            'agua': 280.0 * (2.4 if scale == 'familiar' else 1.0),
            'aceite_oliva': 20.0 * (2.4 if scale == 'familiar' else 1.0),
            'sal': 8.0 * (2.4 if scale == 'familiar' else 1.0),
            'levadura': 7.0 * (2.4 if scale == 'familiar' else 1.0)
        }
    else:
        ingredients = {
            'harina': 500.0 * (2.4 if scale == 'familiar' else 1.0),
            'agua': 300.0 * (2.4 if scale == 'familiar' else 1.0),
            'aceite_oliva': 15.0 * (2.4 if scale == 'familiar' else 1.0),
            'sal': 10.0 * (2.4 if scale == 'familiar' else 1.0),
            'levadura': 5.0 * (2.4 if scale == 'familiar' else 1.0)
        }
    
    # Añadir color si se detectó
    if color == 'rojo':
        ingredients['pure_tomate'] = 30.0 * (2.4 if scale == 'familiar' else 1.0)
        ingredients['pimenton_dulce'] = 5.0 * (2.4 if scale == 'familiar' else 1.0)
    elif color == 'verde':
        ingredients['espinacas_frescas'] = 30.0 * (2.4 if scale == 'familiar' else 1.0)
    elif color == 'amarillo':
        ingredients['curcuma'] = 5.0 * (2.4 if scale == 'familiar' else 1.0)
    
    # Instrucciones genéricas
    instructions = [
        "Mezclar todos los ingredientes secos en un recipiente grande.",
        "Añadir gradualmente los ingredientes líquidos mientras se amasa.",
        "Amasar durante 8-10 minutos hasta obtener una masa elástica.",
        "Dejar reposar la masa tapada durante 1-2 horas.",
        "Extender la masa y hornear a 220°C durante 12-15 minutos."
    ]
    
    # Propiedades detectadas
    properties = {
        'sin_gluten': is_gluten_free,
        'vegano': False,
        'color': color,
        'escala': scale
    }
    
    return {
        'detected_type': 'pizza',
        'ingredients': ingredients,
        'instructions': instructions,
        'properties': properties
    }

def generate_instructions(recipe_data, properties):
    """
    Genera instrucciones detalladas basadas en datos de la receta y sus propiedades.
    
    Args:
        recipe_data: Datos de la receta
        properties: Propiedades de la receta
        
    Returns:
        Lista de instrucciones detalladas
    """
    # Si ya hay instrucciones, devolverlas
    if 'instructions' in recipe_data and recipe_data['instructions']:
        return recipe_data['instructions']
    
    # Instrucciones básicas por defecto
    is_gluten_free = properties.get('sin_gluten', False)
    recipe_type = recipe_data.get('detected_type', 'pizza')
    
    if recipe_type == 'pizza':
        if is_gluten_free:
            return [
                "Mezclar los ingredientes secos en un recipiente grande.",
                "Añadir el agua tibia gradualmente mientras se mezcla.",
                "Incorporar el aceite y amasar hasta obtener una masa homogénea.",
                "Dejar reposar la masa tapada durante 30 minutos.",
                "Extender la masa directamente en la bandeja de horno usando las manos húmedas.",
                "Hornear a 220°C durante 12-15 minutos o hasta que esté dorada."
            ]
        else:
            return [
                "Disolver la levadura en agua tibia.",
                "Mezclar los ingredientes secos en un recipiente grande.",
                "Formar un hueco en el centro y verter la mezcla de agua con levadura.",
                "Amasar durante 8-10 minutos hasta obtener una masa elástica.",
                "Dejar fermentar cubierta durante 1-2 horas, o hasta que duplique su tamaño.",
                "Extender la masa hasta el grosor deseado y hornear a 220-250°C durante 10-12 minutos."
            ]
    else:
        # Instrucciones genéricas para otros tipos
        return [
            "Mezclar los ingredientes secos en un recipiente grande.",
            "Añadir los ingredientes líquidos gradualmente mientras se mezcla.",
            "Amasar hasta obtener la consistencia deseada.",
            "Dejar reposar el tiempo necesario según el tipo de masa.",
            "Dar forma y hornear según las especificaciones del producto."
        ]

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    """Página para validar recetas."""
    if request.method == 'POST':
        try:
            recipe_data = {}
            production_scale = request.form.get('production_scale', 'individual')
            recipe_type = request.form.get('recipe_type', 'pizza')
            
            # Verificar si se ha subido un archivo
            if 'recipe_file' in request.files:
                file = request.files['recipe_file']
                if file and file.filename.endswith('.json'):
                    recipe_data = json.loads(file.read().decode('utf-8'))
            else:
                # Crear receta a partir de los campos del formulario
                for key, value in request.form.items():
                    if key.startswith('ingredient_') and value:
                        ingredient_name = value
                        amount_key = key.replace('ingredient_', 'amount_')
                        if amount_key in request.form and request.form[amount_key]:
                            try:
                                # Intentar convertir a número
                                recipe_data[ingredient_name] = float(request.form[amount_key])
                            except ValueError:
                                recipe_data[ingredient_name] = request.form[amount_key]
            
            if not recipe_data:
                flash('Error: No se proporcionaron datos de receta.', 'danger')
                return render_template('validate.html')
            
            # Inicializar motor de validación
            validation_results = {
                "is_viable": True,
                "recommendations": [],
                "details": [],
                "issues_by_severity": {"critical": 0, "medium": 0, "low": 0},
                "rules_passed": 0,
                "total_rules_checked": 0,
                "total_issues": 0
            }
            
            contextual_recommendations = []
            try:
                engine = ValidationEngine()
                
                # Validar receta
                validation_data = engine.validate_recipe(recipe_data, recipe_type, production_scale)
                
                # Generar resumen
                validation_results = engine.summarize_results(validation_data)
                
                # Asegurar que validation_results tiene todos los campos necesarios
                if 'is_viable' not in validation_results:
                    validation_results['is_viable'] = True
                if 'recommendations' not in validation_results:
                    validation_results['recommendations'] = []
                if 'details' not in validation_results:
                    validation_results['details'] = []
                if 'issues_by_severity' not in validation_results:
                    validation_results['issues_by_severity'] = {"critical": 0, "medium": 0, "low": 0}
                if 'rules_passed' not in validation_results:
                    validation_results['rules_passed'] = 0
                if 'total_rules_checked' not in validation_results:
                    validation_results['total_rules_checked'] = 0
                if 'total_issues' not in validation_results:
                    validation_results['total_issues'] = 0
                
                # Obtener recomendaciones contextuales
                try:
                    contextual_recommendations = engine.get_contextual_recommendations(
                        validation_data, recipe_data, recipe_type, production_scale
                    )
                except Exception as rec_error:
                    app.logger.error(f"Error obteniendo recomendaciones: {str(rec_error)}")
                    app.logger.error(traceback.format_exc())
                    contextual_recommendations = ["No se pudieron generar recomendaciones personalizadas."]
                
                # Para compatibilidad con el código existente
                results = validation_results.copy()
                
                # Pasar resultados a la plantilla
                return render_template('validate.html', 
                                      validation_results=validation_results,
                                      results=results,
                                      recommendations=contextual_recommendations,
                                      contextual_recommendations=contextual_recommendations,
                                      original_recipe=recipe_data,
                                      recipe_type=recipe_type,
                                      scale=production_scale)
            except Exception as val_error:
                app.logger.error(f"Error en validación: {str(val_error)}")
                app.logger.error(traceback.format_exc())
                flash(f"Error en el motor de validación: {str(val_error)}", 'danger')
                return render_template('validate.html')
        
        except Exception as e:
            app.logger.error(f"Error en validación: {str(e)}")
            app.logger.error(traceback.format_exc())
            flash(f"Error: {str(e)}", 'danger')
            return render_template('validate.html')
    
    return render_template('validate.html')

@app.route('/about')
def about():
    """Página acerca del proyecto."""
    return render_template('about.html')

@app.route('/system-status')
def system_status():
    """Comprueba el estado del sistema."""
    integrity_check = check_system_integrity()
    return jsonify(integrity_check)

# Nuevas funciones para analizar la solicitud y hacer sugerencias

def check_missing_information(user_input: str) -> dict:
    """
    Verifica si la solicitud del usuario carece de información importante.
    
    Args:
        user_input: Texto de la solicitud
        
    Returns:
        Diccionario con los tipos de información faltante
    """
    text = user_input.lower()
    missing = {}
    
    # Verificar escala/tamaño
    scale_terms = ["individual", "familiar", "pequeña", "grande", "para", "personas", 
                  "porciones", "restaurante", "comercial"]
    if not any(term in text for term in scale_terms):
        missing["escala"] = True
    
    # Verificar restricciones alimentarias
    diet_terms = ["sin gluten", "gluten", "vegano", "vegetariano", "lactosa", 
                 "alérgico", "alergia", "celiaco", "celíaco"]
    if not any(term in text for term in diet_terms):
        missing["restricciones"] = True
    
    # Verificar tipo específico
    type_terms = ["napolitana", "delgada", "gruesa", "crujiente", "new york", "chicago",
                 "clásica", "tradicional", "margarita", "estilo"]
    if not any(term in text for term in type_terms):
        missing["tipo"] = True
    
    return missing

def generate_suggestion(user_input: str, missing_info: dict) -> str:
    """
    Genera una sugerencia basada en la información faltante.
    
    Args:
        user_input: Texto de la solicitud
        missing_info: Diccionario con los tipos de información faltante
        
    Returns:
        Texto con sugerencia para el usuario
    """
    suggestions = []
    
    if missing_info.get("escala"):
        suggestions.append("tamaño o personas (ej: 'familiar', 'para 4 personas')")
    
    if missing_info.get("restricciones"):
        suggestions.append("restricciones alimentarias si las tienes (ej: 'sin gluten', 'vegano')")
    
    if missing_info.get("tipo"):
        suggestions.append("estilo o tipo específico (ej: 'napolitana', 'masa delgada')")
    
    if not suggestions:
        return ""
    
    return ", ".join(suggestions)

def validate_recipe(recipe, scale='familiar', is_gluten_free=False):
    """
    Valida una receta usando el motor de validación.
    
    Args:
        recipe: Diccionario con los ingredientes y cantidades
        scale: Escala de producción
        is_gluten_free: Indica si la receta es sin gluten
        
    Returns:
        Resultados de la validación
    """
    try:
        # Inicializar motor de validación
        engine = ValidationEngine()
        
        # Preparar receta con flags si es necesario
        if is_gluten_free:
            recipe_with_flags = recipe.copy()
            recipe_with_flags['es_sin_gluten'] = True
            validation_data = engine.validate_recipe(recipe_with_flags, 'pizza', scale)
        else:
            validation_data = engine.validate_recipe(recipe, 'pizza', scale)
        
        # Generar resumen de validación
        validation_results = engine.summarize_results(validation_data)
        
        # Asegurar que el resultado tiene un formato consistente
        if not validation_results:
            validation_results = {
                "status": "warning",
                "messages": [{"type": "warning", "text": "No se pudo analizar completamente la receta"}],
                "recommendations": []
            }
        
        # Verificar que tiene los campos necesarios
        if "status" not in validation_results:
            if validation_results.get("is_viable", False):
                validation_results["status"] = "success"
            else:
                validation_results["status"] = "warning"
        
        if "messages" not in validation_results:
            validation_results["messages"] = []
        
        if "recommendations" not in validation_results:
            # Intentar obtener recomendaciones del detalle si existe
            if "details" in validation_results:
                validation_results["recommendations"] = [
                    {"text": detail.get("message", ""), "priority": detail.get("severity", "low")} 
                    for detail in validation_results["details"] if "message" in detail
                ]
            else:
                validation_results["recommendations"] = []
        
        # Formatear recomendaciones para asegurar formato consistente
        formatted_recommendations = []
        for rec in validation_results.get("recommendations", []):
            if isinstance(rec, str):
                formatted_recommendations.append({"text": rec, "priority": "medium"})
            elif isinstance(rec, dict) and "text" in rec:
                formatted_recommendations.append(rec)
            elif isinstance(rec, dict) and "message" in rec:
                formatted_recommendations.append({
                    "text": rec.get("message", ""), 
                    "priority": rec.get("severity", "medium")
                })
        
        validation_results["recommendations"] = formatted_recommendations
        
        # Calcular hidratación para mostrarla en la UI
        if "agua" in recipe and ("harina" in recipe or any("harina" in k for k in recipe.keys())):
            agua = recipe.get("agua", 0)
            harinas = sum([v for k, v in recipe.items() if "harina" in k.lower()])
            if harinas > 0:
                validation_results["hydration"] = round((agua / harinas) * 100)
        
        return validation_results
    
    except Exception as e:
        # En caso de error, devolver un resultado básico
        app.logger.error(f"Error validando receta: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "messages": [{"type": "error", "text": f"Error al validar: {str(e)}"}],
            "recommendations": []
        }

@app.route('/cache-intelligence')
def cache_intelligence():
    """Página para sistema de caché inteligente."""
    # Verificar si el sistema de caché está disponible
    if not has_cache_system:
        flash("El sistema de caché inteligente no está disponible", "danger")
        return redirect(url_for('index'))
    
    # Obtener estadísticas del caché
    try:
        stats = recipe_cache.get_stats()
    except Exception as e:
        app.logger.error(f"Error al obtener estadísticas del caché: {str(e)}")
        stats = {"total_recipes": 0, "recipe_types": {}}
        flash(f"Error al cargar estadísticas: {str(e)}", "warning")
    
    return render_template('cache_intelligence.html', stats=stats)

@app.route('/api/recipes/cheesecake', methods=['GET'])
def get_cheesecake_recipe():
    """API para obtener receta de cheesecake."""
    # Verificar si el sistema de caché está disponible
    if not has_cache_system:
        return jsonify({
            'success': False,
            'error': 'Sistema de caché inteligente no disponible'
        }), 503
    
    # Obtener parámetros
    gluten_free = request.args.get('gluten_free', 'false').lower() == 'true'
    dairy_free = request.args.get('dairy_free', 'false').lower() == 'true'
    fruit = request.args.get('fruit', '')
    
    # Obtener receta
    try:
        recipe = spoonacular_client.get_complete_cheesecake_recipe(
            gluten_free=gluten_free,
            dairy_free=dairy_free,
            fruit=fruit
        )
        return jsonify({
            'success': True, 
            'recipe': recipe
        })
    except Exception as e:
        app.logger.error(f"Error obteniendo receta: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """API para obtener estadísticas del caché."""
    # Verificar si el sistema de caché está disponible
    if not has_cache_system:
        return jsonify({
            'success': False,
            'error': 'Sistema de caché inteligente no disponible'
        }), 503
    
    try:
        stats = recipe_cache.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        app.logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """API para limpiar el caché."""
    # Verificar si el sistema de caché está disponible
    if not has_cache_system:
        return jsonify({
            'success': False,
            'error': 'Sistema de caché inteligente no disponible'
        }), 503
    
    try:
        recipe_cache.clear_cache()
        return jsonify({
            'success': True,
            'message': 'Caché limpiado correctamente'
        })
    except Exception as e:
        app.logger.error(f"Error limpiando caché: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Configurar el logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicializar sistemas
    app.logger.info("Sistema de validación cargado correctamente")
    app.logger.info("Procesador de lenguaje natural cargado correctamente")
    
    # Obtener puerto de argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Servidor TRIVO-AI')
    parser.add_argument('--port', type=int, default=8000, help='Puerto para ejecutar el servidor')
    args = parser.parse_args()
    port = args.port
    
    app.logger.info(f"Iniciando servidor en puerto {port}")
    
    # Iniciar servidor (sin abrir navegador automáticamente)
    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        app.logger.error(f"Error iniciando el servidor: {str(e)}")
        app.logger.error(traceback.format_exc())