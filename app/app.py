"""
Aplicación web para TRIVO-AI con arquitectura modular para servicios por suscripción.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
import json
import sys
import logging
import traceback
from datetime import datetime
import random
import uuid
from functools import wraps

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar componentes del sistema
try:
    from trivo.features.optimizer.optimizer import RecipeOptimizer
    from trivo.features.validator.validator import RecipeValidator
    from trivo.features.nlp.language_processor import LanguageProcessor
    language_processor_available = True
except ImportError:
    language_processor_available = False
    print("Advertencia: Módulo de procesamiento de lenguaje natural no disponible.")

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('trivo-ai')

# Constantes
MOCK_MODE = True  # Activa el modo de simulación cuando el procesador real no está disponible
DARK_MODE_DEFAULT = True  # Activa el modo oscuro por defecto

# Configuración de módulos y planes
MODULOS = {
    "formulacion": {
        "nombre": "Formulación Básica",
        "descripcion": "Creación básica de recetas de masa",
        "icono": "bi-file-earmark-text"
    },
    "optimizacion": {
        "nombre": "Optimización",
        "descripcion": "Optimiza recetas existentes",
        "icono": "bi-gear"
    },
    "validacion": {
        "nombre": "Validación",
        "descripcion": "Valida recetas para producción",
        "icono": "bi-check-circle"
    },
    "lenguaje_natural": {
        "nombre": "Lenguaje Natural",
        "descripcion": "Crea recetas a partir de descripciones en lenguaje natural",
        "icono": "bi-chat-text"
    },
    "ciclo_vida": {
        "nombre": "Ciclo de Vida",
        "descripcion": "Gestión completa del ciclo de vida del producto",
        "icono": "bi-arrow-repeat"
    }
}

PLANES = {
    "basico": {
        "nombre": "Básico",
        "modulos": ["formulacion"],
        "intentos": 5,
        "precio": 29.99
    },
    "profesional": {
        "nombre": "Profesional",
        "modulos": ["formulacion", "optimizacion", "validacion"],
        "intentos": 20,
        "precio": 99.99
    },
    "enterprise": {
        "nombre": "Enterprise",
        "modulos": ["formulacion", "optimizacion", "validacion", "lenguaje_natural", "ciclo_vida"],
        "intentos": -1,  # ilimitado
        "precio": 249.99
    },
    "demo": {
        "nombre": "Demo",
        "modulos": ["formulacion", "optimizacion", "validacion", "lenguaje_natural"],
        "intentos": 3,
        "precio": 0
    }
}

# Simular base de datos de usuarios (en producción, usar una base de datos real)
USUARIOS = {
    "demo": {
        "id": "usr_demo123",
        "nombre": "Usuario Demo",
        "email": "demo@trivo.ai",
        "plan": "demo",
        "intentos_restantes": 3,
        "fecha_registro": datetime.now().isoformat()
    },
    "premium": {
        "id": "usr_premium456",
        "nombre": "Usuario Premium",
        "email": "premium@trivo.ai",
        "plan": "enterprise",
        "intentos_restantes": -1,
        "fecha_registro": datetime.now().isoformat()
    }
}

# Middleware para verificar acceso a módulos
def requiere_modulo(nombre_modulo):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener usuario actual (en producción, usar sistema de autenticación real)
            usuario_id = session.get('usuario_id', 'demo')
            usuario = USUARIOS.get(usuario_id)
            
            if not usuario:
                flash('Sesión inválida. Por favor inicia sesión nuevamente.', 'danger')
                return redirect(url_for('home'))
                
            plan = PLANES.get(usuario.get('plan'))
            
            if not plan:
                flash('Plan no válido. Contacta a soporte.', 'danger')
                return redirect(url_for('home'))
                
            if nombre_modulo not in plan.get('modulos', []):
                flash(f'Tu plan actual no incluye acceso al módulo "{MODULOS.get(nombre_modulo, {}).get("nombre")}"', 'warning')
                return redirect(url_for('planes'))
                
            # Verificar intentos disponibles (excepto si son ilimitados)
            if plan.get('intentos') != -1 and usuario.get('intentos_restantes', 0) <= 0:
                flash('Has agotado tus intentos disponibles. Actualiza tu plan para continuar.', 'warning')
                return redirect(url_for('planes'))
                
            # Reducir contador de intentos si no es ilimitado
            if plan.get('intentos') != -1:
                USUARIOS[usuario_id]['intentos_restantes'] -= 1
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Iniciar sesión de usuario (simplificado)
@app.route('/login/<usuario_id>')
def login(usuario_id):
    if usuario_id in USUARIOS:
        session['usuario_id'] = usuario_id
        flash(f'Has iniciado sesión como {USUARIOS[usuario_id]["nombre"]}', 'success')
    else:
        flash('Usuario no encontrado', 'danger')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Has cerrado sesión', 'success')
    return redirect(url_for('home'))

@app.route('/')
def home():
    """Página de inicio."""
    # Aplicar modo oscuro por defecto si no está definido
    if 'dark_mode' not in session:
        session['dark_mode'] = DARK_MODE_DEFAULT
        
    dark_mode = session.get('dark_mode', DARK_MODE_DEFAULT)
    # Obtener información del usuario actual
    usuario_id = session.get('usuario_id', 'demo')
    usuario = USUARIOS.get(usuario_id)
    plan = PLANES.get(usuario.get('plan')) if usuario else None
    
    return render_template('index.html', 
                          dark_mode=dark_mode, 
                          usuario=usuario, 
                          plan=plan, 
                          modulos=MODULOS, 
                          modulos_disponibles=plan.get('modulos') if plan else [])

@app.route('/planes')
def planes():
    """Página de planes de suscripción."""
    dark_mode = session.get('dark_mode', DARK_MODE_DEFAULT)
    usuario_id = session.get('usuario_id', 'demo')
    usuario = USUARIOS.get(usuario_id)
    plan_actual = usuario.get('plan') if usuario else None
    
    return render_template('planes.html', 
                          dark_mode=dark_mode, 
                          planes=PLANES, 
                          modulos=MODULOS, 
                          plan_actual=plan_actual)

@app.route('/optimize', methods=['GET', 'POST'])
@requiere_modulo('formulacion')
def optimize():
    """Página de optimización de recetas."""
    dark_mode = session.get('dark_mode', DARK_MODE_DEFAULT)
    
    # Obtener información del usuario actual
    usuario_id = session.get('usuario_id', 'demo')
    usuario = USUARIOS.get(usuario_id)
    plan = PLANES.get(usuario.get('plan')) if usuario else None
    
    # Verificar si tiene acceso al módulo de optimización
    tiene_optimizacion = 'optimizacion' in plan.get('modulos', []) if plan else False
    
    if request.method == 'POST':
        try:
            # Procesar formulario
            ingredients = request.form.getlist('ingredient[]')
            quantities = request.form.getlist('quantity[]')
            
            # Crear diccionario de ingredientes
            recipe_ingredients = {}
            for i, ingredient in enumerate(ingredients):
                if ingredient and quantities[i]:
                    recipe_ingredients[ingredient] = float(quantities[i])
            
            # Si tiene acceso a optimización, optimizar receta
            optimized_recipe = None
            validation_result = None
            
            if tiene_optimizacion:
                # Configurar optimizador
                optimizer = RecipeOptimizer(
                    ingredients=recipe_ingredients,
                    constraints={
                        "max_cost": float(request.form.get('max_cost', 10)),
                        "min_quality": float(request.form.get('min_quality', 70))
                    }
                )
                
                # Optimizar receta
                optimized_recipe = optimizer.optimize()
                
                # Validar receta optimizada si tiene acceso a validación
                if 'validacion' in plan.get('modulos', []):
                    validator = RecipeValidator(production_scale=request.form.get('scale', 'small_business'))
                    validation_result = validator.validate(optimized_recipe)
            
            # Generar ID único para la receta
            recipe_id = str(uuid.uuid4())
            
            # En producción, guardar en base de datos
            
            # Renderizar plantilla con resultados
            return render_template(
                'optimize.html',
                original_recipe=recipe_ingredients,
                optimized_recipe=optimized_recipe,
                validation_result=validation_result,
                dark_mode=dark_mode,
                usuario=usuario,
                plan=plan,
                tiene_optimizacion=tiene_optimizacion,
                recipe_id=recipe_id
            )
            
        except Exception as e:
            logger.error(f"Error en optimización: {str(e)}")
            flash(f"Error en la optimización: {str(e)}", "danger")
            return render_template('optimize.html', 
                                 dark_mode=dark_mode, 
                                 usuario=usuario, 
                                 plan=plan, 
                                 tiene_optimizacion=tiene_optimizacion)
    
    return render_template('optimize.html', 
                         dark_mode=dark_mode, 
                         usuario=usuario, 
                         plan=plan, 
                         tiene_optimizacion=tiene_optimizacion)

@app.route('/validate', methods=['GET', 'POST'])
@requiere_modulo('validacion')
def validate():
    """Página de validación de recetas."""
    dark_mode = session.get('dark_mode', DARK_MODE_DEFAULT)
    
    # Obtener información del usuario
    usuario_id = session.get('usuario_id', 'demo')
    usuario = USUARIOS.get(usuario_id)
    
    if request.method == 'POST':
        try:
            # Manejar carga de archivo
            if 'recipe_file' in request.files:
                file = request.files['recipe_file']
                if file.filename.endswith('.json'):
                    recipe = json.load(file)
                    
                    # Validar receta
                    validator = RecipeValidator(production_scale=request.form.get('scale', 'small_business'))
                    validation_result = validator.validate(recipe)
                    
                    # Registrar el uso del módulo
                    logger.info(f"Usuario {usuario_id} realizó validación de receta")
                    
                    return render_template('validate.html', 
                                         recipe=recipe, 
                                         validation_result=validation_result, 
                                         dark_mode=dark_mode,
                                         usuario=usuario)
            
            return render_template('validate.html', 
                                 error="Archivo no válido o no seleccionado", 
                                 dark_mode=dark_mode,
                                 usuario=usuario)
            
        except Exception as e:
            logger.error(f"Error en validación: {str(e)}")
            flash(f"Error en la validación: {str(e)}", "danger")
            return render_template('validate.html', 
                                 dark_mode=dark_mode,
                                 usuario=usuario)
    
    return render_template('validate.html', 
                         dark_mode=dark_mode,
                         usuario=usuario)

@app.route('/natural-language', methods=['POST'])
@requiere_modulo('lenguaje_natural')
def natural_language():
    """Procesa solicitudes en lenguaje natural."""
    try:
        # Obtener el texto del formulario
        natural_text = request.form.get('natural_text', '')
        
        if not natural_text:
            flash('Por favor, ingresa una descripción de tu receta deseada.', 'warning')
            return redirect(url_for('home'))
        
        # Obtener el procesador de lenguaje natural
        processor = get_language_processor()
            
        # Procesar la solicitud y obtener la receta
        recipe = processor.process_request(natural_text)
        logger.info(f"Receta generada correctamente: {recipe['name']}")
        
        # Generar instrucciones para la receta
        instructions = generate_instructions(recipe)
        
        # Guardar en sesión
        session['recipe'] = recipe
        session['instructions'] = instructions
        session['recipe_request'] = natural_text
        
        # Registrar uso del módulo
        usuario_id = session.get('usuario_id', 'demo')
        logger.info(f"Usuario {usuario_id} utilizó procesamiento lenguaje natural con éxito")
        
        # Redirigir a la página de optimización con los resultados
        flash('¡Receta generada exitosamente a partir de tu descripción!', 'success')
        return redirect(url_for('optimize'))
        
    except Exception as e:
        # Mejorar el manejo de errores con información detallada
        error_info = str(e)
        logger.error(f"Error en procesamiento de lenguaje natural: {error_info}")
        logger.error(traceback.format_exc())
        
        # Guardar información de error en sesión para debugging
        session['nlp_error'] = {
            'message': error_info,
            'traceback': traceback.format_exc(),
            'input': request.form.get('natural_text', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Informar al usuario de manera amigable
        flash(f'Lo sentimos, ocurrió un error al procesar tu solicitud. Estamos trabajando para resolverlo.', 'danger')
        return redirect(url_for('home'))

# Ruta para el ciclo de vida del producto
@app.route('/lifecycle/<recipe_id>')
@requiere_modulo('ciclo_vida')
def lifecycle(recipe_id):
    """Página de ciclo de vida del producto."""
    dark_mode = session.get('dark_mode', DARK_MODE_DEFAULT)
    
    # En producción, cargar receta desde base de datos
    recipe = {
        "id": recipe_id,
        "name": "Receta de prueba",
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "stages": [
            {"name": "Desarrollo", "status": "completed", "date": (datetime.now().isoformat())},
            {"name": "Pruebas", "status": "in_progress", "date": None},
            {"name": "Producción", "status": "pending", "date": None},
            {"name": "Distribución", "status": "pending", "date": None}
        ]
    }
    
    return render_template('lifecycle.html', 
                         dark_mode=dark_mode, 
                         recipe=recipe)

def generate_instructions(recipe):
    """Genera instrucciones paso a paso basadas en la receta y sus propiedades."""
    properties = recipe.get("properties", {})
    ingredients = recipe.get("ingredients", [])
    
    # Base de instrucciones
    instructions = []
    
    # Paso 1: Preparación de ingredientes secos
    dry_ingredients = [ing for ing in ingredients if ing["unit"] == "g"]
    wet_ingredients = [ing for ing in ingredients if ing["unit"] in ["ml", "l"]]
    
    # Instrucción para mezclar secos
    dry_names = ", ".join([ing["name"] for ing in dry_ingredients[:-1]]) + f" y {dry_ingredients[-1]['name']}" if len(dry_ingredients) > 1 else dry_ingredients[0]["name"]
    instructions.append(f"1. En un recipiente grande, mezcla {dry_names}.")
    
    # Instrucción para la levadura
    instructions.append("2. En un recipiente aparte, disuelve la levadura en agua tibia (35°C) y deja reposar 5 minutos hasta que se active y forme espuma.")
    
    # Instrucción para mezclar todo
    instructions.append("3. Forma un hueco en el centro de los ingredientes secos y vierte la mezcla de levadura.")
    
    oil_ingredient = next((ing for ing in ingredients if "aceite" in ing["name"].lower()), None)
    if oil_ingredient:
        instructions.append(f"4. Añade el {oil_ingredient['name']} y comienza a mezclar hasta incorporar todos los ingredientes.")
    
    # Amasado (diferente para sin gluten)
    if "sin gluten" in properties.get("restricciones", []):
        instructions.append("5. Mezcla hasta obtener una masa homogénea. La masa sin gluten será más pegajosa que la tradicional, esto es normal.")
        instructions.append("6. Cubre la masa con papel film y deja reposar en un lugar cálido durante 45 minutos.")
    else:
        instructions.append("5. Amasa sobre una superficie enharinada durante 8-10 minutos hasta obtener una masa elástica y suave.")
        instructions.append("6. Forma una bola, colócala en un recipiente ligeramente aceitado, cúbrela y deja reposar en un lugar cálido por 1-2 horas hasta que duplique su tamaño.")
    
    # Instrucciones de formado según escala
    if properties.get("escala") == "familiar":
        instructions.append("7. Divide la masa en 2 porciones iguales para hacer 2 pizzas familiares.")
    elif properties.get("escala") == "industrial":
        instructions.append("7. Divide la masa en porciones de 250g para hacer varias pizzas de tamaño estándar.")
    else:
        instructions.append("7. Estira la masa sobre una superficie enharinada hasta obtener el grosor deseado.")
    
    instructions.append("8. Precalienta el horno a 220°C (o lo más alto posible).")
    instructions.append("9. Coloca la masa en una bandeja para horno, añade tus ingredientes favoritos y hornea durante 12-15 minutos o hasta que el borde esté dorado y crujiente.")
    
    # Instrucciones específicas según tipo
    if properties.get("tipo_receta") != "básica":
        instructions.append(f"10. Para una pizza {properties.get('tipo_receta')}, recomendamos los siguientes ingredientes:")
        
        if properties.get("tipo_receta") == "margarita":
            instructions.append("   - Salsa de tomate, mozzarella fresca, albahaca fresca y un poco de aceite de oliva.")
        elif properties.get("tipo_receta") == "napolitana":
            instructions.append("   - Salsa de tomate, anchoas, aceitunas negras, alcaparras y orégano.")
        elif properties.get("tipo_receta") == "vegetariana":
            instructions.append("   - Salsa de tomate, mozzarella, pimientos, champiñones, cebolla, calabacín y aceitunas.")
        elif properties.get("tipo_receta") == "hawaiana":
            instructions.append("   - Salsa de tomate, mozzarella, jamón y piña.")
        elif properties.get("tipo_receta") == "pepperoni":
            instructions.append("   - Salsa de tomate, mozzarella abundante y pepperoni.")
    
    return instructions

@app.route('/about')
def about():
    """Página acerca de."""
    dark_mode = session.get('dark_mode', DARK_MODE_DEFAULT)
    return render_template('about.html', dark_mode=dark_mode)

@app.route('/toggle-theme')
def toggle_theme():
    session['dark_mode'] = not session.get('dark_mode', DARK_MODE_DEFAULT)
    return redirect(request.referrer or url_for('home'))

# Definir un procesador mock para desarrollo
class MockLanguageProcessor:
    def __init__(self):
        self.recipe_types = ["margarita", "napolitana", "hawaiana", "vegetariana", "pepperoni"]
        self.dietary_restrictions = ["sin gluten", "vegana", "vegetariana", "baja en sodio", "sin lactosa"]
        self.colors = ["roja", "blanca", "integral", "verde", "negra"]
        self.production_scales = ["familiar", "industrial", "restaurante", "pequeña"]

    def process_request(self, text):
        # Extraer propiedades del texto
        properties = {}
        text = text.lower()
        
        # Detectar tipo de receta
        for tipo in self.recipe_types:
            if tipo in text:
                properties["tipo_receta"] = tipo
                break
        else:
            properties["tipo_receta"] = "básica"
        
        # Detectar restricciones dietéticas
        properties["restricciones"] = []
        for restriccion in self.dietary_restrictions:
            if restriccion in text:
                properties["restricciones"].append(restriccion)
        
        # Detectar color
        for color in self.colors:
            if color in text:
                properties["color"] = color
                break
        else:
            properties["color"] = "blanca"
        
        # Detectar escala
        for escala in self.production_scales:
            if escala in text:
                properties["escala"] = escala
                break
        else:
            properties["escala"] = "pequeña"
        
        # Detectar optimización nutricional
        properties["optimizacion_nutricional"] = "nutricional" in text or "nutritiva" in text or "nutricionalmente" in text
        
        # Generar ingredientes base según las propiedades
        recipe = {
            "name": f"Masa de Pizza {properties['tipo_receta'].capitalize()} {properties['color'].capitalize()}",
            "description": f"Masa de pizza {properties['color']} para {properties['escala']}, optimizada según tus requerimientos.",
            "ingredients": self.generate_ingredients(properties),
            "properties": properties
        }
        
        return recipe
    
    def generate_ingredients(self, properties):
        ingredients = []
        
        # Ingrediente base: harina
        if "sin gluten" in properties.get("restricciones", []):
            ingredients.append({
                "name": "Harina de arroz",
                "quantity": 250.0,
                "unit": "g"
            })
            ingredients.append({
                "name": "Almidón de maíz",
                "quantity": 100.0,
                "unit": "g"
            })
            ingredients.append({
                "name": "Goma xantana",
                "quantity": 5.0,
                "unit": "g"
            })
        else:
            ingredients.append({
                "name": "Harina de trigo",
                "quantity": 350.0,
                "unit": "g"
            })
        
        # Agua
        ingredients.append({
            "name": "Agua",
            "quantity": 200.0,
            "unit": "ml"
        })
        
        # Levadura
        ingredients.append({
            "name": "Levadura seca",
            "quantity": 7.0,
            "unit": "g"
        })
        
        # Sal (menos si es baja en sodio)
        salt_quantity = 3.0 if "baja en sodio" in properties.get("restricciones", []) else 5.0
        ingredients.append({
            "name": "Sal",
            "quantity": salt_quantity,
            "unit": "g"
        })
        
        # Aceite
        ingredients.append({
            "name": "Aceite de oliva",
            "quantity": 15.0,
            "unit": "ml"
        })
        
        # Ingredientes para color
        if properties.get("color") == "roja":
            ingredients.append({
                "name": "Remolacha en polvo",
                "quantity": 15.0,
                "unit": "g"
            })
        elif properties.get("color") == "verde":
            ingredients.append({
                "name": "Espinaca en polvo",
                "quantity": 20.0,
                "unit": "g"
            })
        elif properties.get("color") == "negra":
            ingredients.append({
                "name": "Tinta de calamar",
                "quantity": 10.0,
                "unit": "g"
            })
        elif properties.get("color") == "integral":
            # Reemplazar harina blanca por integral
            for i, ingredient in enumerate(ingredients):
                if ingredient["name"] == "Harina de trigo":
                    ingredients[i] = {
                        "name": "Harina integral",
                        "quantity": 350.0,
                        "unit": "g"
                    }
        
        # Ingredientes adicionales para optimización nutricional
        if properties.get("optimizacion_nutricional"):
            ingredients.append({
                "name": "Semillas de lino molidas",
                "quantity": 10.0,
                "unit": "g"
            })
            ingredients.append({
                "name": "Semillas de chía",
                "quantity": 10.0,
                "unit": "g"
            })
        
        return ingredients

def get_language_processor():
    """Obtener una instancia del procesador de lenguaje natural"""
    try:
        # Intentar importar el procesador real
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        try:
            # Primero intentar desde trivo (nueva estructura)
            from trivo.features.nlp.language_processor import LanguageProcessor
            logger.info("Usando procesador de lenguaje natural de trivo")
            return LanguageProcessor()
        except ImportError:
            # Luego intentar desde src (estructura alternativa)
            from src.features.nlp.language_processor import LanguageProcessor
            logger.info("Usando procesador de lenguaje natural de src")
            return LanguageProcessor()
    except Exception as e:
        logger.warning(f"No se pudo cargar el procesador de lenguaje real: {str(e)}")
        logger.info("Usando procesador simulado para desarrollo")
        return MockLanguageProcessor()

if __name__ == '__main__':
    # Cambiar el puerto a 8080 para evitar conflictos
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

def main():
    """Función principal para el punto de entrada."""
    # Obtener puerto desde variables de entorno o usar el valor predeterminado
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)