"""
Cliente para la API de Spoonacular con mecanismo de caché para optimizar el uso.
"""

import os
import json
import time
import logging
import requests
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configurar logger
logger = logging.getLogger(__name__)

class SpoonacularClient:
    """Cliente para la API de Spoonacular con caché de resultados."""
    
    def __init__(self, api_key: Optional[str] = None, recipe_cache = None):
        """
        Inicializa el cliente de Spoonacular API.
        
        Args:
            api_key: Clave de API de Spoonacular (si es None, se busca en variables de entorno)
            recipe_cache: Instancia opcional de caché de recetas
        """
        self.api_key = api_key or os.environ.get('SPOONACULAR_API_KEY', '')
        self.cache = recipe_cache
        if not self.api_key:
            logger.warning("No se ha proporcionado API key para Spoonacular")
        
        # Configurar caché
        self.recipe_cache = recipe_cache
        
        # Directorio para guardar caché de respuestas
        self.cache_dir = Path(__file__).parent.parent.parent / 'data' / 'cache' / 'spoonacular'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de la API
        self.base_url = "https://api.spoonacular.com"
        
        # Límites para versión gratuita
        self.daily_points_limit = 150
        self.used_points = 0
        self.reset_day = time.strftime("%Y-%m-%d")
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """
        Genera una clave única para la caché basada en el endpoint y parámetros.
        
        Args:
            endpoint: Endpoint de la API
            params: Parámetros de la consulta
            
        Returns:
            Clave para la caché
        """
        # Ordenar parámetros para consistencia
        param_str = json.dumps(params, sort_keys=True)
        
        # Crear hash para evitar nombres de archivo inválidos
        hash_obj = hashlib.md5(f"{endpoint}:{param_str}".encode())
        return hash_obj.hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Intenta obtener datos desde la caché.
        
        Args:
            cache_key: Clave para la caché
            
        Returns:
            Datos en caché o None si no existen
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Datos recuperados de caché: {cache_key}")
                    return data
            except Exception as e:
                logger.error(f"Error leyendo cache: {str(e)}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Guarda datos en la caché.
        
        Args:
            cache_key: Clave para la caché
            data: Datos a guardar
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Datos guardados en caché: {cache_key}")
        except Exception as e:
            logger.error(f"Error guardando en caché: {str(e)}")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Realiza una solicitud a la API con gestión de caché.
        
        Args:
            endpoint: Endpoint de la API
            params: Parámetros de la consulta
            
        Returns:
            Datos de respuesta
        """
        # Reiniciar contador si es un nuevo día
        current_day = time.strftime("%Y-%m-%d")
        if current_day != self.reset_day:
            self.used_points = 0
            self.reset_day = current_day
        
        # Inicializar parámetros si es None
        if params is None:
            params = {}
        
        # Añadir la API key
        params['apiKey'] = self.api_key
        
        # Generar clave de caché
        cache_key = self._get_cache_key(endpoint, params)
        
        # Intentar obtener de caché primero
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Si no está en caché, hacer la solicitud a la API
        url = f"{self.base_url}/{endpoint}"
        logger.info(f"Haciendo solicitud a Spoonacular: {endpoint}")
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Actualizar contador de puntos
            if 'X-API-Quota-Used' in response.headers:
                points_used = float(response.headers['X-API-Quota-Used'])
                self.used_points += points_used
                logger.info(f"Puntos usados: {points_used} (Total hoy: {self.used_points})")
                
                if self.used_points > self.daily_points_limit:
                    logger.warning(f"Límite diario superado: {self.used_points}/{self.daily_points_limit}")
            
            data = response.json()
            
            # Guardar en caché
            self._save_to_cache(cache_key, data)
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en solicitud a Spoonacular: {str(e)}")
            return {"error": str(e)}
    
    def search_recipes(self, query: str, cuisine: Optional[str] = None, diet: Optional[str] = None, intolerances: Optional[str] = None, number: int = 5) -> List[Dict[str, Any]]:
        """
        Busca recetas en Spoonacular.
        
        Args:
            query: Términos de búsqueda
            cuisine: Tipo de cocina (italian, mexican, etc.)
            diet: Tipo de dieta (vegetarian, vegan, gluten free, etc.)
            intolerances: Intolerancias (dairy, gluten, etc.)
            number: Número máximo de resultados
            
        Returns:
            Lista de recetas
        """
        params = {
            'query': query,
            'number': number,
            'addRecipeInformation': 'true',
            'fillIngredients': 'true'
        }
        
        if cuisine:
            params['cuisine'] = cuisine
        
        if diet:
            params['diet'] = diet
        
        if intolerances:
            params['intolerances'] = intolerances
        
        results = self._make_request('recipes/complexSearch', params)
        return results.get('results', [])
    
    def get_recipe_by_id(self, recipe_id: int) -> Dict[str, Any]:
        """
        Obtiene información detallada de una receta por su ID.
        
        Args:
            recipe_id: ID de la receta en Spoonacular
            
        Returns:
            Datos de la receta
        """
        params = {
            'includeNutrition': 'true'
        }
        
        return self._make_request(f'recipes/{recipe_id}/information', params)
    
    def convert_spoonacular_to_trivo(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convierte una receta de Spoonacular al formato de TRIVO-AI.
        
        Args:
            recipe: Receta en formato Spoonacular
            
        Returns:
            Receta en formato TRIVO-AI
        """
        # Extraer información básica
        recipe_name = recipe.get('title', 'Receta desconocida')
        is_gluten_free = recipe.get('glutenFree', False)
        is_dairy_free = recipe.get('dairyFree', False)
        is_vegetarian = recipe.get('vegetarian', False)
        is_vegan = recipe.get('vegan', False)
        
        # Detectar tipo de receta
        dough_type = "otro"
        if 'pizza' in recipe_name.lower():
            dough_type = "pizza"
        elif 'bread' in recipe_name.lower() or 'pan' in recipe_name.lower():
            dough_type = "pan"
        elif 'cookie' in recipe_name.lower() or 'galleta' in recipe_name.lower():
            dough_type = "galletas"
        elif 'cheesecake' in recipe_name.lower() or 'tarta de queso' in recipe_name.lower():
            dough_type = "galletas"  # Base de galletas para cheesecake
        
        # Convertir ingredientes
        ingredients = {}
        instructions = []
        
        if 'extendedIngredients' in recipe:
            for ingredient in recipe['extendedIngredients']:
                name = ingredient.get('name', '').lower()
                amount = ingredient.get('amount', 0)
                unit = ingredient.get('unit', 'g')
                
                # Normalizar unidades a gramos si es posible
                if unit == 'ml' and name in ['water', 'agua', 'milk', 'leche']:
                    amount = amount  # 1ml = ~1g para líquidos
                elif unit == 'tsp' or unit == 'teaspoon' or unit == 'cucharadita':
                    amount = amount * 5  # Aproximadamente 5g por cucharadita
                elif unit == 'tbsp' or unit == 'tablespoon' or unit == 'cucharada':
                    amount = amount * 15  # Aproximadamente 15g por cucharada
                elif unit == 'cup' or unit == 'taza':
                    amount = amount * 240  # Aproximadamente 240g por taza
                
                # Normalizar nombres de ingredientes
                normalized_name = name.replace(' ', '_').replace('-', '_')
                ingredients[normalized_name] = amount
        
        # Convertir instrucciones
        if 'analyzedInstructions' in recipe and recipe['analyzedInstructions']:
            for instruction_group in recipe['analyzedInstructions']:
                for step in instruction_group.get('steps', []):
                    instructions.append(step.get('step', ''))
        elif 'instructions' in recipe and recipe['instructions']:
            # Dividir por puntos o números si no hay instrucciones analizadas
            import re
            text = recipe['instructions']
            # Intentar dividir por números seguidos de punto o paréntesis
            matches = re.findall(r'\d+[\.\)]|\.', text)
            if matches:
                parts = re.split(r'\d+[\.\)]|\.', text)
                # Eliminar elementos vacíos
                instructions = [p.strip() for p in parts if p.strip()]
            else:
                # Si no hay divisores claros, usar puntos
                instructions = [s.strip() for s in text.split('.') if s.strip()]
        
        # Propiedades
        properties = {
            "sin_gluten": is_gluten_free,
            "vegano": is_vegan,
            "vegetariano": is_vegetarian,
            "sin_lactosa": is_dairy_free,
            "de_spoonacular": True,
            "original_id": recipe.get('id', 0),
            "original_url": recipe.get('sourceUrl', '')
        }
        
        # Construir resultado final
        result = {
            "detected_type": dough_type,
            "ingredients": ingredients,
            "properties": properties,
            "instructions": instructions,
            "name": recipe_name,
            "image": recipe.get('image', '')
        }
        
        return result
    
    def get_cheesecake_base_recipe(self, gluten_free: bool = False, dairy_free: bool = False) -> Dict[str, Any]:
        """
        Obtiene una receta específica para base de cheesecake.
        
        Args:
            gluten_free: Si debe ser sin gluten
            dairy_free: Si debe ser sin lactosa
            
        Returns:
            Receta en formato TRIVO-AI
        """
        # Construir query
        query = "cheesecake base crust"
        diet = []
        intolerances = []
        
        if gluten_free:
            diet.append("gluten free")
            intolerances.append("gluten")
            query += " gluten free"
        
        if dairy_free:
            intolerances.append("dairy")
            query += " dairy free"
        
        # Realizar búsqueda
        recipes = self.search_recipes(
            query=query,
            diet=",".join(diet) if diet else None,
            intolerances=",".join(intolerances) if intolerances else None,
            number=3
        )
        
        if not recipes:
            logger.warning("No se encontraron recetas de base de cheesecake")
            # Devolver receta por defecto
            return self._get_default_cheesecake_base(gluten_free, dairy_free)
        
        # Tomar la primera receta
        recipe = recipes[0]
        
        # Si encontramos la receta completa, filtrar solo la parte de la base
        if 'base' in recipe.get('title', '').lower() or 'crust' in recipe.get('title', '').lower():
            # Ya es una receta de base
            return self.convert_spoonacular_to_trivo(recipe)
        else:
            # Es una receta completa, intentar filtrar solo la base
            recipe_detail = self.get_recipe_by_id(recipe['id'])
            base_instructions = []
            
            # Buscar instrucciones relacionadas con la base
            if 'analyzedInstructions' in recipe_detail and recipe_detail['analyzedInstructions']:
                for instruction_group in recipe_detail['analyzedInstructions']:
                    for step in instruction_group.get('steps', []):
                        step_text = step.get('step', '').lower()
                        # Identificar pasos relacionados con la base
                        if any(word in step_text for word in ['crust', 'base', 'graham', 'galleta', 'mantequilla', 'butter', 'press', 'presionar']):
                            base_instructions.append(step.get('step', ''))
            
            # Si encontramos instrucciones específicas para la base
            if base_instructions:
                # Crear una copia de la receta y modificarla
                base_recipe = self.convert_spoonacular_to_trivo(recipe_detail)
                base_recipe['instructions'] = base_instructions
                return base_recipe
            
            # Si no pudimos filtrar, devolver la receta completa
            return self.convert_spoonacular_to_trivo(recipe_detail)
    
    def _get_default_cheesecake_base(self, gluten_free: bool = False, dairy_free: bool = False) -> Dict[str, Any]:
        """
        Devuelve una receta por defecto para base de cheesecake.
        
        Args:
            gluten_free: Si debe ser sin gluten
            dairy_free: Si debe ser sin lactosa
            
        Returns:
            Receta en formato TRIVO-AI
        """
        if gluten_free and dairy_free:
            # Base sin gluten y sin lácteos
            ingredients = {
                "galletas_sin_gluten": 200.0,
                "aceite_coco": 80.0,
                "azucar_moreno": 30.0,
                "semillas_chia_molidas": 10.0
            }
            instructions = [
                "Tritura las galletas sin gluten hasta obtener un polvo fino.",
                "Derrite el aceite de coco a temperatura baja.",
                "Mezcla las galletas trituradas con el aceite de coco derretido y el azúcar moreno.",
                "Añade las semillas de chía molidas para mejorar la cohesión de la masa.",
                "Presiona la mezcla en el fondo de un molde desmontable formando una capa uniforme.",
                "Refrigera durante 30 minutos para que la base tome consistencia."
            ]
        elif gluten_free:
            # Base sin gluten
            ingredients = {
                "galletas_sin_gluten": 200.0,
                "mantequilla": 100.0,
                "azucar_moreno": 30.0,
                "semillas_chia_molidas": 10.0
            }
            instructions = [
                "Tritura las galletas sin gluten hasta obtener un polvo fino.",
                "Derrite la mantequilla a temperatura baja.",
                "Mezcla las galletas trituradas con la mantequilla derretida y el azúcar moreno.",
                "Añade las semillas de chía molidas para evitar que la base quede harinosa.",
                "Presiona la mezcla en el fondo de un molde desmontable formando una capa uniforme.",
                "Hornea a 150°C durante 5-7 minutos para sellar la base y evitar que se humedezca.",
                "Deja enfriar completamente antes de añadir el relleno."
            ]
        elif dairy_free:
            # Base sin lácteos
            ingredients = {
                "galletas_digestive": 200.0,
                "aceite_coco": 80.0,
                "azucar_moreno": 30.0
            }
            instructions = [
                "Tritura las galletas digestive hasta obtener un polvo fino.",
                "Derrite el aceite de coco a temperatura baja.",
                "Mezcla las galletas trituradas con el aceite de coco derretido y el azúcar moreno.",
                "Presiona la mezcla en el fondo de un molde desmontable formando una capa uniforme.",
                "Refrigera durante 30 minutos para que la base tome consistencia."
            ]
        else:
            # Base tradicional
            ingredients = {
                "galletas_digestive": 200.0,
                "mantequilla": 100.0,
                "azucar": 30.0
            }
            instructions = [
                "Tritura las galletas digestive hasta obtener un polvo fino.",
                "Derrite la mantequilla a temperatura baja.",
                "Mezcla las galletas trituradas con la mantequilla derretida y el azúcar.",
                "Presiona la mezcla en el fondo de un molde desmontable formando una capa uniforme.",
                "Refrigera durante 30 minutos o hornea a 180°C durante 8-10 minutos (opcional)."
            ]
        
        # Propiedades
        properties = {
            "sin_gluten": gluten_free,
            "sin_lactosa": dairy_free,
            "vegano": dairy_free,  # Si es sin lácteos, asumimos que es vegano
            "de_default": True,
        }
        
        return {
            "detected_type": "galletas",
            "ingredients": ingredients,
            "properties": properties,
            "instructions": instructions,
            "name": "Base para Cheesecake" + (" Sin Gluten" if gluten_free else "") + (" Sin Lácteos" if dairy_free else "")
        }
    
    def get_cheesecake_filling(self, gluten_free: bool = False, dairy_free: bool = False) -> Dict[str, Any]:
        """
        Obtiene una receta para el relleno de cheesecake.
        
        Args:
            gluten_free: Si debe ser sin gluten
            dairy_free: Si debe ser sin lactosa
            
        Returns:
            Receta en formato TRIVO-AI
        """
        # Construir query
        query = "cheesecake filling no-bake"
        diet = []
        intolerances = []
        
        if gluten_free:
            diet.append("gluten free")
            intolerances.append("gluten")
        
        if dairy_free:
            intolerances.append("dairy")
            query += " dairy free vegan"
        
        # Realizar búsqueda
        recipes = self.search_recipes(
            query=query,
            diet=",".join(diet) if diet else None,
            intolerances=",".join(intolerances) if intolerances else None,
            number=3
        )
        
        if not recipes:
            logger.warning("No se encontraron recetas de relleno de cheesecake")
            # Devolver receta por defecto
            return self._get_default_cheesecake_filling(gluten_free, dairy_free)
        
        # Tomar la primera receta
        recipe = recipes[0]
        return self.convert_spoonacular_to_trivo(recipe)
    
    def _get_default_cheesecake_filling(self, gluten_free: bool = False, dairy_free: bool = False) -> Dict[str, Any]:
        """
        Devuelve una receta por defecto para relleno de cheesecake.
        
        Args:
            gluten_free: Si debe ser sin gluten
            dairy_free: Si debe ser sin lactosa
            
        Returns:
            Receta en formato TRIVO-AI
        """
        if dairy_free:
            # Relleno vegano sin lácteos
            ingredients = {
                "anacardos_crudos": 300.0,
                "leche_coco": 200.0,
                "aceite_coco": 80.0,
                "zumo_limon": 45.0,
                "azucar": 150.0,
                "extracto_vainilla": 5.0,
                "agar_agar": 7.0  # Sustituto vegano de la gelatina
            }
            instructions = [
                "Remojar los anacardos en agua durante al menos 4 horas o toda la noche.",
                "Escurrir y enjuagar los anacardos.",
                "En una batidora potente, mezclar los anacardos, la leche de coco, el aceite de coco derretido, el zumo de limón, el azúcar y el extracto de vainilla hasta obtener una crema suave.",
                "En una cacerola, calentar 100ml de agua con el agar-agar y llevar a ebullición durante 2-3 minutos.",
                "Incorporar la mezcla de agar-agar a la crema de anacardos y mezclar rápidamente.",
                "Verter sobre la base de galletas preparada.",
                "Refrigerar durante al menos 4 horas, preferiblemente toda la noche."
            ]
        else:
            # Relleno tradicional con lácteos
            ingredients = {
                "queso_crema": 500.0,
                "azucar": 150.0,
                "huevos": 150.0,  # aproximadamente 3 huevos
                "nata_liquida": 200.0,
                "extracto_vainilla": 5.0,
                "zumo_limon": 15.0
            }
            instructions = [
                "En un bol grande, batir el queso crema hasta que esté suave y cremoso.",
                "Añadir el azúcar gradualmente y seguir batiendo hasta que se integre completamente.",
                "Incorporar los huevos uno a uno, mezclando bien después de cada adición.",
                "Añadir la nata, el extracto de vainilla y el zumo de limón, mezclando hasta obtener una crema homogénea.",
                "Verter la mezcla sobre la base de galletas preparada.",
                "Hornear a 150°C durante 1 hora o hasta que los bordes estén firmes pero el centro aún tiemble ligeramente.",
                "Apagar el horno y dejar el cheesecake dentro con la puerta entreabierta durante 1 hora.",
                "Refrigerar durante al menos 4 horas antes de servir."
            ]
        
        # Propiedades
        properties = {
            "sin_gluten": True,  # El relleno de cheesecake normalmente no contiene gluten
            "sin_lactosa": dairy_free,
            "vegano": dairy_free,
            "de_default": True,
        }
        
        return {
            "detected_type": "relleno_cheesecake",
            "ingredients": ingredients,
            "properties": properties,
            "instructions": instructions,
            "name": "Relleno para Cheesecake" + (" Sin Lácteos" if dairy_free else " Tradicional")
        }
    
    def get_complete_cheesecake_recipe(self, gluten_free: bool = False, dairy_free: bool = False, fruit: str = "") -> Dict[str, Any]:
        """
        Obtiene una receta completa de cheesecake, optimizando el uso de la API.
        
        Args:
            gluten_free: Si debe ser sin gluten
            dairy_free: Si debe ser sin lactosa
            fruit: Fruta principal para el cheesecake
            
        Returns:
            Receta en formato TRIVO-AI
        """
        # Verificar si podemos usar el caché inteligente
        if self.recipe_cache:
            # Intentar encontrar una receta similar para adaptar
            similar_recipe_id = self.recipe_cache.find_similar_recipe(
                recipe_type="cheesecake", 
                fruit=fruit,
                gluten_free=gluten_free, 
                dairy_free=dairy_free
            )
            
            if similar_recipe_id:
                logger.info(f"Encontrada receta similar en caché: {similar_recipe_id}")
                
                # Si la receta tiene exactamente las mismas características, usarla directamente
                cached_recipe = self.recipe_cache.get_recipe(similar_recipe_id)
                cached_props = cached_recipe.get('properties', {})
                
                is_exact_match = (
                    cached_props.get('sin_gluten', False) == gluten_free and
                    cached_props.get('sin_lactosa', False) == dairy_free
                )
                
                if is_exact_match:
                    # Si coincide todo excepto la fruta, adaptarla
                    detected_fruit = self.recipe_cache._detect_fruit(cached_recipe.get('name', ''), cached_recipe)
                    
                    if detected_fruit != fruit and fruit:
                        logger.info(f"Adaptando fruta de {detected_fruit} a {fruit}")
                        adapted_recipe = self.recipe_cache.adapt_recipe(
                            similar_recipe_id, 
                            new_fruit=fruit
                        )
                        # Guardar la receta adaptada en caché para futuros usos
                        self.recipe_cache.add_recipe(adapted_recipe)
                        return adapted_recipe
                    
                    # Si coincide todo, usarla tal cual
                    return cached_recipe
                
                # Si difieren las restricciones dietéticas pero tenemos una receta similar
                logger.info("Adaptando receta para restricciones dietéticas")
                adapted_recipe = self.recipe_cache.adapt_recipe(
                    similar_recipe_id, 
                    new_fruit=fruit if fruit else None,
                    gluten_free=gluten_free,
                    dairy_free=dairy_free
                )
                
                # Guardar la receta adaptada en caché para futuros usos
                self.recipe_cache.add_recipe(adapted_recipe)
                return adapted_recipe
        
        # Si llegamos aquí, no encontramos receta en caché o la adaptación no es posible
        # Realizar consulta a la API
        logger.info("Consultando a Spoonacular para obtener receta de cheesecake")
        
        # Construir query
        query = "cheesecake"
        if fruit:
            query += f" {fruit}"
        
        diet = []
        intolerances = []
        
        if gluten_free:
            diet.append("gluten free")
            intolerances.append("gluten")
            query += " gluten free"
        
        if dairy_free:
            intolerances.append("dairy")
            query += " dairy free vegan"
        
        # Realizar búsqueda
        recipes = self.search_recipes(
            query=query,
            diet=",".join(diet) if diet else None,
            intolerances=",".join(intolerances) if intolerances else None,
            number=3
        )
        
        # Si no encontramos recetas, usar el método anterior
        if not recipes:
            if dairy_free or gluten_free:
                logger.warning("No se encontraron recetas específicas, usando método antiguo")
                # Obtener las dos partes
                base = self.get_cheesecake_base_recipe(gluten_free, dairy_free)
                filling = self.get_cheesecake_filling(gluten_free, dairy_free)
                
                # Combinar
                combined_recipe = self._combine_base_and_filling(base, filling)
                
                # Añadir fruta si se especificó
                if fruit:
                    self._add_fruit_to_recipe(combined_recipe, fruit)
                
                # Guardar en caché para futuros usos
                if self.recipe_cache:
                    self.recipe_cache.add_recipe(combined_recipe)
                
                return combined_recipe
            else:
                # Para recetas estándar, usar receta por defecto
                default_recipe = self._get_default_cheesecake(fruit)
                
                # Guardar en caché para futuros usos
                if self.recipe_cache:
                    self.recipe_cache.add_recipe(default_recipe)
                
                return default_recipe
        
        # Tomar la mejor receta
        recipe = recipes[0]
        detailed_recipe = self.get_recipe_by_id(recipe['id'])
        converted_recipe = self.convert_spoonacular_to_trivo(detailed_recipe)
        
        # Añadir fruta si no estaba incluida en la receta
        if fruit and not any(fruit in ing.lower() for ing in converted_recipe.get('ingredients', {}).keys()):
            self._add_fruit_to_recipe(converted_recipe, fruit)
        
        # Guardar en caché para futuros usos
        if self.recipe_cache:
            self.recipe_cache.add_recipe(converted_recipe)
        
        return converted_recipe
    
    def _combine_base_and_filling(self, base: Dict[str, Any], filling: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combina la base y el relleno en una receta completa.
        
        Args:
            base: Receta de la base
            filling: Receta del relleno
            
        Returns:
            Receta combinada
        """
        # Combinar ingredientes
        combined_ingredients = {**base.get('ingredients', {}), **filling.get('ingredients', {})}
        
        # Combinar instrucciones
        combined_instructions = []
        combined_instructions.append("--- PREPARACIÓN DE LA BASE ---")
        combined_instructions.extend(base.get('instructions', []))
        combined_instructions.append("--- PREPARACIÓN DEL RELLENO ---")
        combined_instructions.extend(filling.get('instructions', []))
        
        # Propiedades
        properties = {
            "sin_gluten": base.get('properties', {}).get('sin_gluten', False),
            "sin_lactosa": base.get('properties', {}).get('sin_lactosa', False),
            "vegano": base.get('properties', {}).get('vegano', False),
            "de_spoonacular": base.get('properties', {}).get('de_spoonacular', False),
        }
        
        # Nombre combinado
        name = "Cheesecake"
        if properties.get('sin_gluten'):
            name += " Sin Gluten"
        if properties.get('sin_lactosa'):
            name += " Sin Lácteos"
        
        return {
            "detected_type": "cheesecake",
            "ingredients": combined_ingredients,
            "properties": properties,
            "instructions": combined_instructions,
            "name": name
        }
    
    def _add_fruit_to_recipe(self, recipe: Dict[str, Any], fruit: str) -> None:
        """
        Añade una fruta a una receta existente.
        
        Args:
            recipe: Receta a modificar
            fruit: Fruta a añadir
        """
        # Actualizar nombre
        if fruit not in recipe.get('name', '').lower():
            recipe['name'] = f"{recipe['name']} con {fruit}"
        
        # Añadir a ingredientes
        normalized_fruit = fruit.replace(' ', '_')
        if normalized_fruit not in recipe.get('ingredients', {}):
            recipe['ingredients'][normalized_fruit] = 200.0  # Cantidad estimada
        
        # Añadir a instrucciones
        instructions = recipe.get('instructions', [])
        for i, instruction in enumerate(instructions):
            if "decorar" in instruction.lower() or "cubrir" in instruction.lower():
                instructions[i] = f"Cubrir la superficie con {fruit} frescas."
                break
        else:
            # Si no hay instrucción de decoración, añadirla
            instructions.append(f"Decorar con {fruit} frescas antes de servir.")
    
    def _get_default_cheesecake(self, fruit: str = "") -> Dict[str, Any]:
        """
        Devuelve una receta predeterminada de cheesecake con la fruta especificada.
        
        Args:
            fruit: Fruta para el cheesecake
            
        Returns:
            Receta de cheesecake
        """
        # Base
        ingredients = {
            "galletas_digestive": 200.0,
            "mantequilla": 100.0,
            "azucar": 30.0,
            "queso_crema": 500.0,
            "huevos": 150.0,
            "nata_liquida": 200.0,
            "azucar": 150.0,
            "extracto_vainilla": 5.0,
            "zumo_limon": 15.0
        }
        
        # Añadir fruta si se especificó
        if fruit:
            normalized_fruit = fruit.replace(' ', '_')
            ingredients[normalized_fruit] = 200.0
        
        # Instrucciones básicas
        instructions = [
            "--- PREPARACIÓN DE LA BASE ---",
            "Tritura las galletas digestive hasta obtener un polvo fino.",
            "Derrite la mantequilla a temperatura baja.",
            "Mezcla las galletas trituradas con la mantequilla derretida y el azúcar.",
            "Presiona la mezcla en el fondo de un molde desmontable formando una capa uniforme.",
            "Refrigera durante 30 minutos para que la base tome consistencia.",
            "--- PREPARACIÓN DEL RELLENO ---",
            "En un bol grande, batir el queso crema hasta que esté suave y cremoso.",
            "Añadir el azúcar gradualmente y seguir batiendo hasta que se integre completamente.",
            "Incorporar los huevos uno a uno, mezclando bien después de cada adición.",
            "Añadir la nata, el extracto de vainilla y el zumo de limón, mezclando hasta obtener una crema homogénea.",
            "Verter la mezcla sobre la base de galletas preparada.",
            "Hornear a 150°C durante 1 hora o hasta que los bordes estén firmes pero el centro aún tiemble ligeramente.",
            "Apagar el horno y dejar el cheesecake dentro con la puerta entreabierta durante 1 hora.",
            "Refrigerar durante al menos 4 horas antes de servir."
        ]
        
        # Añadir paso para la fruta
        if fruit:
            instructions.append(f"Decorar con {fruit} frescas antes de servir.")
        
        # Propiedades
        properties = {
            "sin_gluten": False,
            "sin_lactosa": False,
            "vegano": False,
            "de_default": True
        }
        
        # Nombre
        name = "Cheesecake"
        if fruit:
            name += f" con {fruit}"
        
        return {
            "detected_type": "cheesecake",
            "ingredients": ingredients,
            "properties": properties,
            "instructions": instructions,
            "name": name
        } 