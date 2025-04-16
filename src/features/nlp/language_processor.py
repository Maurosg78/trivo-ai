"""
Procesador de lenguaje natural avanzado para interpretar recetas a partir de descripciones.
Funciona con o sin dependencias externas (NLTK, sentence-transformers).
"""

import re
import os
import json
import logging
import random
from collections import defaultdict

# Configurar logging
logger = logging.getLogger('trivo.nlp')

# Intentar importar dependencias opcionales
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    nltk_available = True
    
    # Asegurar que los recursos necesarios estén disponibles
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
        
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
except ImportError:
    nltk_available = False
    logger.warning("NLTK no disponible. Usando tokenización básica.")

try:
    from sentence_transformers import SentenceTransformer, util
    transformers_available = True
except ImportError:
    transformers_available = False
    logger.warning("SentenceTransformers no disponible. Usando similitud basada en reglas.")

class LanguageProcessor:
    """
    Procesador de lenguaje natural avanzado para recetas.
    Combina enfoques basados en reglas y modelos de embeddings para una mejor comprensión.
    """
    
    def __init__(self, use_transformers=True):
        """
        Inicializa el procesador de lenguaje natural.
        
        Args:
            use_transformers: Si se deben usar modelos de embeddings más avanzados
        """
        # Verificar si podemos usar transformers
        self.use_transformers = use_transformers and transformers_available
        
        # Cargar modelo de embeddings si está habilitado
        if self.use_transformers:
            try:
                self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("Modelo de embeddings cargado correctamente.")
            except Exception as e:
                logger.warning(f"No se pudo cargar el modelo de embeddings: {e}")
                self.use_transformers = False
        
        # Stopwords en español (versión simplificada si NLTK no está disponible)
        if nltk_available:
            self.stopwords = set(stopwords.words('spanish'))
        else:
            # Lista básica de stopwords en español
            self.stopwords = set([
                'a', 'al', 'algo', 'algunas', 'algunos', 'ante', 'antes', 'como', 'con', 'contra',
                'cual', 'cuando', 'de', 'del', 'desde', 'donde', 'durante', 'e', 'el', 'ella',
                'ellas', 'ellos', 'en', 'entre', 'era', 'erais', 'eran', 'eras', 'eres', 'es',
                'esa', 'esas', 'ese', 'eso', 'esos', 'esta', 'estaba', 'estabais', 'estaban',
                'estabas', 'estad', 'estada', 'estadas', 'estado', 'estados', 'estamos', 'estando',
                'estar', 'estaremos', 'estará', 'estarán', 'estarás', 'estaré', 'estaréis',
                'estaría', 'estaríais', 'estaríamos', 'estarían', 'estarías', 'estas', 'este',
                'estemos', 'esto', 'estos', 'estoy', 'estuve', 'estuviera', 'estuvierais',
                'estuvieran', 'estuvieras', 'estuvieron', 'estuviese', 'estuvieseis', 'estuviesen',
                'estuvieses', 'estuvimos', 'estuviste', 'estuvisteis', 'estuviéramos',
                'estuviésemos', 'estuvo', 'está', 'estábamos', 'estáis', 'están', 'estás', 'esté',
                'estéis', 'estén', 'estés', 'fue', 'fuera', 'fuerais', 'fueran', 'fueras',
                'fueron', 'fuese', 'fueseis', 'fuesen', 'fueses', 'fui', 'fuimos', 'fuiste',
                'fuisteis', 'fuéramos', 'fuésemos', 'ha', 'habida', 'habidas', 'habido', 'habidos',
                'habiendo', 'habremos', 'habrá', 'habrán', 'habrás', 'habré', 'habréis', 'habría',
                'habríais', 'habríamos', 'habrían', 'habrías', 'hace', 'hacemos', 'hacen', 'hacer',
                'haces', 'hago', 'han', 'has', 'hasta', 'hay', 'haya', 'hayamos', 'hayan', 'hayas',
                'hayáis', 'he', 'hemos', 'hube', 'hubiera', 'hubierais', 'hubieran', 'hubieras',
                'hubieron', 'hubiese', 'hubieseis', 'hubiesen', 'hubieses', 'hubimos', 'hubiste',
                'hubisteis', 'hubiéramos', 'hubiésemos', 'hubo', 'la', 'las', 'le', 'les', 'lo',
                'los', 'me', 'mi', 'mis', 'mucho', 'muchos', 'muy', 'más', 'mí', 'mía', 'mías',
                'mío', 'míos', 'ni', 'no', 'nos', 'nosotras', 'nosotros', 'nuestra', 'nuestras',
                'nuestro', 'nuestros', 'o', 'os', 'otra', 'otras', 'otro', 'otros', 'para', 'pero',
                'poco', 'por', 'porque', 'que', 'quien', 'quienes', 'qué', 'se', 'sea', 'seamos',
                'sean', 'seas', 'seremos', 'será', 'serán', 'serás', 'seré', 'seréis', 'sería',
                'seríais', 'seríamos', 'serían', 'serías', 'seáis', 'si', 'sido', 'siendo', 'sin',
                'sobre', 'sois', 'somos', 'son', 'soy', 'su', 'sus', 'suya', 'suyas', 'suyo',
                'suyos', 'sí', 'también', 'tanto', 'te', 'tendremos', 'tendrá', 'tendrán',
                'tendrás', 'tendré', 'tendréis', 'tendría', 'tendríais', 'tendríamos', 'tendrían',
                'tendrías', 'tened', 'tenemos', 'tenga', 'tengamos', 'tengan', 'tengas', 'tengo',
                'tengáis', 'tenida', 'tenidas', 'tenido', 'tenidos', 'teniendo', 'tenéis', 'tenía',
                'teníais', 'teníamos', 'tenían', 'tenías', 'ti', 'tiene', 'tienen', 'tienes', 'todo',
                'todos', 'tu', 'tus', 'tuve', 'tuviera', 'tuvierais', 'tuvieran', 'tuvieras',
                'tuvieron', 'tuviese', 'tuvieseis', 'tuviesen', 'tuvieses', 'tuvimos', 'tuviste',
                'tuvisteis', 'tuviéramos', 'tuviésemos', 'tuvo', 'tuya', 'tuyas', 'tuyo', 'tuyos',
                'tú', 'un', 'una', 'uno', 'unos', 'vosotras', 'vosotros', 'vuestra', 'vuestras',
                'vuestro', 'vuestros', 'y', 'ya', 'yo', 'él', 'éramos'
            ])
        
        # Características ampliadas de masas
        self.keywords = {
            # Tipos de pizza
            "pizza_types": [
                "margarita", "napolitana", "pepperoni", "hawaiana", "vegana", "cuatro quesos", 
                "barbacoa", "marinera", "caprichosa", "siciliana", "española", "mexicana", 
                "carbonara", "fugazzeta", "fugazza", "calzone", "neoyorquina", "chicago", "detroit"
            ],
            
            # Tipos de masa
            "dough_types": {
                "pizza": [
                    "delgada", "gruesa", "crujiente", "suave", "integral", "artesanal", "tradicional", 
                    "nueva york", "estilo chicago", "madre", "fermentación natural", "hidratación alta",
                    "de poolish", "biga", "napolitana auténtica", "romana", "siciliana", "detroit"
                ],
                "pan": [
                    "baguette", "chapata", "hogaza", "de molde", "integral", "multicereales", "de centeno",
                    "campesino", "de masa madre", "brioche", "focaccia", "naan", "pita"
                ],
                "pastelería": [
                    "hojaldre", "quebrada", "sablée", "brisa", "choux", "masa para galletas", 
                    "croissant", "danesa", "strudel"
                ]
            },
            
            # Tamaños
            "sizes": ["personal", "mediana", "familiar", "industrial", "grande", "pequeña", "individual", "extra grande"],
            
            # Restricciones dietéticas
            "restrictions": [
                "sin gluten", "vegana", "keto", "baja en sodio", "sin lácteos", "sin huevo", "sin azúcar",
                "baja en carbohidratos", "baja en grasas", "sin aditivos", "sin conservantes", "ecológica",
                "sin transgénicos", "paleo", "diabética"
            ],
            
            # Colores
            "colors": ["blanca", "roja", "verde", "integral", "negra", "dorada", "violeta", "amarilla", "multicolor"],
            
            # Métodos de cocción
            "cooking_methods": [
                "horno de leña", "horno eléctrico", "sartén", "plancha", "parrilla", "horno de gas",
                "horno de piedra", "barbacoa", "microondas", "freidora de aire", "sous vide"
            ],
            
            # Texturas deseadas
            "textures": [
                "crujiente", "suave", "esponjosa", "elástica", "firme", "aireada", "densa", "ligera", 
                "masticable", "tierna", "flexible", "rígida", "alveolada"
            ],
            
            # Propiedades nutricionales
            "nutritional": [
                "alta en proteínas", "baja en carbohidratos", "alta en fibra", "baja en calorías",
                "nutritiva", "nutricional", "energética", "proteica", "saludable", "nutritivo", "saludable",
                "equilibrada", "balanceada", "vitaminas", "minerales", "antioxidantes"
            ]
        }
        
        # Base de conocimiento ampliada para ingredientes y propiedades
        self.ingredient_properties = {
            "harina_de_arroz": {
                "descripción": "Harina básica sin gluten, sabor neutro",
                "hidratación": 0.65,
                "elasticidad": 0.3,
                "textura": "suave",
                "sustitutos": ["harina de sorgo", "harina de mijo"],
                "proporción_base": 0.6
            },
            "harina_de_almendra": {
                "descripción": "Harina sin gluten rica en proteínas y grasas",
                "hidratación": 0.3,
                "elasticidad": 0.2,
                "textura": "densa",
                "sustitutos": ["harina de avellana", "harina de coco"],
                "proporción_base": 0.15
            },
            "almidón_de_maíz": {
                "descripción": "Almidón para mejorar textura en masas sin gluten",
                "hidratación": 0.7,
                "elasticidad": 0.1,
                "textura": "ligera",
                "sustitutos": ["fécula de patata", "tapioca"],
                "proporción_base": 0.25
            },
            "harina_de_trigo": {
                "descripción": "Harina tradicional con gluten para masas elásticas",
                "hidratación": 0.60,
                "elasticidad": 0.8,
                "textura": "elástica",
                "sustitutos": ["harina de espelta", "harina de fuerza"],
                "proporción_base": 1.0
            },
            "semillas_de_lino": {
                "descripción": "Semillas ricas en omega 3 y fibra",
                "hidratación": 0.0,
                "elasticidad": 0.0,
                "textura": "crujiente",
                "sustitutos": ["semillas de chía", "semillas de girasol"],
                "proporción_base": 0.05
            },
            "goma_xantana": {
                "descripción": "Espesante que proporciona elasticidad a masas sin gluten",
                "hidratación": 0,
                "elasticidad": 0.9,
                "textura": "elástica",
                "sustitutos": ["psyllium husk", "goma guar"],
                "proporción_base": 0.02
            }
        }
        
        # Proporciones e hidratación por tipo de producto
        self.product_specifications = {
            "pizza": {
                "napolitana": {"hidratación": 0.65, "levadura": 0.01, "sal": 0.025, "aceite": 0.03},
                "nueva york": {"hidratación": 0.60, "levadura": 0.008, "sal": 0.02, "aceite": 0.02},
                "chicago": {"hidratación": 0.55, "levadura": 0.015, "sal": 0.02, "aceite": 0.05},
                "default": {"hidratación": 0.62, "levadura": 0.01, "sal": 0.022, "aceite": 0.03}
            },
            "pan": {
                "baguette": {"hidratación": 0.72, "levadura": 0.005, "sal": 0.018, "aceite": 0},
                "chapata": {"hidratación": 0.8, "levadura": 0.003, "sal": 0.02, "aceite": 0.02},
                "default": {"hidratación": 0.7, "levadura": 0.01, "sal": 0.02, "aceite": 0.01}
            },
            "default": {"hidratación": 0.65, "levadura": 0.01, "sal": 0.02, "aceite": 0.02}
        }
        
        # Referencia para interpretar frases
        self.reference_sentences = {
            "tipo_receta": {
                "margarita": ["quiero una pizza margarita", "me gustaría preparar una margarita", "receta para pizza tipo margarita"],
                "napolitana": ["pizza napolitana auténtica", "masa estilo napolitano", "receta tradicional napolitana"],
                "chicago": ["masa estilo chicago", "deep dish pizza", "pizza estilo chicago"]
            },
            "restricciones": {
                "sin gluten": ["no puedo comer gluten", "soy celíaco", "masa libre de gluten", "sin gluten por favor"],
                "vegana": ["soy vegano", "sin productos animales", "vegano", "100% vegetal"],
                "keto": ["dieta cetogénica", "comida keto", "baja en carbohidratos", "cetogénica"]
            }
        }
    
    def _tokenize(self, text):
        """Tokeniza el texto usando NLTK si está disponible o split básico."""
        if nltk_available:
            return word_tokenize(text, language='spanish')
        else:
            # Tokenización simple con expresiones regulares
            # Eliminar puntuación y dividir por espacios
            return re.findall(r'\w+', text.lower())
    
    def _detect_properties(self, text, tokens):
        """
        Detecta propiedades de la receta a partir del texto y tokens.
        
        Args:
            text: Texto completo de la solicitud
            tokens: Lista de tokens (palabras) del texto
            
        Returns:
            Diccionario con propiedades detectadas
        """
        properties = {
            "tipo_receta": "básica",
            "tipo_masa": "tradicional",
            "restricciones": [],
            "color": "blanca",
            "escala": "pequeña",
            "textura_deseada": [],
            "optimizacion_nutricional": False
        }
        
        # Detectar tipo de receta (pizza específica)
        for tipo in self.keywords["pizza_types"]:
            if tipo in text or any(token == tipo for token in tokens):
                properties["tipo_receta"] = tipo
                break
        
        # Detectar textura deseada
        for textura in self.keywords["textures"]:
            if textura in text:
                properties["textura_deseada"].append(textura)
        
        # Detectar restricciones dietéticas
        for restriccion in self.keywords["restrictions"]:
            if restriccion in text:
                properties["restricciones"].append(restriccion)
        
        # Detectar color
        for color in self.keywords["colors"]:
            if color in text:
                properties["color"] = color
                break
        
        # Detectar escala/tamaño
        for size in self.keywords["sizes"]:
            if size in text:
                properties["escala"] = size
                break
        
        # Detectar optimización nutricional
        for term in self.keywords["nutritional"]:
            if term in text:
                properties["optimizacion_nutricional"] = True
                break
        
        return properties
    
    def _enhance_with_embeddings(self, text, properties):
        """
        Mejora la detección de propiedades usando embeddings si están disponibles.
        
        Args:
            text: Texto original de la solicitud
            properties: Diccionario de propiedades detectadas a mejorar
        """
        if not self.use_transformers:
            return
        
        # Generar embedding para el texto de entrada
        text_embedding = self.model.encode(text)
        
        # Comparar con referencias para mejorar la detección de intenciones
        for property_type, references in self.reference_sentences.items():
            best_score = 0
            best_match = None
            
            for value, sentences in references.items():
                for sentence in sentences:
                    ref_embedding = self.model.encode(sentence)
                    similarity = util.pytorch_cos_sim(text_embedding, ref_embedding).item()
                    
                    if similarity > best_score and similarity > 0.7:  # Umbral de similitud
                        best_score = similarity
                        best_match = value
            
            # Actualizar propiedad si encontramos mejor coincidencia
            if best_match and best_score > 0.7:
                if property_type == "restricciones":
                    if best_match not in properties[property_type]:
                        properties[property_type].append(best_match)
                else:
                    properties[property_type] = best_match
    
    def _infer_missing_properties(self, properties):
        """
        Infiere propiedades faltantes basadas en el conocimiento del dominio.
        
        Args:
            properties: Diccionario de propiedades detectadas a completar
        """
        # Si es sin gluten pero no hay textura deseada, añadir elástica
        if "sin gluten" in properties["restricciones"] and not properties["textura_deseada"]:
            properties["textura_deseada"].append("elástica")
        
        # Si es margarita o napolitana y no hay color, sugerir blanca
        if properties["tipo_receta"] in ["margarita", "napolitana"] and properties["color"] == "blanca":
            properties["color"] = "blanca"
        
        # Si es familiar y no hay escala, establecer familiar
        if "familiar" in properties["textura_deseada"] and properties["escala"] == "pequeña":
            properties["escala"] = "familiar"
    
    def _generate_recipe(self, properties):
        """
        Genera una receta basada en las propiedades detectadas.
        
        Args:
            properties: Diccionario con propiedades detectadas
            
        Returns:
            Diccionario con la receta generada
        """
        ingredients = []
        
        # Nombre de la receta
        recipe_name = f"Masa de Pizza {properties['tipo_receta'].capitalize()} {properties['color'].capitalize()}"
        
        # Descripción
        description = f"Masa de pizza {properties['color']} para {properties['escala']}"
        if properties["restricciones"]:
            description += f", {', '.join(properties['restricciones'])}"
        if properties["optimizacion_nutricional"]:
            description += ", nutricionalmente optimizada"
        
        # Base de harina
        if "sin gluten" in properties["restricciones"]:
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
        
        # Determinar hidratación según tipo y escala
        hydration = 0.65  # Por defecto
        if properties["tipo_receta"] in self.product_specifications["pizza"]:
            hydration = self.product_specifications["pizza"][properties["tipo_receta"]]["hidratación"]
        elif "crujiente" in properties["textura_deseada"]:
            hydration = 0.55
        elif "suave" in properties["textura_deseada"] or "esponjosa" in properties["textura_deseada"]:
            hydration = 0.70
        
        # Ajustar cantidad de harina según escala
        flour_qty = 0
        for ing in ingredients:
            if "harina" in ing["name"].lower() or "almidón" in ing["name"].lower():
                flour_qty += ing["quantity"]
        
        # Calcular agua basada en hidratación
        water_qty = flour_qty * hydration
        
        # Agua
        ingredients.append({
            "name": "Agua",
            "quantity": round(water_qty, 1),
            "unit": "ml"
        })
        
        # Levadura
        yeast_qty = flour_qty * 0.01  # 1% de la harina por defecto
        ingredients.append({
            "name": "Levadura seca",
            "quantity": round(yeast_qty, 1),
            "unit": "g"
        })
        
        # Sal (menos si es baja en sodio)
        salt_qty = flour_qty * 0.02  # 2% de la harina por defecto
        if "baja en sodio" in properties["restricciones"]:
            salt_qty = flour_qty * 0.01  # 1% si es baja en sodio
        ingredients.append({
            "name": "Sal",
            "quantity": round(salt_qty, 1),
            "unit": "g"
        })
        
        # Aceite
        oil_qty = flour_qty * 0.03  # 3% de la harina por defecto
        ingredients.append({
            "name": "Aceite de oliva",
            "quantity": round(oil_qty, 1),
            "unit": "ml"
        })
        
        # Ingredientes para color
        if properties["color"] == "roja":
            ingredients.append({
                "name": "Remolacha en polvo",
                "quantity": round(flour_qty * 0.04, 1),
                "unit": "g"
            })
        elif properties["color"] == "verde":
            ingredients.append({
                "name": "Espinaca en polvo",
                "quantity": round(flour_qty * 0.05, 1),
                "unit": "g"
            })
        elif properties["color"] == "negra":
            ingredients.append({
                "name": "Tinta de calamar",
                "quantity": round(flour_qty * 0.03, 1),
                "unit": "g"
            })
        elif properties["color"] == "integral":
            # Reemplazar harina blanca por integral
            for i, ingredient in enumerate(ingredients):
                if ingredient["name"] == "Harina de trigo":
                    ingredients[i] = {
                        "name": "Harina integral",
                        "quantity": ingredient["quantity"],
                        "unit": "g"
                    }
        
        # Ingredientes adicionales para optimización nutricional
        if properties["optimizacion_nutricional"]:
            ingredients.append({
                "name": "Semillas de lino molidas",
                "quantity": round(flour_qty * 0.03, 1),
                "unit": "g"
            })
            ingredients.append({
                "name": "Semillas de chía",
                "quantity": round(flour_qty * 0.03, 1),
                "unit": "g"
            })
        
        # Escalar cantidades según tamaño
        scale_factor = 1.0
        if properties["escala"] == "familiar":
            scale_factor = 2.0
        elif properties["escala"] == "industrial":
            scale_factor = 4.0
        elif properties["escala"] == "grande":
            scale_factor = 1.5
        
        if scale_factor != 1.0:
            for i in range(len(ingredients)):
                ingredients[i]["quantity"] = round(ingredients[i]["quantity"] * scale_factor, 1)
        
        return {
            "name": recipe_name,
            "description": description,
            "ingredients": ingredients,
            "properties": properties
        }
    
    def process_request(self, text):
        """
        Procesa una solicitud en lenguaje natural con análisis avanzado.
        
        Args:
            text: Texto de la solicitud
            
        Returns:
            Diccionario con las propiedades detectadas y la receta generada
        """
        logger.info(f"Procesando solicitud: {text}")
        
        # Normalizar texto
        text = text.lower()
        
        # Tokenizar texto
        tokens = self._tokenize(text)
        tokens = [t for t in tokens if t not in self.stopwords]
        
        # Detector avanzado de propiedades
        properties = self._detect_properties(text, tokens)
        
        # Realizar análisis mediante embeddings si está disponible
        if self.use_transformers:
            self._enhance_with_embeddings(text, properties)
        
        # Inferir propiedades faltantes basadas en conocimiento del dominio
        self._infer_missing_properties(properties)
        
        # Generar una receta adaptada a las propiedades
        recipe = self._generate_recipe(properties)
        
        # Registrar resultado
        logger.info(f"Propiedades detectadas: {properties}")
        
        return recipe 