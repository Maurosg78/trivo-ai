"""
Aplicación web para TRIVO-AI.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import json
import sys
import logging
import traceback
from datetime import datetime

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar componentes del sistema
try:
    from src.features.optimizer.optimizer import RecipeOptimizer
    from src.features.validator.validator import RecipeValidator
    from src.features.nlp.language_processor import LanguageProcessor
except ImportError as e:
    print(f"Error al importar módulos: {e}")

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('trivo-ai')

@app.route('/')
def home():
    """Página de inicio."""
    dark_mode = session.get('dark_mode', False)
    return render_template('index.html', dark_mode=dark_mode)

@app.route('/optimize', methods=['GET', 'POST'])
def optimize():
    """Página de optimización de recetas."""
    dark_mode = session.get('dark_mode', False)
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
            
            # Validar receta optimizada
            validator = RecipeValidator(production_scale=request.form.get('scale', 'small_business'))
            validation_result = validator.validate(optimized_recipe)
            
            return render_template(
                'optimize.html',
                original_recipe=recipe_ingredients,
                optimized_recipe=optimized_recipe,
                validation_result=validation_result,
                dark_mode=dark_mode
            )
            
        except Exception as e:
            return render_template('optimize.html', error=str(e), dark_mode=dark_mode)
    
    return render_template('optimize.html', dark_mode=dark_mode)

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    """Página de validación de recetas."""
    dark_mode = session.get('dark_mode', False)
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
                    
                    return render_template('validate.html', recipe=recipe, validation_result=validation_result, dark_mode=dark_mode)
            
            return render_template('validate.html', error="Archivo no válido o no seleccionado", dark_mode=dark_mode)
            
        except Exception as e:
            return render_template('validate.html', error=str(e), dark_mode=dark_mode)
    
    return render_template('validate.html', dark_mode=dark_mode)

@app.route('/natural-language', methods=['POST'])
def natural_language():
    """Procesa solicitudes en lenguaje natural."""
    try:
        user_query = request.form.get('query', '')
        logger.info(f"Solicitud de lenguaje natural recibida: {user_query}")
        
        # Intentar importar el procesador de lenguaje natural
        try:
            from src.features.nlp.language_processor import LanguageProcessor
            processor = LanguageProcessor()
        except ImportError as e:
            logger.warning(f"No se pudo importar el procesador de lenguaje natural: {e}")
            # Usar un procesador simulado para desarrollo
            processor = MockLanguageProcessor()
        
        # Procesar la consulta
        result = processor.process_request(user_query)
        
        # Comprobar si es una receta sin gluten con propiedades específicas
        if ("sin gluten" in result.get("properties", {}).get("restrictions", []) and 
            "gluten_free_properties" in result.get("properties", {})):
            try:
                # Intentar importar y utilizar el optimizador específico para sin gluten
                from src.features.optimizer.gluten_free_optimizer import GlutenFreeOptimizer
                
                # Determinar tipo de producto (por defecto pizza)
                product_type = "pizza"
                if result["properties"].get("pizza_type"):
                    product_type = "pizza"
                
                # Extraer propiedades específicas para sin gluten
                gluten_free_props = result["properties"].get("gluten_free_properties", {})
                
                # Crear instancia del optimizador
                optimizer = GlutenFreeOptimizer()
                
                # Ejecutar optimización
                optimized_result = optimizer.optimize(
                    product_type=product_type,
                    desired_properties=gluten_free_props
                )
                
                # Integrar resultado optimizado con resultado original
                result["recipe"]["ingredients"] = optimized_result["ingredients"]
                result["recipe"]["instructions"] = optimized_result["instructions"]
                
                # Añadir recomendaciones
                result["recommendations"] = optimized_result["recommendations"]
                
                logger.info("Receta sin gluten optimizada con algoritmo genético")
            except ImportError as e:
                logger.warning(f"No se pudo importar el optimizador sin gluten: {e}")
                logger.info("Usando receta sin gluten estándar")
        
        # Generar instrucciones basadas en las propiedades detectadas
        instructions = generate_instructions(result)
        
        # Guardar en la sesión para mostrar en la página de optimización
        session['recipe_data'] = result
        session['instructions'] = instructions
        
        return redirect(url_for('optimize'))
    
    except Exception as e:
        logger.error(f"Error procesando solicitud de lenguaje natural: {str(e)}")
        logger.error(traceback.format_exc())
        session['error'] = f"Error al procesar la solicitud: {str(e)}"
        return redirect(url_for('home'))

def generate_instructions(result):
    """Genera instrucciones paso a paso basadas en la receta y propiedades"""
    recipe = result.get("recipe", {})
    properties = result.get("properties", {})
    
    instructions = []
    
    # Paso 1: Preparación de ingredientes
    instructions.append({
        "step": 1,
        "title": "Preparación de ingredientes",
        "description": "Pesa y prepara todos los ingredientes secos y líquidos por separado."
    })
    
    # Paso 2: Mezclado de ingredientes secos
    dry_ingredients = []
    for ingredient, data in recipe.items():
        if ingredient not in ["agua", "aceite_oliva"] and ingredient != "levadura":
            name = ingredient.replace("_", " ")
            dry_ingredients.append(f"{data['cantidad']} {data['unidad']} de {name}")
    
    step2_desc = "Mezcla en un recipiente amplio los siguientes ingredientes secos: " + ", ".join(dry_ingredients) + "."
    
    # Ajustar si es sin gluten
    if properties.get("restricciones") and "sin_gluten" in properties["restricciones"]:
        step2_desc += " Asegúrate de que todos los ingredientes sean certificados sin gluten."
    
    instructions.append({
        "step": 2,
        "title": "Mezcla de ingredientes secos",
        "description": step2_desc
    })
    
    # Paso 3: Preparación de levadura
    if "levadura" in recipe:
        instructions.append({
            "step": 3,
            "title": "Activación de la levadura",
            "description": f"En un recipiente pequeño, disuelve {recipe['levadura']['cantidad']} {recipe['levadura']['unidad']} de levadura en 50 ml de agua tibia (35°C). Deja reposar por 5-10 minutos hasta que se forme espuma."
        })
    
    # Paso 4: Mezclado de masa
    water_amount = recipe.get("agua", {}).get("cantidad", 0)
    oil_amount = recipe.get("aceite_oliva", {}).get("cantidad", 0)
    
    instructions.append({
        "step": 4,
        "title": "Formación de la masa",
        "description": f"Forma un volcán con los ingredientes secos y agrega la mezcla de levadura en el centro. Añade gradualmente {water_amount} ml de agua y {oil_amount} ml de aceite de oliva. Mezcla hasta integrar todos los ingredientes."
    })
    
    # Paso 5: Amasado
    knead_time = "10-12 minutos" if not (properties.get("restricciones") and "sin_gluten" in properties["restricciones"]) else "5-7 minutos"
    
    instructions.append({
        "step": 5,
        "title": "Amasado",
        "description": f"Amasa enérgicamente sobre una superficie ligeramente enharinada durante {knead_time} hasta obtener una masa elástica y homogénea."
    })
    
    # Paso 6: Fermentación
    fermentation_time = "1-2 horas" if not (properties.get("restricciones") and "sin_gluten" in properties["restricciones"]) else "45-60 minutos"
    
    instructions.append({
        "step": 6,
        "title": "Primera fermentación",
        "description": f"Coloca la masa en un recipiente ligeramente aceitado, cúbrela con un paño húmedo y deja fermentar en un lugar cálido durante {fermentation_time} hasta que duplique su tamaño."
    })
    
    # Paso 7: División y formado
    portions = "4 porciones iguales" if properties.get("tipo") == "familiar" else "2 porciones iguales"
    
    instructions.append({
        "step": 7,
        "title": "División y formado",
        "description": f"Desgasifica la masa presionando suavemente y divídela en {portions}. Forma bolas suaves y déjalas reposar cubiertas durante 15 minutos."
    })
    
    # Paso 8: Estirado de la masa
    instructions.append({
        "step": 8,
        "title": "Estirado de la masa",
        "description": "Estira cada porción de masa sobre una superficie enharinada hasta formar discos uniformes del grosor deseado."
    })
    
    # Paso 9: Segunda fermentación
    instructions.append({
        "step": 9,
        "title": "Segunda fermentación",
        "description": "Coloca las masas estiradas sobre papel de hornear y déjalas reposar durante 20-30 minutos adicionales."
    })
    
    # Paso 10: Horneado
    instructions.append({
        "step": 10,
        "title": "Horneado",
        "description": "Precalienta el horno a 250°C. Hornea las bases de pizza durante 5-7 minutos hasta que estén ligeramente doradas. Añade tus ingredientes preferidos y continúa horneando según la receta de tu pizza."
    })
    
    # Paso adicional para tipos específicos de pizza
    pizza_type = properties.get("tipo_pizza", "")
    if pizza_type and pizza_type != "clásica":
        toppings = {
            "margarita": "salsa de tomate, mozzarella fresca y hojas de albahaca",
            "pepperoni": "salsa de tomate, mozzarella y rodajas de pepperoni",
            "vegetariana": "salsa de tomate, mozzarella, pimientos, calabacín, berenjenas y champiñones",
            "hawaiana": "salsa de tomate, mozzarella, jamón y piña"
        }
        
        if pizza_type in toppings:
            instructions.append({
                "step": 11,
                "title": f"Preparación de pizza {pizza_type}",
                "description": f"Para completar tu pizza {pizza_type}, añade {toppings[pizza_type]} sobre la base prehorneada y hornea 7-10 minutos más hasta que el queso esté burbujeante y dorado."
            })
    
    return instructions

@app.route('/about')
def about():
    """Página acerca de."""
    dark_mode = session.get('dark_mode', False)
    return render_template('about.html', dark_mode=dark_mode)

@app.route('/toggle-theme')
def toggle_theme():
    session['dark_mode'] = not session.get('dark_mode', False)
    return redirect(request.referrer or url_for('home'))

# Procesador de lenguaje natural simulado para desarrollo
class MockLanguageProcessor:
    def process_request(self, query):
        logger.info(f"Usando procesador simulado para: {query}")
        
        # Análisis simple basado en palabras clave
        properties = {
            "tipo": "familiar" if "familiar" in query.lower() else "individual",
            "color": self._detect_color(query),
            "restricciones": self._detect_restrictions(query),
            "nutricional": "optimizado" if any(kw in query.lower() for kw in ["nutricional", "nutrición", "saludable"]) else "estándar",
            "tipo_pizza": self._detect_pizza_type(query)
        }
        
        # Crear una receta básica adaptada a las propiedades detectadas
        recipe = self._generate_recipe(properties)
        
        return {
            "query": query,
            "properties": properties,
            "recipe": recipe
        }
    
    def _detect_color(self, query):
        if "rojo" in query.lower() or "rojiza" in query.lower():
            return "rojo"
        elif "verde" in query.lower() or "verdosa" in query.lower():
            return "verde"
        elif "negro" in query.lower() or "negra" in query.lower():
            return "negro"
        else:
            return "natural"
    
    def _detect_restrictions(self, query):
        restrictions = []
        if any(term in query.lower() for term in ["sin gluten", "gluten free", "celíaco", "celiaco"]):
            restrictions.append("sin_gluten")
        if any(term in query.lower() for term in ["vegano", "vegan", "sin productos animales"]):
            restrictions.append("vegano")
        if any(term in query.lower() for term in ["vegetariano", "vegetarian"]):
            restrictions.append("vegetariano")
        return restrictions
    
    def _detect_pizza_type(self, query):
        if "margarita" in query.lower():
            return "margarita"
        elif "pepperoni" in query.lower():
            return "pepperoni"
        elif "vegetariana" in query.lower() and not "vegetariano" in query.lower():
            return "vegetariana"
        elif "hawaiana" in query.lower():
            return "hawaiana"
        else:
            return "clásica"
    
    def _generate_recipe(self, properties):
        # Receta base
        recipe = {
            "harina": {"cantidad": 500, "unidad": "g"},
            "agua": {"cantidad": 325, "unidad": "ml"},
            "levadura": {"cantidad": 7, "unidad": "g"},
            "sal": {"cantidad": 10, "unidad": "g"},
            "aceite_oliva": {"cantidad": 15, "unidad": "ml"}
        }
        
        # Ajuste por tamaño
        if properties["tipo"] == "familiar":
            for ingredient in recipe:
                recipe[ingredient]["cantidad"] *= 1.5
        
        # Ajuste por restricciones
        if "sin_gluten" in properties["restricciones"]:
            recipe.pop("harina")
            recipe["harina_arroz"] = {"cantidad": 300, "unidad": "g"}
            recipe["almidon_maiz"] = {"cantidad": 150, "unidad": "g"}
            recipe["goma_xantana"] = {"cantidad": 10, "unidad": "g"}
        
        # Ajuste por color
        if properties["color"] == "rojo":
            recipe["remolacha_polvo"] = {"cantidad": 20, "unidad": "g"}
        elif properties["color"] == "verde":
            recipe["espinaca_polvo"] = {"cantidad": 20, "unidad": "g"}
        elif properties["color"] == "negro":
            recipe["carbon_activado"] = {"cantidad": 10, "unidad": "g"}
        
        # Ajuste nutricional
        if properties["nutricional"] == "optimizado":
            recipe["semillas_lino"] = {"cantidad": 20, "unidad": "g"}
            recipe["semillas_chia"] = {"cantidad": 15, "unidad": "g"}
        
        return recipe

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)