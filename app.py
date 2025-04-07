#!/usr/bin/env python
import os
import sys
import json
import logging
from flask import Flask, request, jsonify, render_template

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar el sistema de caché inteligente y procesador de lenguaje
from src.features.external_api import get_spoonacular_client, get_recipe_cache
try:
    from src.features.nlp.language_processor import LanguageProcessor
    nlp_available = True
    logger.info("Procesador de lenguaje natural disponible")
except ImportError:
    nlp_available = False
    logger.warning("Procesador de lenguaje natural no disponible")

# Crear aplicación Flask
app = Flask(__name__, template_folder='templates')

# Inicializar componentes
cache = get_recipe_cache()
client = get_spoonacular_client()
processor = LanguageProcessor() if nlp_available else None

@app.route('/')
def index():
    """Página principal."""
    # Obtener estadísticas del caché
    stats = cache.get_stats()
    return render_template('index.html', stats=stats)

@app.route('/api/recipes/cheesecake', methods=['GET'])
def get_cheesecake():
    """API para obtener receta de cheesecake."""
    # Obtener parámetros
    gluten_free = request.args.get('gluten_free', 'false').lower() == 'true'
    dairy_free = request.args.get('dairy_free', 'false').lower() == 'true'
    fruit = request.args.get('fruit', '')
    
    # Obtener receta
    try:
        recipe = client.get_complete_cheesecake_recipe(
            gluten_free=gluten_free,
            dairy_free=dairy_free,
            fruit=fruit
        )
        return jsonify({
            'success': True, 
            'recipe': recipe
        })
    except Exception as e:
        logger.error(f"Error obteniendo receta: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/natural-language', methods=['POST'])
def process_natural_language():
    """API para procesar solicitud en lenguaje natural."""
    if not nlp_available or not processor:
        return jsonify({
            'success': False,
            'error': 'Procesador de lenguaje natural no disponible'
        }), 503
    
    # Obtener datos de la solicitud
    data = request.json
    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'Se requiere el campo "text" con la solicitud en lenguaje natural'
        }), 400
    
    # Procesar solicitud
    try:
        recipe = processor.process_request(data['text'])
        return jsonify({
            'success': True,
            'recipe': recipe
        })
    except Exception as e:
        logger.error(f"Error procesando lenguaje natural: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """API para obtener estadísticas del caché."""
    try:
        stats = cache.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """API para limpiar el caché."""
    try:
        cache.clear_cache()
        return jsonify({
            'success': True,
            'message': 'Caché limpiado correctamente'
        })
    except Exception as e:
        logger.error(f"Error limpiando caché: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Crear directorio para templates si no existe
    os.makedirs('templates', exist_ok=True)
    
    # Crear template básico si no existe
    template_path = os.path.join('templates', 'index.html')
    if not os.path.exists(template_path):
        with open(template_path, 'w') as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>TRIVO-AI - Sistema de Caché Inteligente</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: #f9f9f9;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #27ae60;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #219653;
        }
        .result {
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 20px;
            margin-top: 20px;
            white-space: pre-wrap;
        }
        .stats {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }
        .stat-card {
            flex: 1;
            min-width: 200px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin: 10px;
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
            color: #27ae60;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>TRIVO-AI - Sistema de Caché Inteligente</h1>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Recetas en caché</h3>
                <div class="stat-number">{{ stats.total_recipes }}</div>
            </div>
            {% for type, count in stats.recipe_types.items() %}
            <div class="stat-card">
                <h3>{{ type }}</h3>
                <div class="stat-number">{{ count }}</div>
            </div>
            {% endfor %}
        </div>
        
        <div class="card">
            <h2>Consulta de receta de cheesecake</h2>
            <div class="form-group">
                <label for="fruit">Fruta:</label>
                <input type="text" id="fruit" placeholder="Ej: frambuesa, fresa, arándano">
            </div>
            <div class="form-group">
                <label>Opciones:</label>
                <div>
                    <input type="checkbox" id="gluten_free"> <label for="gluten_free">Sin gluten</label>
                </div>
                <div>
                    <input type="checkbox" id="dairy_free"> <label for="dairy_free">Sin lácteos</label>
                </div>
            </div>
            <button onclick="getRecipe()">Obtener receta</button>
            <div id="recipe-result" class="result" style="display: none;"></div>
        </div>
        
        <div class="card">
            <h2>Consulta en lenguaje natural</h2>
            <div class="form-group">
                <label for="nlp-text">Describe lo que necesitas:</label>
                <textarea id="nlp-text" rows="4" placeholder="Ej: Quiero un cheesecake de fresa sin gluten"></textarea>
            </div>
            <button onclick="processNaturalLanguage()">Procesar</button>
            <div id="nlp-result" class="result" style="display: none;"></div>
        </div>
        
        <div class="card">
            <h2>Administración del caché</h2>
            <button onclick="clearCache()">Limpiar caché</button>
            <div id="cache-result" class="result" style="display: none;"></div>
        </div>
    </div>
    
    <script>
        function getRecipe() {
            const fruit = document.getElementById('fruit').value;
            const glutenFree = document.getElementById('gluten_free').checked;
            const dairyFree = document.getElementById('dairy_free').checked;
            
            const url = `/api/recipes/cheesecake?fruit=${encodeURIComponent(fruit)}&gluten_free=${glutenFree}&dairy_free=${dairyFree}`;
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    const resultElement = document.getElementById('recipe-result');
                    if (data.success) {
                        resultElement.textContent = JSON.stringify(data.recipe, null, 2);
                    } else {
                        resultElement.textContent = `Error: ${data.error}`;
                    }
                    resultElement.style.display = 'block';
                })
                .catch(error => {
                    document.getElementById('recipe-result').textContent = `Error: ${error.message}`;
                    document.getElementById('recipe-result').style.display = 'block';
                });
        }
        
        function processNaturalLanguage() {
            const text = document.getElementById('nlp-text').value;
            
            fetch('/api/natural-language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            })
                .then(response => response.json())
                .then(data => {
                    const resultElement = document.getElementById('nlp-result');
                    if (data.success) {
                        resultElement.textContent = JSON.stringify(data.recipe, null, 2);
                    } else {
                        resultElement.textContent = `Error: ${data.error}`;
                    }
                    resultElement.style.display = 'block';
                })
                .catch(error => {
                    document.getElementById('nlp-result').textContent = `Error: ${error.message}`;
                    document.getElementById('nlp-result').style.display = 'block';
                });
        }
        
        function clearCache() {
            fetch('/api/cache/clear', {
                method: 'POST'
            })
                .then(response => response.json())
                .then(data => {
                    const resultElement = document.getElementById('cache-result');
                    if (data.success) {
                        resultElement.textContent = data.message;
                        // Recargar la página para actualizar estadísticas
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        resultElement.textContent = `Error: ${data.error}`;
                    }
                    resultElement.style.display = 'block';
                })
                .catch(error => {
                    document.getElementById('cache-result').textContent = `Error: ${error.message}`;
                    document.getElementById('cache-result').style.display = 'block';
                });
        }
    </script>
</body>
</html>
            """)
    
    # Iniciar servidor
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True) 