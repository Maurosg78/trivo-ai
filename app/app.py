import os
import sys
import json
import uuid
import secrets
import logging
from datetime import datetime
from functools import wraps
import random
import time

# Flask y otros imports importantes
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración básica
DEBUG = True
PORT = int(os.getenv("PORT", "8081"))
# Clave para acceso a la demo (para uso interno o presentaciones)
DEMO_ACCESS_KEY = os.getenv('DEMO_ACCESS_KEY', 'trivo-demo-access')

# Inicializar la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Configuración de directorios de datos
app.config['DATA_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
app.config['UPLOAD_FOLDER'] = os.path.join(app.config['DATA_FOLDER'], 'uploads')

# Crear directorios si no existen
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger('trivo-ai')

# Funciones de utilidad
def get_current_user():
    # En una aplicación real, esto verificaría la sesión
    if 'user_id' in session:
        user_id = session['user_id']
        # Buscar usuario en la base de datos
        return {"id": user_id, "name": f"Usuario {user_id}", "role": "admin"}
    return None

def is_demo_access_allowed():
    """Verifica si se tiene acceso a la demo"""
    return 'demo_access' in session and session['demo_access'] == True

def demo_required(f):
    """Decorador para rutas que requieren acceso de demo."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_demo_access_allowed():
            flash('Esta funcionalidad solo está disponible para usuarios autorizados.', 'warning')
            return redirect(url_for('demo_login'))
        return f(*args, **kwargs)
    return decorated_function

# Procesador de lenguaje natural simulado
def mock_language_processing(user_text):
    """
    Simula el procesamiento de lenguaje natural para generar una receta.
    En una versión real, esto llamaría a un modelo de IA.
    """
    # Simulamos un tiempo de procesamiento
    time.sleep(1)
    
    # Generamos una receta básica con campos aleatorios
    pizza_types = ["Margarita", "Pepperoni", "Hawaiana", "Vegetariana", "Cuatro Quesos", "Mexicana"]
    dificultad_levels = ["Fácil", "Media", "Difícil"]
    
    # Detectamos características especiales en el texto
    is_gluten_free = "sin gluten" in user_text.lower() or "gluten free" in user_text.lower()
    is_halloween = "halloween" in user_text.lower() or "calabaza" in user_text.lower()
    is_orange = "naranja" in user_text.lower() or "orange" in user_text.lower()
    is_family_size = "familiar" in user_text.lower() or "family" in user_text.lower() or "grande" in user_text.lower()
    
    # Extraemos algunas palabras clave del texto del usuario
    keywords = [word for word in user_text.lower().split() 
                if len(word) > 3 and word not in ["para", "como", "quiero", "hacer", "pizza", "gluten", "naranja", "halloween"]]
    
    nombre = f"Pizza {random.choice(pizza_types)}"
    # Modificamos el nombre según las características
    if is_gluten_free:
        nombre = "Pizza Sin Gluten"
    if is_halloween:
        nombre += " de Halloween"
    if keywords:
        nombre += f" con {random.choice(keywords).capitalize()}"
    
    # Generamos ingredientes basados en el tipo de pizza
    ingredientes = []
    
    # Base de la masa según si es sin gluten o no
    if is_gluten_free:
        ingredientes.append({"name": "Mezcla de harinas sin gluten", "amount": "300", "unit": "g"})
        ingredientes.append({"name": "Goma xantana", "amount": "5", "unit": "g"})
    else:
        ingredientes.append({"name": "Masa de pizza", "amount": "250", "unit": "g"})
    
    # Ingredientes comunes
    ingredientes.append({"name": "Salsa de tomate", "amount": "100", "unit": "ml"})
    ingredientes.append({"name": "Queso mozzarella", "amount": "200", "unit": "g"})
    
    # Añadimos ingredientes especiales para Halloween/naranja
    if is_halloween or is_orange:
        ingredientes.append({"name": "Calabaza asada", "amount": "150", "unit": "g"})
        ingredientes.append({"name": "Zanahoria rallada", "amount": "50", "unit": "g"})
        ingredientes.append({"name": "Colorante alimentario naranja", "amount": "1", "unit": "cucharadita"})
    
    # Añadimos ingredientes basados en el texto del usuario
    if "vegetariana" in user_text.lower():
        ingredientes.extend([
            {"name": "Pimiento", "amount": "50", "unit": "g"},
            {"name": "Cebolla", "amount": "50", "unit": "g"},
            {"name": "Champiñones", "amount": "100", "unit": "g"}
        ])
    elif "pepperoni" in user_text.lower():
        ingredientes.append({"name": "Pepperoni", "amount": "100", "unit": "g"})
    elif "hawaiana" in user_text.lower():
        ingredientes.extend([
            {"name": "Jamón", "amount": "100", "unit": "g"},
            {"name": "Piña", "amount": "80", "unit": "g"}
        ])
    
    # Generamos método de preparación específico
    metodo = []
    
    if is_gluten_free:
        metodo.extend([
            "Precalienta el horno a 200°C.",
            "Mezcla las harinas sin gluten con la goma xantana, sal y levadura.",
            "Añade agua tibia y aceite de oliva y amasa hasta obtener una masa homogénea.",
            "Deja reposar la masa en un lugar cálido por 30 minutos."
        ])
    else:
        metodo.append("Precalienta el horno a 220°C.")
        
    metodo.extend([
        "Estira la masa hasta formar un círculo uniforme.",
        "Extiende la salsa de tomate sobre la masa.",
        "Añade el queso mozzarella rallado de manera uniforme."
    ])
    
    if is_halloween or is_orange:
        metodo.append("Distribuye la calabaza asada y zanahoria rallada por encima.")
        metodo.append("Si deseas un color más intenso, mezcla unas gotas de colorante naranja con aceite de oliva y pincela los bordes.")
    else:
        metodo.append("Distribuye los ingredientes adicionales por encima.")
    
    metodo.extend([
        f"Hornea durante {12 if is_gluten_free else 15}-{15 if is_gluten_free else 18} minutos hasta que la masa esté dorada y el queso burbujeante.",
        "Retira del horno y deja reposar 2 minutos antes de cortar."
    ])
    
    if is_halloween:
        metodo.append("Decora con aceitunas negras formando arañas o corta queso en forma de fantasmas para una presentación temática.")
    
    # Generamos explicaciones personalizadas
    explanations = []
    
    if is_gluten_free:
        explanations.append("Se utilizó una mezcla de harinas sin gluten con goma xantana para lograr una textura similar a la masa tradicional.")
    
    if is_halloween or is_orange:
        explanations.append("Se incorporaron ingredientes de color naranja y decoraciones temáticas para adaptarse a la celebración de Halloween.")
    
    if is_family_size:
        explanations.append("Las proporciones se ajustaron para una pizza de tamaño familiar que rinde más porciones.")
    
    # Añadimos explicaciones estándar
    explanations.append("La selección de ingredientes se basó en tu solicitud específica.")
    explanations.append("El equilibrio entre los ingredientes se optimizó para el mejor sabor.")
    explanations.append("La temperatura y tiempo de cocción se ajustaron para este tipo específico de pizza.")
    
    # Generamos un tip profesional contextualizado
    tips = []
    
    if is_gluten_free:
        tips.extend([
            "Para una masa sin gluten más ligera, deja reposar la masa al menos 1 hora antes de hornearla.",
            "Asegúrate de que todos los ingredientes, no solo la masa, sean certificados sin gluten para evitar contaminación cruzada."
        ])
    
    if is_halloween or is_orange:
        tips.extend([
            "Puedes añadir calabaza asada previamente con un poco de canela para darle un sabor dulce y especiado.",
            "Las semillas de calabaza tostadas añaden un toque crujiente a la pizza."
        ])
    
    if is_family_size:
        tips.append("Para pizzas grandes, hornea la masa 3-4 minutos antes de añadir los ingredientes para evitar que quede cruda en el centro.")
    
    # Tips generales
    tips.extend([
        "Para una masa más crujiente, precalienta también la bandeja de horno.",
        "Utiliza mozzarella fresca para un sabor más auténtico.",
        "El secreto de una buena pizza está en la calidad de la salsa de tomate.",
        "Añade un chorrito de aceite de oliva antes de hornear para mayor sabor."
    ])
    
    # Ajustamos las porciones para pizza familiar
    porciones = 8 if is_family_size else random.randint(2, 4)
    
    recipe = {
        "id": str(random.randint(1000, 9999)),
        "nombre": nombre,
        "descripcion": f"Una deliciosa {nombre.lower()} preparada especialmente según tu solicitud.",
        "ingredientes": ingredientes,
        "metodo": metodo,
        "tiempo_preparacion": random.randint(20, 30) if is_gluten_free else random.randint(10, 20),
        "tiempo_coccion": random.randint(12, 15),
        "porciones": porciones,
        "dificultad": "Difícil" if is_gluten_free else random.choice(dificultad_levels),
        "tags": ["Pizza", "Horno"] + 
               (["Sin Gluten"] if is_gluten_free else []) + 
               (["Halloween", "Temática"] if is_halloween else []) + 
               (["Familiar", "Grande"] if is_family_size else []) +
               [keyword.capitalize() for keyword in keywords[:2]],
        "notas": "Esta receta puede personalizarse según tus preferencias añadiendo o quitando ingredientes."
    }
    
    # Guardamos temporalmente la receta generada (en una aplicación real usaríamos una base de datos)
    recipe_filename = f"app/static/data/recipe_{recipe['id']}.json"
    os.makedirs(os.path.dirname(recipe_filename), exist_ok=True)
    
    with open(recipe_filename, 'w') as f:
        json.dump({
            "recipe": recipe,
            "input_text": user_text,
            "explanations": explanations,
            "key_tip": random.choice(tips),
            "created_at": datetime.now().isoformat()
        }, f)
    
    return recipe

# Rutas simplificadas para que la aplicación arranque

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/demo')
def demo_home():
    """Página principal de demostración"""
    if is_demo_access_allowed():
        return render_template('demo_home.html')
    return redirect(url_for('demo_login'))

@app.route('/demo-login', methods=['GET', 'POST'])
def demo_login():
    """Página de acceso a la demo"""
    if request.method == 'POST':
        access_key = request.form.get('access_key', '')
        
        if access_key == DEMO_ACCESS_KEY:
            session['demo_access'] = True
            flash('¡Bienvenido al modo demostración!', 'success')
            return redirect(url_for('demo_home'))
        else:
            flash('Clave de acceso incorrecta', 'error')
    
    return render_template('demo_login.html')

@app.route('/demo-logout')
def demo_logout():
    """Cerrar sesión de demo"""
    session.pop('demo_access', None)
    flash('Has salido del modo demostración', 'info')
    return redirect(url_for('index'))

@app.route('/test-form')
def test_form():
    """Formulario de prueba para natural language"""
    return render_template('test_form.html')

@app.route('/natural-language', methods=['GET', 'POST'])
def natural_language():
    if request.method == 'POST':
        # Verificar acceso de demostración
        if not is_demo_access_allowed():
            session['demo_access'] = True  # Para propósitos de prueba, habilitamos temporalmente el acceso
            
        user_text = request.form.get('user_text', '')
        
        if not user_text:
            flash('Por favor ingresa un texto para generar la receta', 'error')
            return redirect(url_for('index'))
        
        # Procesamos el texto usando nuestro mock
        recipe = mock_language_processing(user_text)
        
        # Guardamos el ID de la receta en la sesión para recuperarla después
        session['last_recipe_id'] = recipe['id']
        
        # Redirigimos a la página de resultados
        return redirect(url_for('recipe_result', recipe_id=recipe['id']))
    
    # Para solicitudes GET, simplemente mostramos el formulario
    return render_template('index.html')

@app.route('/recipe-result/<recipe_id>')
def recipe_result(recipe_id):
    # Recuperamos la receta desde el archivo JSON
    recipe_filename = f"app/static/data/recipe_{recipe_id}.json"
    
    try:
        with open(recipe_filename, 'r') as f:
            data = json.load(f)
            
        return render_template('recipe_result.html', 
                              recipe=data['recipe'],
                              input_text=data['input_text'],
                              explanations=data['explanations'],
                              key_tip=data['key_tip'])
    except FileNotFoundError:
        flash('Receta no encontrada', 'error')
        return redirect(url_for('index'))

@app.route('/suppliers')
def manage_suppliers():
    """Gestión de proveedores de ingredientes"""
    # Carga los proveedores desde el archivo JSON
    suppliers = {}
    suppliers_file = os.path.join(app.config['DATA_FOLDER'], 'suppliers.json')
    
    if os.path.exists(suppliers_file):
        try:
            with open(suppliers_file, 'r') as f:
                suppliers = json.load(f)
        except Exception as e:
            app.logger.error(f"Error al cargar proveedores: {e}")
            flash("Error al cargar la lista de proveedores", "error")
    
    return render_template('manage_suppliers.html', suppliers=suppliers)

@app.route('/api/suppliers/<supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """API para obtener datos de un proveedor específico"""
    suppliers_file = os.path.join(app.config['DATA_FOLDER'], 'suppliers.json')
    
    if os.path.exists(suppliers_file):
        try:
            with open(suppliers_file, 'r') as f:
                suppliers = json.load(f)
                
            if supplier_id in suppliers:
                return jsonify(suppliers[supplier_id])
            else:
                return jsonify({"error": "Proveedor no encontrado"}), 404
        except Exception as e:
            app.logger.error(f"Error al obtener proveedor: {e}")
            return jsonify({"error": "Error al procesar la solicitud"}), 500
    else:
        return jsonify({"error": "No hay proveedores registrados"}), 404

@app.route('/add_supplier', methods=['POST'])
def add_supplier():
    """Añadir un nuevo proveedor"""
    # Obtener datos del formulario
    name = request.form.get('name')
    contact_person = request.form.get('contact_person', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    notes = request.form.get('notes', '')
    
    # Validar datos mínimos
    if not name:
        flash("El nombre del proveedor es obligatorio", "error")
        return redirect(url_for('manage_suppliers'))
    
    # Cargar proveedores existentes
    suppliers = {}
    suppliers_file = os.path.join(app.config['DATA_FOLDER'], 'suppliers.json')
    
    if os.path.exists(suppliers_file):
        try:
            with open(suppliers_file, 'r') as f:
                suppliers = json.load(f)
        except Exception as e:
            app.logger.error(f"Error al cargar proveedores: {e}")
    
    # Generar ID único para el nuevo proveedor
    supplier_id = str(uuid.uuid4())
    
    # Crear nuevo proveedor
    suppliers[supplier_id] = {
        'name': name,
        'contact_person': contact_person,
        'phone': phone,
        'email': email,
        'address': address,
        'notes': notes,
        'ingredients': [],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    # Guardar cambios
    try:
        # Asegurar que existe el directorio
        os.makedirs(os.path.dirname(suppliers_file), exist_ok=True)
        
        with open(suppliers_file, 'w') as f:
            json.dump(suppliers, f, indent=4)
        
        flash(f"Proveedor '{name}' añadido correctamente", "success")
    except Exception as e:
        app.logger.error(f"Error al guardar proveedor: {e}")
        flash("Error al guardar el proveedor", "error")
    
    return redirect(url_for('manage_suppliers'))

@app.route('/update_supplier', methods=['POST'])
def update_supplier():
    """Actualizar un proveedor existente"""
    # Obtener datos del formulario
    supplier_id = request.form.get('supplier_id')
    name = request.form.get('name')
    contact_person = request.form.get('contact_person', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    notes = request.form.get('notes', '')
    
    # Validar datos mínimos
    if not supplier_id or not name:
        flash("Faltan campos obligatorios", "error")
        return redirect(url_for('manage_suppliers'))
    
    # Cargar proveedores existentes
    suppliers_file = os.path.join(app.config['DATA_FOLDER'], 'suppliers.json')
    
    try:
        with open(suppliers_file, 'r') as f:
            suppliers = json.load(f)
        
        if supplier_id not in suppliers:
            flash("Proveedor no encontrado", "error")
            return redirect(url_for('manage_suppliers'))
        
        # Actualizar datos del proveedor
        suppliers[supplier_id].update({
            'name': name,
            'contact_person': contact_person,
            'phone': phone,
            'email': email,
            'address': address,
            'notes': notes,
            'updated_at': datetime.now().isoformat()
        })
        
        # Guardar cambios
        with open(suppliers_file, 'w') as f:
            json.dump(suppliers, f, indent=4)
        
        flash(f"Proveedor '{name}' actualizado correctamente", "success")
    except Exception as e:
        app.logger.error(f"Error al actualizar proveedor: {e}")
        flash("Error al actualizar el proveedor", "error")
    
    return redirect(url_for('manage_suppliers'))

@app.route('/delete_supplier', methods=['POST'])
def delete_supplier():
    """Eliminar un proveedor"""
    supplier_id = request.form.get('supplier_id')
    
    if not supplier_id:
        flash("ID de proveedor no proporcionado", "error")
        return redirect(url_for('manage_suppliers'))
    
    # Cargar proveedores existentes
    suppliers_file = os.path.join(app.config['DATA_FOLDER'], 'suppliers.json')
    
    try:
        with open(suppliers_file, 'r') as f:
            suppliers = json.load(f)
        
        if supplier_id not in suppliers:
            flash("Proveedor no encontrado", "error")
            return redirect(url_for('manage_suppliers'))
        
        # Guardar el nombre antes de eliminar
        supplier_name = suppliers[supplier_id]['name']
        
        # Eliminar proveedor
        del suppliers[supplier_id]
        
        # Guardar cambios
        with open(suppliers_file, 'w') as f:
            json.dump(suppliers, f, indent=4)
        
        flash(f"Proveedor '{supplier_name}' eliminado correctamente", "success")
    except Exception as e:
        app.logger.error(f"Error al eliminar proveedor: {e}")
        flash("Error al eliminar el proveedor", "error")
    
    return redirect(url_for('manage_suppliers'))

@app.route('/cost-analysis')
def cost_analysis():
    """Página principal de análisis de costos"""
    return render_template('cost_analysis.html')

@app.route('/optimize')
def optimize():
    """Página de creación de recetas"""
    return render_template('optimize.html')

@app.route('/validate')
def validate():
    """Página de validación de recetas"""
    return render_template('validate.html')

@app.route('/about')
def about():
    """Página 'Acerca de'"""
    return render_template('about.html')

@app.route('/accessibility')
def accessibility_guide():
    """Guía de Accesibilidad"""
    return render_template('accessibility_guide.html')

@app.route('/login/<usuario_id>')
def login(usuario_id):
    """Inicio de sesión simplificado (solo para desarrollo)"""
    session['user_id'] = usuario_id
    flash(f"Sesión iniciada como Usuario {usuario_id}", "success")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash("Sesión cerrada correctamente", "success")
    return redirect(url_for('index'))

@app.route('/api/generate-recipe', methods=['POST'])
def api_generate_recipe():
    """API para generar recetas sin interfaz web"""
    if request.method == 'POST':
        user_text = request.json.get('user_text', '')
        
        if not user_text:
            return jsonify({"error": "Texto vacío. Por favor proporciona una descripción de la receta."}), 400
        
        # Procesamos el texto usando nuestro mock
        recipe = mock_language_processing(user_text)
        
        # Preparamos la respuesta
        recipe_filename = f"app/static/data/recipe_{recipe['id']}.json"
        
        try:
            with open(recipe_filename, 'r') as f:
                data = json.load(f)
                
            return jsonify({
                "success": True,
                "recipe": data['recipe'],
                "input_text": data['input_text'],
                "explanations": data['explanations'],
                "key_tip": data['key_tip']
            })
        except FileNotFoundError:
            return jsonify({"error": "Error al guardar la receta"}), 500

# Importar el asistente de recetas
from recipe_assistant import RecipeAssistant

# Instancia global del asistente (en producción usaría una solución basada en sesiones)
recipe_assistant = RecipeAssistant()

@app.route('/assistant')
def recipe_assistant_view():
    """Interfaz del asistente de recetas"""
    return render_template('assistant_chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API para el chat con el asistente de recetas"""
    data = request.json
    user_message = data.get('message', '')
    
    # En una aplicación real, manejaríamos el estado de la conversación por sesión
    # Aquí simplemente usamos una instancia global para simplicidad
    response = recipe_assistant.respond(user_message)
    
    return jsonify({"response": response})

@app.route('/api/generate_recipe', methods=['POST'])
def generate_recipe_api():
    """API para generar recetas basadas en la conversación"""
    # Construir el prompt para el generador
    prompt = recipe_assistant.construct_recipe_prompt()
    
    # Generar la receta utilizando el procesador de lenguaje natural
    recipe = mock_language_processing(prompt)
    
    return jsonify(recipe)

# Rutas para fichas técnicas industriales
@app.route('/recipe-sheets')
def list_recipe_sheets():
    """Muestra la lista de fichas técnicas disponibles."""
    from app.recipe_sheet import RecipeSheet
    
    recipe_sheet_manager = RecipeSheet(app.config['DATA_FOLDER'])
    sheets = recipe_sheet_manager.list_recipe_sheets()
    
    return render_template('recipe_sheets/list_recipe_sheets.html', 
                          sheets=sheets,
                          title="Fichas Técnicas Industriales")

@app.route('/recipe-sheets/<recipe_id>')
def view_recipe_sheet(recipe_id):
    """Muestra una ficha técnica específica."""
    from app.recipe_sheet import RecipeSheet
    
    recipe_sheet_manager = RecipeSheet(app.config['DATA_FOLDER'])
    recipe = recipe_sheet_manager.get_recipe_sheet(recipe_id)
    
    if not recipe:
        flash('Ficha técnica no encontrada', 'error')
        return redirect(url_for('list_recipe_sheets'))
    
    return render_template('view_recipe_sheet.html', recipe=recipe)

@app.route('/recipe-sheets/new', methods=['GET', 'POST'])
def new_recipe_sheet():
    """Crea una nueva ficha técnica."""
    if request.method == 'GET':
        return render_template('recipe_sheets/edit_recipe_sheet.html', 
                              recipe=None, 
                              title="Nueva Ficha Técnica")
    
    # Procesar el formulario POST
    from app.recipe_sheet import RecipeSheet
    
    try:
        # Obtener datos del formulario
        recipe_data = {
            "name": request.form.get('name'),
            "description": request.form.get('description'),
            "category": request.form.get('category'),
            "target_market": request.form.get('target_market', 'General'),
            "serving_size": request.form.get('serving_size'),
            "yield": {
                "amount": float(request.form.get('yield_amount', 0)),
                "unit": request.form.get('yield_unit', 'g')
            },
            "difficulty": request.form.get('difficulty', 'Media'),
            "shelf_life": {
                "ambient": request.form.get('shelf_life_ambient', '1 día'),
                "refrigerated": request.form.get('shelf_life_refrigerated', '3 días'),
                "frozen": request.form.get('shelf_life_frozen', '30 días')
            },
            "preparation_time": int(request.form.get('preparation_time', 0)),
            "mixing_time": int(request.form.get('mixing_time', 0)),
            "fermentation_time": int(request.form.get('fermentation_time', 0)),
            "baking_time": int(request.form.get('baking_time', 0)),
            "cooling_time": int(request.form.get('cooling_time', 0)),
            "appearance": request.form.get('appearance', ''),
            "texture": request.form.get('texture', ''),
            "taste": request.form.get('taste', ''),
            "aroma": request.form.get('aroma', ''),
            "equipment": request.form.getlist('equipment')
        }
        
        # Procesar ingredientes (múltiples campos de un formulario dinámico)
        ingredients = []
        ingredient_names = request.form.getlist('ingredient_name[]')
        ingredient_amounts = request.form.getlist('ingredient_amount[]')
        ingredient_units = request.form.getlist('ingredient_unit[]')
        ingredient_functions = request.form.getlist('ingredient_function[]')
        ingredient_criticals = request.form.getlist('ingredient_critical[]')
        
        for i in range(len(ingredient_names)):
            if ingredient_names[i].strip():  # Si el nombre no está vacío
                ingredients.append({
                    "name": ingredient_names[i],
                    "amount": float(ingredient_amounts[i]) if ingredient_amounts[i] else 0,
                    "unit": ingredient_units[i],
                    "function": ingredient_functions[i] if i < len(ingredient_functions) else "",
                    "critical": i < len(ingredient_criticals) and ingredient_criticals[i] == "on"
                })
        
        # Procesar pasos del proceso
        process_steps = []
        step_orders = request.form.getlist('step_order[]')
        step_names = request.form.getlist('step_name[]')
        step_descriptions = request.form.getlist('step_description[]')
        step_times = request.form.getlist('step_time[]')
        step_temperatures = request.form.getlist('step_temperature[]')
        step_criticals = request.form.getlist('step_critical[]')
        
        for i in range(len(step_names)):
            if step_names[i].strip():  # Si el nombre no está vacío
                process_steps.append({
                    "order": int(step_orders[i]) if step_orders[i] else i+1,
                    "name": step_names[i],
                    "description": step_descriptions[i],
                    "time": int(step_times[i]) if step_times[i] and step_times[i].isdigit() else 0,
                    "temperature": step_temperatures[i] if i < len(step_temperatures) else "",
                    "critical": i < len(step_criticals) and step_criticals[i] == "on"
                })
        
        # Crear la ficha técnica
        recipe_sheet_manager = RecipeSheet(app.config['DATA_FOLDER'])
        recipe_sheet = recipe_sheet_manager.create_recipe_sheet(
            recipe_data=recipe_data,
            ingredients=ingredients,
            process_steps=process_steps,
            author=session.get('username', 'Sistema')
        )
        
        flash(f'Ficha técnica "{recipe_data["name"]}" creada exitosamente', 'success')
        return redirect(url_for('view_recipe_sheet', recipe_id=recipe_sheet['id']))
        
    except Exception as e:
        flash(f'Error al crear la ficha técnica: {str(e)}', 'error')
        return redirect(url_for('list_recipe_sheets'))

@app.route('/recipe-sheets/<recipe_id>/edit', methods=['GET', 'POST'])
def edit_recipe_sheet(recipe_id):
    """Edita una ficha técnica existente."""
    from app.recipe_sheet import RecipeSheet
    
    recipe_sheet_manager = RecipeSheet(app.config['DATA_FOLDER'])
    recipe = recipe_sheet_manager.get_recipe_sheet(recipe_id)
    
    if not recipe:
        flash('Ficha técnica no encontrada', 'error')
        return redirect(url_for('list_recipe_sheets'))
    
    if request.method == 'GET':
        return render_template('recipe_sheets/edit_recipe_sheet.html', 
                              recipe=recipe, 
                              title=f"Editar {recipe['recipe_info']['name']}")
    
    # Procesar el formulario POST - similar a new_recipe_sheet
    try:
        # Obtener datos del formulario (similar a new_recipe_sheet)
        # ...
        
        # Actualizar la ficha técnica
        updates = {
            # Preparar las actualizaciones según los datos del formulario
        }
        
        updated_recipe = recipe_sheet_manager.update_recipe_sheet(recipe_id, updates)
        
        if updated_recipe:
            flash(f'Ficha técnica "{updated_recipe["recipe_info"]["name"]}" actualizada exitosamente', 'success')
            return redirect(url_for('view_recipe_sheet', recipe_id=recipe_id))
        else:
            flash('Error al actualizar la ficha técnica', 'error')
            return redirect(url_for('edit_recipe_sheet', recipe_id=recipe_id))
            
    except Exception as e:
        flash(f'Error al editar la ficha técnica: {str(e)}', 'error')
        return redirect(url_for('view_recipe_sheet', recipe_id=recipe_id))

@app.route('/recipe-sheets/<recipe_id>/delete', methods=['POST'])
def delete_recipe_sheet(recipe_id):
    """Elimina una ficha técnica."""
    from app.recipe_sheet import RecipeSheet
    
    recipe_sheet_manager = RecipeSheet(app.config['DATA_FOLDER'])
    success = recipe_sheet_manager.delete_recipe_sheet(recipe_id)
    
    if success:
        flash('Ficha técnica eliminada exitosamente', 'success')
    else:
        flash('Error al eliminar la ficha técnica', 'error')
    
    return redirect(url_for('list_recipe_sheets'))

@app.route('/recipe-sheets/<recipe_id>/pdf')
def download_recipe_sheet_pdf(recipe_id):
    """Genera y descarga una ficha técnica en formato PDF."""
    from app.recipe_sheet import RecipeSheet
    
    recipe_sheet_manager = RecipeSheet(app.config['DATA_FOLDER'])
    pdf_path = recipe_sheet_manager.generate_pdf(recipe_id)
    
    if not pdf_path or not os.path.exists(pdf_path):
        flash('Error al generar el PDF', 'error')
        return redirect(url_for('view_recipe_sheet', recipe_id=recipe_id))
    
    # Devolver el archivo PDF para descarga
    return send_file(pdf_path, download_name=f"ficha_tecnica_{recipe_id}.pdf", as_attachment=True)

@app.route('/recipe-sheets/<recipe_id>/production-sheet', methods=['GET', 'POST'])
def production_sheet(recipe_id):
    """Genera una hoja de producción para un lote específico."""
    from app.recipe_sheet import RecipeSheet
    
    recipe_sheet_manager = RecipeSheet(app.config['DATA_FOLDER'])
    
    if request.method == 'POST':
        try:
            batch_size = float(request.form.get('batch_size', 1))
            production_data = recipe_sheet_manager.generate_production_sheet(recipe_id, batch_size)
            
            if not production_data:
                flash('Error al generar la hoja de producción', 'error')
                return redirect(url_for('view_recipe_sheet', recipe_id=recipe_id))
            
            # Guardar temporalmente la hoja de producción
            session['production_sheet'] = production_data
            
            return render_template('recipe_sheets/production_sheet.html', 
                                  production=production_data,
                                  title="Hoja de Producción")
                                  
        except ValueError as e:
            flash('Por favor ingrese un valor numérico válido para el tamaño del lote', 'error')
            return redirect(url_for('view_recipe_sheet', recipe_id=recipe_id))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('view_recipe_sheet', recipe_id=recipe_id))
    
    # Método GET muestra el formulario para ingresar el tamaño del lote
    recipe = recipe_sheet_manager.get_recipe_sheet(recipe_id)
    if not recipe:
        flash('Ficha técnica no encontrada', 'error')
        return redirect(url_for('list_recipe_sheets'))
    
    return render_template('recipe_sheets/scale_recipe.html', 
                          recipe=recipe,
                          title=f"Escalar {recipe['recipe_info']['name']}")

# Iniciar la aplicación
if __name__ == '__main__':
    try:
        print(f"Iniciando aplicación TRIVO-AI en http://localhost:{PORT}")
        app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}")
        print(f"Error al iniciar la aplicación: {e}") 