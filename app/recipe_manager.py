import json
import os
import logging
import uuid
from datetime import datetime
from config import DATA_DIR
from app.price_manager import PriceManager

class RecipeManager:
    """
    Gestor de recetas para todo tipo de masas.
    Soporta diferentes tipos de productos: pizza, pan, pasta, postres, etc.
    """
    
    def __init__(self):
        """Inicializa el gestor de recetas."""
        self.logger = logging.getLogger("recipe-manager")
        
        # Archivos de datos
        self.recipes_dir = os.path.join(DATA_DIR, "recipes")
        self.recipe_index_file = os.path.join(DATA_DIR, "recipe_index.json")
        self.categories_file = os.path.join(DATA_DIR, "dough_categories.json")
        
        # Asegurar que existan los directorios necesarios
        if not os.path.exists(self.recipes_dir):
            os.makedirs(self.recipes_dir)
        
        # Cargar datos existentes
        self.recipe_index = self._load_recipe_index()
        self.categories = self._load_categories()
        
        # Inicializar gestor de precios para cálculos de costos
        self.price_manager = PriceManager()
    
    def _load_recipe_index(self):
        """Carga el índice de recetas desde el archivo JSON."""
        if os.path.exists(self.recipe_index_file):
            try:
                with open(self.recipe_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                self.logger.error("Error al cargar índice de recetas. Creando nuevo.")
                return {"last_updated": datetime.now().isoformat(), "recipes": []}
        return {"last_updated": datetime.now().isoformat(), "recipes": []}
    
    def _save_recipe_index(self):
        """Guarda el índice de recetas en el archivo JSON."""
        with open(self.recipe_index_file, 'w', encoding='utf-8') as f:
            json.dump(self.recipe_index, f, indent=2, ensure_ascii=False)
    
    def _load_categories(self):
        """Carga las categorías de masas desde el archivo JSON."""
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                self.logger.error("Error al cargar categorías. Creando nuevo.")
                return self._create_default_categories()
        return self._create_default_categories()
    
    def _create_default_categories(self):
        """Crea las categorías predeterminadas."""
        categories = {
            "types": [
                {
                    "id": "pizza",
                    "name": "Pizza",
                    "base_hydration": 65,
                    "description": "Masas para pizzas de varios estilos",
                    "variants": ["napolitana", "new york", "siciliana", "chicago", "sin gluten"]
                },
                {
                    "id": "bread",
                    "name": "Pan",
                    "base_hydration": 70,
                    "description": "Masas para diferentes tipos de pan",
                    "variants": ["baguette", "hogaza", "chapata", "integral", "sin gluten"]
                },
                {
                    "id": "pasta",
                    "name": "Pasta",
                    "base_hydration": 50,
                    "description": "Masas para pasta fresca",
                    "variants": ["spaghetti", "fettuccine", "ravioli", "sin gluten"]
                },
                {
                    "id": "pastry",
                    "name": "Pastelería",
                    "base_hydration": 60,
                    "description": "Masas para pastelería y repostería",
                    "variants": ["hojaldre", "quebrada", "bizcocho", "sin gluten"]
                },
                {
                    "id": "flatbread",
                    "name": "Pan Plano",
                    "base_hydration": 65,
                    "description": "Masas para panes planos",
                    "variants": ["naan", "pita", "tortilla", "focaccia", "sin gluten"]
                },
                {
                    "id": "cracker",
                    "name": "Galletas y Crackers",
                    "base_hydration": 40,
                    "description": "Masas para galletas y crackers",
                    "variants": ["saladas", "dulces", "integrales", "sin gluten"]
                }
            ],
            "base_ingredients": [
                "harina", "agua", "sal", "levadura"
            ],
            "alternative_flours": [
                "harina de arroz", "harina de maíz", "harina de garbanzos", 
                "harina de almendras", "harina de coco", "harina de sorgo",
                "harina de tapioca", "harina de quinoa", "harina de mijo",
                "harina de avena", "harina de trigo sarraceno"
            ],
            "diets": [
                "tradicional", "sin gluten", "keto", "vegana", "paleo", "integral"
            ]
        }
        
        # Guardar categorías predeterminadas
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)
        
        return categories
    
    def save_recipe(self, recipe_data):
        """
        Guarda una receta en el sistema.
        
        Args:
            recipe_data (dict): Datos de la receta
            
        Returns:
            dict: Información de la receta guardada
        """
        try:
            # Generar ID si no existe
            if "id" not in recipe_data or not recipe_data["id"]:
                recipe_data["id"] = f"recipe_{uuid.uuid4().hex[:8]}"
            
            # Agregar timestamps
            if "created_at" not in recipe_data:
                recipe_data["created_at"] = datetime.now().isoformat()
            recipe_data["updated_at"] = datetime.now().isoformat()
            
            # Asegurar que tenga categoría
            if "category" not in recipe_data or not recipe_data["category"]:
                recipe_data["category"] = "pizza"  # Categoría por defecto
            
            # Guardar archivo de receta
            recipe_file = os.path.join(self.recipes_dir, f"{recipe_data['id']}.json")
            with open(recipe_file, 'w', encoding='utf-8') as f:
                json.dump(recipe_data, f, indent=2, ensure_ascii=False)
            
            # Actualizar índice
            self._update_recipe_index(recipe_data)
            
            return {"success": True, "recipe_id": recipe_data["id"]}
        
        except Exception as e:
            self.logger.error(f"Error al guardar receta: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _update_recipe_index(self, recipe_data):
        """Actualiza el índice de recetas con la información básica."""
        # Buscar si ya existe
        existing = False
        for i, recipe in enumerate(self.recipe_index["recipes"]):
            if recipe["id"] == recipe_data["id"]:
                # Actualizar entrada existente
                self.recipe_index["recipes"][i] = {
                    "id": recipe_data["id"],
                    "name": recipe_data.get("nombre", "Sin nombre"),
                    "category": recipe_data.get("category", "pizza"),
                    "tags": recipe_data.get("tags", []),
                    "created_at": recipe_data.get("created_at"),
                    "updated_at": recipe_data.get("updated_at")
                }
                existing = True
                break
        
        # Crear nueva entrada si no existe
        if not existing:
            self.recipe_index["recipes"].append({
                "id": recipe_data["id"],
                "name": recipe_data.get("nombre", "Sin nombre"),
                "category": recipe_data.get("category", "pizza"),
                "tags": recipe_data.get("tags", []),
                "created_at": recipe_data.get("created_at"),
                "updated_at": recipe_data.get("updated_at")
            })
        
        # Actualizar fecha de última actualización
        self.recipe_index["last_updated"] = datetime.now().isoformat()
        
        # Guardar índice
        self._save_recipe_index()
    
    def get_recipe(self, recipe_id):
        """
        Obtiene una receta por su ID.
        
        Args:
            recipe_id (str): ID de la receta
            
        Returns:
            dict: Datos de la receta o error
        """
        recipe_file = os.path.join(self.recipes_dir, f"{recipe_id}.json")
        
        if os.path.exists(recipe_file):
            try:
                with open(recipe_file, 'r', encoding='utf-8') as f:
                    recipe_data = json.load(f)
                return {"success": True, "recipe": recipe_data}
            except json.JSONDecodeError:
                return {"success": False, "error": f"Formato de archivo inválido para receta {recipe_id}"}
        
        return {"success": False, "error": f"No se encontró la receta con ID {recipe_id}"}
    
    def delete_recipe(self, recipe_id):
        """
        Elimina una receta del sistema.
        
        Args:
            recipe_id (str): ID de la receta
            
        Returns:
            dict: Resultado de la operación
        """
        recipe_file = os.path.join(self.recipes_dir, f"{recipe_id}.json")
        
        if os.path.exists(recipe_file):
            try:
                # Eliminar archivo
                os.remove(recipe_file)
                
                # Actualizar índice
                self.recipe_index["recipes"] = [r for r in self.recipe_index["recipes"] if r["id"] != recipe_id]
                self.recipe_index["last_updated"] = datetime.now().isoformat()
                self._save_recipe_index()
                
                return {"success": True, "message": f"Receta {recipe_id} eliminada correctamente"}
            except Exception as e:
                return {"success": False, "error": f"Error al eliminar receta: {str(e)}"}
        
        return {"success": False, "error": f"No se encontró la receta con ID {recipe_id}"}
    
    def search_recipes(self, query=None, category=None, tags=None, page=1, limit=20):
        """
        Busca recetas según criterios específicos.
        
        Args:
            query (str, optional): Texto a buscar en nombre e ingredientes
            category (str, optional): Categoría de receta
            tags (list, optional): Lista de etiquetas
            page (int): Número de página para paginación
            limit (int): Límite de resultados por página
            
        Returns:
            dict: Resultados de la búsqueda
        """
        results = []
        
        # Aplicar filtros
        for recipe_info in self.recipe_index["recipes"]:
            # Filtrar por categoría
            if category and recipe_info.get("category") != category:
                continue
            
            # Filtrar por etiquetas
            if tags and not all(tag in recipe_info.get("tags", []) for tag in tags):
                continue
            
            # Filtrar por texto de búsqueda
            if query:
                # Necesitamos cargar la receta completa para buscar en ingredientes
                recipe_result = self.get_recipe(recipe_info["id"])
                if not recipe_result["success"]:
                    continue
                
                recipe = recipe_result["recipe"]
                
                # Buscar en nombre e ingredientes
                search_text = f"{recipe.get('nombre', '')} {recipe.get('ingredientes', '')}"
                if query.lower() not in search_text.lower():
                    continue
            
            # Agregar a resultados
            results.append(recipe_info)
        
        # Calcular paginación
        total = len(results)
        offset = (page - 1) * limit
        paginated_results = results[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "page": page,
            "total_pages": (total + limit - 1) // limit,
            "results": paginated_results
        }
    
    def calculate_dough_properties(self, recipe_data):
        """
        Calcula propiedades de la masa basadas en los ingredientes.
        
        Args:
            recipe_data (dict): Datos de la receta
            
        Returns:
            dict: Propiedades calculadas de la masa
        """
        # Parsear ingredientes
        ingredient_list = self.price_manager._parse_recipe_ingredients(recipe_data.get("ingredientes", ""))
        
        # Inicializar valores
        total_flour = 0
        total_water = 0
        total_salt = 0
        total_weight = 0
        
        # Identificar ingredientes clave y sus cantidades
        for item in ingredient_list:
            ingredient = item["ingredient"].lower()
            quantity = item["quantity"]
            unit = item["unit"].lower()
            
            # Convertir a gramos si es necesario
            weight_g = quantity
            if unit != "g":
                weight_g = self.price_manager._convert_units(quantity, unit, "g")
            
            # Sumar al peso total
            total_weight += weight_g
            
            # Categorizar ingrediente y sumar a totales correspondientes
            if "harina" in ingredient or "flour" in ingredient:
                total_flour += weight_g
            elif ingredient == "agua" or ingredient == "water":
                total_water += weight_g
            elif ingredient == "sal" or ingredient == "salt":
                total_salt += weight_g
        
        # Calcular propiedades
        properties = {
            "total_weight_g": total_weight,
            "total_flour_g": total_flour,
            "flour_percentage": 100,  # Base para baker's percentage
        }
        
        # Porcentajes panaderos (basados en harina como 100%)
        if total_flour > 0:
            properties["hydration"] = round((total_water / total_flour) * 100, 1)
            properties["salt_percentage"] = round((total_salt / total_flour) * 100, 1)
        else:
            properties["hydration"] = 0
            properties["salt_percentage"] = 0
        
        # Calcular costo
        cost_result = self.price_manager.calculate_recipe_cost(recipe_data)
        if cost_result["success"]:
            properties["total_cost"] = cost_result["total_cost"]
            properties["missing_prices"] = cost_result["missing_prices"]
            
            # Costo por kg
            if total_weight > 0:
                properties["cost_per_kg"] = round(cost_result["total_cost"] / (total_weight / 1000), 2)
        
        return properties
    
    def get_dough_categories(self):
        """
        Obtiene las categorías de masas disponibles.
        
        Returns:
            dict: Categorías de masas
        """
        return self.categories
    
    def add_dough_category(self, category_data):
        """
        Agrega una nueva categoría de masa.
        
        Args:
            category_data (dict): Información de la categoría
            
        Returns:
            dict: Resultado de la operación
        """
        # Verificar que tenga los campos necesarios
        required_fields = ["id", "name", "base_hydration"]
        for field in required_fields:
            if field not in category_data:
                return {"success": False, "error": f"Falta el campo obligatorio '{field}'"}
        
        # Verificar que no exista ya
        for category in self.categories["types"]:
            if category["id"] == category_data["id"]:
                return {"success": False, "error": f"Ya existe una categoría con ID '{category_data['id']}'"}
        
        # Agregar categoría
        self.categories["types"].append(category_data)
        
        # Guardar cambios
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(self.categories, f, indent=2, ensure_ascii=False)
        
        return {"success": True, "category": category_data}
    
    def generate_lifecycle_data(self, recipe_id):
        """
        Genera datos para el ciclo de vida de una receta.
        
        Args:
            recipe_id (str): ID de la receta
            
        Returns:
            dict: Datos del ciclo de vida
        """
        # Obtener receta
        recipe_result = self.get_recipe(recipe_id)
        if not recipe_result["success"]:
            return {"success": False, "error": recipe_result["error"]}
        
        recipe = recipe_result["recipe"]
        
        # Calcular costos y propiedades
        properties = self.calculate_dough_properties(recipe)
        
        # Definir etapas del ciclo de vida
        stages = [
            {
                "id": "ideation",
                "name": "Ideación",
                "status": "completed",
                "date": recipe.get("created_at"),
                "description": "Conceptualización y diseño inicial de la receta"
            },
            {
                "id": "formulation",
                "name": "Formulación",
                "status": "completed",
                "date": recipe.get("updated_at"),
                "description": "Desarrollo de la fórmula y ajuste de ingredientes"
            },
            {
                "id": "testing",
                "name": "Pruebas",
                "status": "in_progress",
                "date": None,
                "description": "Pruebas y validación de la receta"
            },
            {
                "id": "pilot",
                "name": "Producción Piloto",
                "status": "pending",
                "date": None,
                "description": "Producción a escala piloto"
            },
            {
                "id": "production",
                "name": "Producción",
                "status": "pending",
                "date": None,
                "description": "Producción a escala completa"
            },
            {
                "id": "distribution",
                "name": "Distribución",
                "status": "pending",
                "date": None,
                "description": "Distribución y comercialización"
            }
        ]
        
        # Generar estimaciones de costos para diferentes escalas
        cost_scales = {
            "small_batch": {
                "batch_size": "10 kg",
                "unit_cost": properties.get("cost_per_kg", 0),
                "setup_time": "2 horas",
                "labor_cost": 50,
                "overhead": 20
            },
            "medium_batch": {
                "batch_size": "100 kg",
                "unit_cost": properties.get("cost_per_kg", 0) * 0.9,  # 10% descuento por volumen
                "setup_time": "4 horas",
                "labor_cost": 200,
                "overhead": 150
            },
            "industrial": {
                "batch_size": "1000 kg",
                "unit_cost": properties.get("cost_per_kg", 0) * 0.7,  # 30% descuento por volumen
                "setup_time": "8 horas",
                "labor_cost": 1200,
                "overhead": 800
            }
        }
        
        return {
            "success": True,
            "recipe": {
                "id": recipe.get("id"),
                "name": recipe.get("nombre", "Sin nombre"),
                "category": recipe.get("category", "pizza"),
                "created_at": recipe.get("created_at"),
                "updated_at": recipe.get("updated_at"),
                "properties": properties
            },
            "lifecycle": {
                "stages": stages,
                "current_stage": "testing",
                "cost_analysis": cost_scales,
                "notes": "Datos generados automáticamente para análisis del ciclo de vida"
            }
        } 