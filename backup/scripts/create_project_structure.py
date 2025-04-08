#!/usr/bin/env python3
"""
Script para inicializar la estructura del proyecto TRIVO-AI conforme al roadmap.
Este script crea directorios y archivos base requeridos para el MVP.
"""

import os
import json
import shutil
from pathlib import Path

def create_directory_structure():
    """Crea la estructura de directorios para el proyecto."""
    directories = [
        "app/static/css",
        "app/static/js",
        "app/static/img",
        "app/templates",
        "docs",
        "scripts/validation_system",
        "src/features/optimizer",
        "src/features/validator",
        "src/features/nlp",
        "src/utils",
        "data/recipes",
        "data/ingredients",
        "tests/unit",
        "tests/integration"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Creado directorio: {directory}")

def create_base_files():
    """Crea archivos base para el proyecto."""
    files = {
        "requirements.txt": """
flask==2.2.3
pandas==1.5.3
numpy==1.24.2
scikit-learn==1.2.2
matplotlib==3.7.1
pytest==7.3.1
python-dotenv==1.0.0
requests==2.28.2
PyGithub==1.59.0
""",
        ".env.example": """
# API Keys
USDA_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here

# Configuración
DEBUG=True
LOG_LEVEL=INFO
""",
        ".gitignore": """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Entorno virtual
venv/
ENV/

# Archivos sensibles
.env

# Logs
logs/
*.log

# Archivos temporales
tmp/
temp/

# Archivos de sistema
.DS_Store
Thumbs.db
""",
        "src/features/optimizer/optimizer.py": """
\"\"\"
Módulo de optimización de recetas basado en algoritmos genéticos.
\"\"\"

import random
import numpy as np

class RecipeOptimizer:
    \"\"\"Optimizador de recetas basado en algoritmos genéticos.\"\"\"
    
    def __init__(self, ingredients, constraints, population_size=100, generations=50):
        \"\"\"
        Inicializa el optimizador.
        
        Args:
            ingredients: Diccionario de ingredientes disponibles con sus propiedades
            constraints: Restricciones para la optimización
            population_size: Tamaño de la población
            generations: Número de generaciones
        \"\"\"
        self.ingredients = ingredients
        self.constraints = constraints
        self.population_size = population_size
        self.generations = generations
    
    def optimize(self):
        \"\"\"
        Ejecuta el algoritmo genético para optimizar la receta.
        
        Returns:
            La receta optimizada como un diccionario
        \"\"\"
        # Implementación simplificada para el MVP
        print("Optimizando receta...")
        # TODO: Implementar algoritmo genético completo
        
        # Devolver una receta básica como ejemplo
        return {
            "name": "Receta optimizada",
            "ingredients": {
                "harina": 1000,  # g
                "agua": 650,     # ml
                "sal": 20,       # g
                "levadura": 10   # g
            },
            "cost": 2.5,         # Costo por kg
            "hydration": 65,     # Porcentaje
            "estimated_quality": 85  # Índice 0-100
        }
""",
        "src/features/validator/validator.py": """
\"\"\"
Sistema de validación de recetas para diferentes escalas de producción.
\"\"\"

class RecipeValidator:
    \"\"\"Validador de recetas para diferentes escalas de producción.\"\"\"
    
    def __init__(self, rules=None, production_scale="small_business"):
        \"\"\"
        Inicializa el validador de recetas.
        
        Args:
            rules: Lista de reglas de validación
            production_scale: Escala de producción (small_business, restaurant, industrial)
        \"\"\"
        self.rules = rules or []
        self.production_scale = production_scale
        self.load_default_rules()
    
    def load_default_rules(self):
        \"\"\"Carga las reglas de validación predeterminadas.\"\"\"
        # Reglas críticas
        self.rules.extend([
            {"name": "hydration_ratio", "severity": "critical", "function": self._check_hydration},
            {"name": "salt_ratio", "severity": "critical", "function": self._check_salt},
            {"name": "yeast_ratio", "severity": "critical", "function": self._check_yeast},
            {"name": "essential_ingredients", "severity": "critical", "function": self._check_essentials},
            {"name": "scale_limits", "severity": "critical", "function": self._check_scale}
        ])
        
        # Reglas de nivel medio
        self.rules.extend([
            {"name": "fermentation_params", "severity": "medium", "function": self._check_fermentation},
            {"name": "cost_efficiency", "severity": "medium", "function": self._check_cost},
            {"name": "quality_factors", "severity": "medium", "function": self._check_quality}
        ])
    
    def validate(self, recipe):
        \"\"\"
        Valida una receta según las reglas configuradas.
        
        Args:
            recipe: Diccionario con la receta a validar
            
        Returns:
            Diccionario con resultados de validación
        \"\"\"
        results = {
            "valid": True,
            "scale": self.production_scale,
            "issues": [],
            "warnings": [],
            "suggestions": []
        }
        
        for rule in self.rules:
            issue = rule["function"](recipe)
            if issue:
                if rule["severity"] == "critical":
                    results["valid"] = False
                    results["issues"].append(issue)
                elif rule["severity"] == "medium":
                    results["warnings"].append(issue)
                else:
                    results["suggestions"].append(issue)
        
        return results
    
    # Implementaciones simplificadas de las funciones de validación
    def _check_hydration(self, recipe):
        # TODO: Implementar validación real
        return None
    
    def _check_salt(self, recipe):
        # TODO: Implementar validación real
        return None
    
    def _check_yeast(self, recipe):
        # TODO: Implementar validación real
        return None
    
    def _check_essentials(self, recipe):
        # TODO: Implementar validación real
        return None
    
    def _check_scale(self, recipe):
        # TODO: Implementar validación real
        return None
    
    def _check_fermentation(self, recipe):
        # TODO: Implementar validación real
        return None
    
    def _check_cost(self, recipe):
        # TODO: Implementar validación real
        return None
    
    def _check_quality(self, recipe):
        # TODO: Implementar validación real
        return None
""",
        "src/features/nlp/language_processor.py": """
\"\"\"
Procesador de lenguaje natural para interpretar recetas a partir de descripciones.
\"\"\"

class LanguageProcessor:
    \"\"\"Procesador de lenguaje natural para recetas.\"\"\"
    
    def __init__(self):
        \"\"\"Inicializa el procesador de lenguaje natural.\"\"\"
        # En el MVP, usamos una implementación simplificada
        self.keywords = {
            "pizza_types": ["margarita", "napolitana", "pepperoni", "hawaiana", "vegana"],
            "dough_types": ["delgada", "gruesa", "crujiente", "suave", "integral"],
            "sizes": ["personal", "mediana", "familiar", "industrial"],
            "restrictions": ["sin gluten", "vegana", "keto", "baja en sodio"],
            "colors": ["blanca", "roja", "verde", "integral"]
        }
    
    def process_request(self, text):
        \"\"\"
        Procesa una solicitud en lenguaje natural.
        
        Args:
            text: Texto de la solicitud
            
        Returns:
            Diccionario con las propiedades detectadas y la receta generada
        \"\"\"
        # Versión simplificada para el MVP
        text = text.lower()
        
        # Detectar propiedades
        properties = {
            "pizza_type": next((t for t in self.keywords["pizza_types"] if t in text), None),
            "dough_type": next((t for t in self.keywords["dough_types"] if t in text), None),
            "size": next((s for s in self.keywords["sizes"] if s in text), "mediana"),
            "restrictions": [r for r in self.keywords["restrictions"] if r in text],
            "color": next((c for c in self.keywords["colors"] if c in text), None)
        }
        
        # Generar una receta básica basada en las propiedades
        recipe = self._generate_recipe(properties)
        
        return {
            "properties": properties,
            "recipe": recipe,
            "status": "success"
        }
    
    def _generate_recipe(self, properties):
        \"\"\"
        Genera una receta basada en las propiedades detectadas.
        
        Args:
            properties: Diccionario con propiedades detectadas
            
        Returns:
            Diccionario con la receta generada
        \"\"\"
        # Implementación simplificada para el MVP
        recipe = {
            "name": f"Masa para pizza {properties['pizza_type'] or 'básica'}",
            "ingredients": {
                "harina": 1000  # g
            },
            "instructions": []
        }
        
        # Ajustar ingredientes según tipo
        if "sin gluten" in properties["restrictions"]:
            recipe["ingredients"] = {
                "harina de arroz": 700,  # g
                "almidón de maíz": 300,  # g
                "goma xantana": 20       # g
            }
        
        # Ajustar hidratación según tipo de masa
        if properties["dough_type"] == "delgada":
            recipe["ingredients"]["agua"] = 550  # ml
        elif properties["dough_type"] == "gruesa":
            recipe["ingredients"]["agua"] = 700  # ml
        else:
            recipe["ingredients"]["agua"] = 650  # ml
        
        # Agregar ingredientes básicos
        recipe["ingredients"]["sal"] = 20        # g
        recipe["ingredients"]["levadura"] = 10   # g
        recipe["ingredients"]["aceite de oliva"] = 30  # ml
        
        # Generar instrucciones básicas
        recipe["instructions"] = [
            "Mezclar la harina y la sal en un recipiente grande.",
            "Disolver la levadura en agua tibia.",
            "Incorporar el agua con levadura a la mezcla de harina.",
            "Amasar durante 10 minutos hasta obtener una masa elástica.",
            "Dejar reposar tapado por 1 hora o hasta que duplique su volumen.",
            "Dividir y formar según el uso deseado."
        ]
        
        return recipe
""",
        "app/app.py": """
\"\"\"
Aplicación web para TRIVO-AI.
\"\"\"

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import sys

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

@app.route('/')
def index():
    \"\"\"Página de inicio.\"\"\"
    return render_template('index.html')

@app.route('/optimize', methods=['GET', 'POST'])
def optimize():
    \"\"\"Página de optimización de recetas.\"\"\"
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
                validation_result=validation_result
            )
            
        except Exception as e:
            return render_template('optimize.html', error=str(e))
    
    return render_template('optimize.html')

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    \"\"\"Página de validación de recetas.\"\"\"
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
                    
                    return render_template('validate.html', recipe=recipe, validation_result=validation_result)
            
            return render_template('validate.html', error="Archivo no válido o no seleccionado")
            
        except Exception as e:
            return render_template('validate.html', error=str(e))
    
    return render_template('validate.html')

@app.route('/natural-language', methods=['POST'])
def natural_language():
    \"\"\"Procesa solicitudes en lenguaje natural.\"\"\"
    try:
        text = request.form.get('text', '')
        if not text:
            return redirect(url_for('index'))
        
        processor = LanguageProcessor()
        result = processor.process_request(text)
        
        # Generar instrucciones basadas en la receta y propiedades
        instructions = generate_instructions(result['recipe'], result['properties'])
        result['recipe']['instructions'] = instructions
        
        return render_template(
            'optimize.html',
            nlp_request=text,
            nlp_result=result,
            optimized_recipe=result['recipe']
        )
        
    except Exception as e:
        return render_template('index.html', error=str(e))

def generate_instructions(recipe, properties):
    \"\"\"Genera instrucciones basadas en la receta y propiedades.\"\"\"
    # Versión básica para el MVP
    instructions = [
        "Mezclar todos los ingredientes secos en un recipiente grande.",
        "Agregar los ingredientes líquidos gradualmente mientras se mezcla.",
        "Amasar durante 10-15 minutos hasta obtener una masa elástica.",
        "Dejar reposar la masa cubierta por 1-2 horas en un lugar cálido.",
        "Dividir y dar forma según necesidades."
    ]
    
    # Personalizar según restricciones
    if properties.get('restrictions'):
        if "sin gluten" in properties['restrictions']:
            instructions.insert(2, "Para masas sin gluten, no amasar en exceso para evitar que se vuelva pegajosa.")
    
    # Personalizar según tipo de masa
    if properties.get('dough_type') == "delgada":
        instructions.append("Estirar la masa muy fina para lograr una base crujiente.")
    elif properties.get('dough_type') == "gruesa":
        instructions.append("Estirar la masa con un grosor de aproximadamente 1 cm para una base esponjosa.")
    
    return instructions

@app.route('/about')
def about():
    \"\"\"Página acerca de.\"\"\"
    return render_template('about.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
"""
    }
    
    for file_path, content in files.items():
        with open(file_path, 'w') as f:
            f.write(content.strip())
        print(f"✓ Creado archivo: {file_path}")

def create_sample_data():
    """Crea datos de ejemplo para el proyecto."""
    sample_data = {
        "data/ingredients/basic.json": {
            "harina": {
                "price": 0.8,  # € por kg
                "properties": {
                    "protein": 10.5,  # %
                    "fiber": 2.7,     # %
                    "category": "flour"
                }
            },
            "agua": {
                "price": 0.001,  # € por litro
                "properties": {
                    "category": "liquid"
                }
            },
            "sal": {
                "price": 0.5,  # € por kg
                "properties": {
                    "category": "salt"
                }
            },
            "levadura fresca": {
                "price": 4.0,  # € por kg
                "properties": {
                    "category": "leavening"
                }
            },
            "levadura seca": {
                "price": 12.0,  # € por kg
                "properties": {
                    "category": "leavening",
                    "conversion_factor": 0.33  # 1/3 de la cantidad de levadura fresca
                }
            },
            "aceite de oliva": {
                "price": 5.0,  # € por litro
                "properties": {
                    "category": "fat"
                }
            },
            "harina de fuerza": {
                "price": 1.2,  # € por kg
                "properties": {
                    "protein": 13.5,  # %
                    "fiber": 2.5,     # %
                    "category": "flour"
                }
            },
            "harina integral": {
                "price": 1.5,  # € por kg
                "properties": {
                    "protein": 12.0,  # %
                    "fiber": 10.5,    # %
                    "category": "flour"
                }
            },
            "harina de arroz": {
                "price": 2.5,  # € por kg
                "properties": {
                    "protein": 7.0,   # %
                    "fiber": 1.4,     # %
                    "category": "flour",
                    "gluten_free": True
                }
            },
            "almidón de maíz": {
                "price": 2.0,  # € por kg
                "properties": {
                    "protein": 0.3,   # %
                    "fiber": 0.1,     # %
                    "category": "flour",
                    "gluten_free": True
                }
            },
            "goma xantana": {
                "price": 25.0,  # € por kg
                "properties": {
                    "category": "additive",
                    "gluten_free": True
                }
            }
        },
        "data/recipes/napolitana_basica.json": {
            "name": "Masa de Pizza Napolitana Básica",
            "ingredients": {
                "harina de fuerza": 1000,  # g
                "agua": 650,               # ml
                "sal": 25,                 # g
                "levadura fresca": 20      # g
            },
            "process": {
                "fermentation_time": 24,   # horas
                "fermentation_temp": 4,    # °C (refrigerador)
                "proofing_time": 2         # horas
            },
            "metadata": {
                "author": "TRIVO-AI",
                "created": "2024-03-21",
                "version": 1.0,
                "type": "pizza",
                "category": "napolitana"
            }
        }
    }
    
    for file_path, data in sample_data.items():
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Creado archivo de datos: {file_path}")

def create_basic_html_templates():
    """Crea plantillas HTML básicas para la aplicación web."""
    templates = {
        "app/templates/base.html": """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}TRIVO-AI - Formulación Inteligente{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">TRIVO-AI</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/' %}active{% endif %}" href="/">Inicio</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/optimize' %}active{% endif %}" href="/optimize">Crear Receta</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/validate' %}active{% endif %}" href="/validate">Validar Receta</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/about' %}active{% endif %}" href="/about">Acerca de</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container py-4">
        {% if error %}
        <div class="alert alert-danger">{{ error }}</div>
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>

    <footer class="mt-5 py-4 text-center text-muted bg-light">
        <div class="container">
            <p>TRIVO-AI &copy; 2024 | <a href="https://github.com/Maurosg78/trivo-ai" target="_blank" rel="noopener">GitHub</a></p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>""",
        "app/templates/index.html": """{% extends 'base.html' %}

{% block title %}TRIVO-AI - Formulación Inteligente de Masas{% endblock %}

{% block content %}
<div class="container">
    <div class="row mb-5 align-items-center">
        <div class="col-lg-7">
            <h1 class="display-4 fw-bold mb-4">TRIVO-AI</h1>
            <h2 class="mb-4">Formulación Inteligente para PYMEs Alimentarias</h2>
            <p class="lead mb-4">
                Optimiza tus recetas de masas utilizando inteligencia artificial y algoritmos genéticos. 
                Reduce costos, mejora la calidad y valida tus fórmulas para diferentes escalas de producción.
            </p>
            
            <form action="/natural-language" method="post" class="my-4 natural-language-input">
                <div class="mb-3">
                    <label for="nlText" class="form-label">Describe lo que necesitas:</label>
                    <textarea class="form-control" id="nlText" name="text" rows="3" placeholder="Ej: Quiero una masa de pizza familiar, de color rojo, sin gluten, nutricionalmente optimizada para niños"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Crear con IA</button>
            </form>
            
            <div class="mt-4">
                <a href="/optimize" class="btn btn-outline-primary me-2">Crear Receta</a>
                <a href="/validate" class="btn btn-outline-primary">Validar Receta</a>
            </div>
        </div>
        <div class="col-lg-5 mt-4 mt-lg-0">
            <div class="card shadow">
                <div class="card-body">
                    <h3 class="card-title">¿Por qué TRIVO-AI?</h3>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item d-flex">
                            <div class="feature-icon me-3">
                                <span class="badge bg-primary rounded-circle">1</span>
                            </div>
                            <div>
                                <h5>Algoritmos Genéticos</h5>
                                <p class="text-muted">Optimización avanzada para encontrar la mejor combinación de ingredientes</p>
                            </div>
                        </li>
                        <li class="list-group-item d-flex">
                            <div class="feature-icon me-3">
                                <span class="badge bg-primary rounded-circle">2</span>
                            </div>
                            <div>
                                <h5>Masas Plant-Based</h5>
                                <p class="text-muted">Soporte para formulaciones sin gluten, veganas y alternativas</p>
                            </div>
                        </li>
                        <li class="list-group-item d-flex">
                            <div class="feature-icon me-3">
                                <span class="badge bg-primary rounded-circle">3</span>
                            </div>
                            <div>
                                <h5>Validación Crítica</h5>
                                <p class="text-muted">Sistema de validación para garantizar la viabilidad de tus fórmulas</p>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-5">
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <h3 class="card-title">Optimización</h3>
                    <p class="card-text">Nuestro algoritmo genético optimiza tus recetas para reducir costos manteniendo la calidad.</p>
                    <a href="/optimize" class="btn btn-primary mt-3">Optimizar Receta</a>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <h3 class="card-title">Validación</h3>
                    <p class="card-text">Valida tus recetas para diferentes escalas de producción y garantiza su viabilidad.</p>
                    <a href="/validate" class="btn btn-primary mt-3">Validar Receta</a>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <h3 class="card-title">Lenguaje Natural</h3>
                    <p class="card-text">Describe lo que necesitas y nuestro sistema interpreta y genera la receta ideal.</p>
                    <a href="#" class="btn btn-primary mt-3" onclick="document.getElementById('nlText').focus(); return false;">Probar Ahora</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",
        "app/static/css/styles.css": """/* TRIVO-AI styles */

:root {
    --primary: #27ae60;
    --secondary: #e67e22;
    --dark: #212529;
    --light: #f8f9fa;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f9f9f9;
    color: #333;
}

/* Navbar */
.navbar {
    background-color: var(--primary);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
    font-weight: 700;
    letter-spacing: 1px;
}

/* Buttons */
.btn-primary {
    background-color: var(--primary);
    border-color: var(--primary);
}

.btn-primary:hover, .btn-primary:focus {
    background-color: #219653;
    border-color: #219653;
}

.btn-outline-primary {
    color: var(--primary);
    border-color: var(--primary);
}

.btn-outline-primary:hover, .btn-outline-primary:focus {
    background-color: var(--primary);
    border-color: var(--primary);
}

/* Cards */
.card {
    border-radius: 10px;
    border: none;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

/* Form elements */
.form-control:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 0.25rem rgba(39, 174, 96, 0.25);
}

/* Feature icons */
.feature-icon .badge {
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--primary);
}

/* Recipe display */
.recipe-container {
    background-color: #fff;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.ingredient-list {
    list-style-type: none;
    padding-left: 0;
}

.ingredient-list li {
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
}

/* Validation results */
.validation-badge {
    padding: 8px 12px;
    font-weight: 500;
    border-radius: 20px;
}

.validation-valid {
    background-color: #d4edda;
    color: #155724;
}

.validation-invalid {
    background-color: #f8d7da;
    color: #721c24;
}

/* Natural language input */
.natural-language-input {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #e9ecef;
}

.natural-language-input .form-control:focus {
    border-color: var(--secondary);
    box-shadow: 0 0 0 0.25rem rgba(230, 126, 34, 0.25);
}

.natural-language-input .btn-primary {
    background-color: var(--secondary);
    border-color: var(--secondary);
}

.natural-language-input .btn-primary:hover,
.natural-language-input .btn-primary:focus {
    background-color: #d35400;
    border-color: #d35400;
}

/* Footer */
footer {
    margin-top: 2rem;
}

footer a {
    color: var(--primary);
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}"""
    }
    
    for file_path, content in templates.items():
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✓ Creada plantilla: {file_path}")

def create_project_structure():
    """Crea la estructura completa del proyecto."""
    print("Inicializando estructura del proyecto TRIVO-AI...")
    
    # Crear directorios
    create_directory_structure()
    
    # Crear archivos base
    create_base_files()
    
    # Crear datos de ejemplo
    create_sample_data()
    
    # Crear plantillas HTML
    create_basic_html_templates()
    
    print("\nEstructura del proyecto inicializada correctamente.")
    print("\nPróximos pasos:")
    print("1. Crear un entorno virtual: python -m venv venv")
    print("2. Activar el entorno: source venv/bin/activate (Linux/Mac) o venv\\Scripts\\activate (Windows)")
    print("3. Instalar dependencias: pip install -r requirements.txt")
    print("4. Ejecutar la aplicación: python -m app.app")
    print("5. Acceder a la aplicación en http://localhost:8000")

if __name__ == "__main__":
    create_project_structure() 