"""
Módulo para la generación y gestión de fichas técnicas industriales para recetas.

Este módulo permite crear documentación técnica estandarizada para la producción
industrial de masas, incluyendo información detallada sobre ingredientes, procesos,
valores nutricionales y controles de calidad.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import jinja2
from weasyprint import HTML

# Configuración de logging
logger = logging.getLogger(__name__)

class RecipeSheet:
    """
    Clase para la creación y gestión de fichas técnicas industriales de recetas.
    Permite generar documentación estandarizada para producción y control de calidad.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Inicializa el gestor de fichas técnicas.
        
        Args:
            data_dir: Directorio donde se almacenan los datos y plantillas
        """
        self.data_dir = data_dir
        self.sheets_dir = os.path.join(data_dir, "recipe_sheets")
        self.templates_dir = os.path.join("app", "templates", "recipe_sheets")
        self.pdf_output_dir = os.path.join(data_dir, "pdf_sheets")
        
        # Asegurar que los directorios existen
        os.makedirs(self.sheets_dir, exist_ok=True)
        os.makedirs(self.pdf_output_dir, exist_ok=True)
        
        # Configurar entorno de plantillas Jinja2
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Tabla de alérgenos comunes
        self.allergens = [
            "Gluten", "Lácteos", "Huevos", "Frutos secos", "Maní", 
            "Soja", "Pescado", "Mariscos", "Sésamo", "Sulfitos"
        ]
        
        # Etapas de proceso estándar
        self.standard_stages = [
            "Preparación", "Mezcla", "Amasado", "Fermentación", 
            "División", "Formado", "Horneado", "Enfriamiento", "Empaquetado"
        ]
    
    def create_recipe_sheet(self, 
                           recipe_data: Dict[str, Any], 
                           ingredients: List[Dict],
                           process_steps: List[Dict],
                           author: str = "Sistema") -> Dict[str, Any]:
        """
        Crea una nueva ficha técnica para una receta.
        
        Args:
            recipe_data: Datos generales de la receta (nombre, descripción, etc.)
            ingredients: Lista de ingredientes con cantidades
            process_steps: Pasos del proceso detallados
            author: Autor de la ficha técnica
            
        Returns:
            Diccionario con los datos de la ficha técnica creada
        """
        try:
            # Generar ID único
            recipe_id = recipe_data.get("id", f"RT-{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            # Estructura base para ficha técnica
            recipe_sheet = {
                "id": recipe_id,
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "author": author,
                "recipe_info": {
                    "name": recipe_data.get("name", ""),
                    "description": recipe_data.get("description", ""),
                    "category": recipe_data.get("category", ""),
                    "target_market": recipe_data.get("target_market", "General"),
                    "version": recipe_data.get("version", "1.0"),
                    "serving_size": recipe_data.get("serving_size", ""),
                    "yield": recipe_data.get("yield", {
                        "amount": 0,
                        "unit": "g"
                    }),
                    "total_time": recipe_data.get("total_time", 0),
                    "difficulty": recipe_data.get("difficulty", "Media"),
                    "shelf_life": recipe_data.get("shelf_life", {
                        "ambient": "1 día",
                        "refrigerated": "3 días",
                        "frozen": "30 días"
                    }),
                    "certification": recipe_data.get("certification", [])
                },
                "ingredients": self._format_ingredients(ingredients),
                "process": {
                    "preparation_time": recipe_data.get("preparation_time", 0),
                    "mixing_time": recipe_data.get("mixing_time", 0),
                    "fermentation_time": recipe_data.get("fermentation_time", 0),
                    "baking_time": recipe_data.get("baking_time", 0),
                    "cooling_time": recipe_data.get("cooling_time", 0),
                    "total_production_time": recipe_data.get("total_production_time", 0),
                    "critical_control_points": recipe_data.get("critical_control_points", []),
                    "steps": process_steps
                },
                "nutrition": self._calculate_nutrition(ingredients),
                "quality_parameters": {
                    "appearance": recipe_data.get("appearance", ""),
                    "texture": recipe_data.get("texture", ""),
                    "taste": recipe_data.get("taste", ""),
                    "aroma": recipe_data.get("aroma", ""),
                    "ph": recipe_data.get("ph", ""),
                    "moisture": recipe_data.get("moisture", ""),
                    "color_parameters": recipe_data.get("color_parameters", {})
                },
                "allergens": self._identify_allergens(ingredients),
                "packaging": {
                    "primary": recipe_data.get("primary_packaging", ""),
                    "secondary": recipe_data.get("secondary_packaging", ""),
                    "tertiary": recipe_data.get("tertiary_packaging", ""),
                    "labeling": recipe_data.get("labeling", [])
                },
                "storage": {
                    "temperature": recipe_data.get("storage_temperature", ""),
                    "humidity": recipe_data.get("storage_humidity", ""),
                    "light": recipe_data.get("storage_light", "Proteger de la luz directa"),
                    "special_instructions": recipe_data.get("storage_instructions", "")
                },
                "equipment": recipe_data.get("equipment", []),
                "cost_analysis": recipe_data.get("cost_analysis", {})
            }
            
            # Calcular tiempos totales si no se proporcionaron
            if not recipe_data.get("total_production_time"):
                times = [
                    recipe_sheet["process"]["preparation_time"],
                    recipe_sheet["process"]["mixing_time"],
                    recipe_sheet["process"]["fermentation_time"],
                    recipe_sheet["process"]["baking_time"],
                    recipe_sheet["process"]["cooling_time"]
                ]
                recipe_sheet["process"]["total_production_time"] = sum(t for t in times if t)
            
            # Guardar la ficha técnica
            self._save_recipe_sheet(recipe_id, recipe_sheet)
            
            return recipe_sheet
        
        except Exception as e:
            logger.error(f"Error al crear ficha técnica: {e}")
            raise
    
    def update_recipe_sheet(self, 
                           recipe_id: str, 
                           updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Actualiza una ficha técnica existente.
        
        Args:
            recipe_id: ID de la receta a actualizar
            updates: Diccionario con los campos a actualizar
            
        Returns:
            Ficha técnica actualizada o None si no se encuentra
        """
        try:
            # Cargar la ficha técnica existente
            recipe_sheet = self._load_recipe_sheet(recipe_id)
            if not recipe_sheet:
                logger.warning(f"No se encontró la ficha técnica con ID {recipe_id}")
                return None
            
            # Actualizar la versión y fecha
            recipe_sheet["version"] = str(float(recipe_sheet["version"]) + 0.1)
            recipe_sheet["updated_at"] = datetime.now().isoformat()
            
            # Función recursiva para actualizar campos anidados
            def update_nested_dict(d, u):
                for k, v in u.items():
                    if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                        d[k] = update_nested_dict(d[k], v)
                    else:
                        d[k] = v
                return d
            
            # Aplicar actualizaciones
            recipe_sheet = update_nested_dict(recipe_sheet, updates)
            
            # Guardar la ficha técnica actualizada
            self._save_recipe_sheet(recipe_id, recipe_sheet)
            
            return recipe_sheet
        
        except Exception as e:
            logger.error(f"Error al actualizar ficha técnica: {e}")
            return None
    
    def get_recipe_sheet(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una ficha técnica por su ID.
        
        Args:
            recipe_id: ID de la receta
            
        Returns:
            Diccionario con la ficha técnica o None si no existe
        """
        return self._load_recipe_sheet(recipe_id)
    
    def delete_recipe_sheet(self, recipe_id: str) -> bool:
        """
        Elimina una ficha técnica.
        
        Args:
            recipe_id: ID de la receta a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            file_path = os.path.join(self.sheets_dir, f"{recipe_id}.json")
            if not os.path.exists(file_path):
                logger.warning(f"No se encontró la ficha técnica con ID {recipe_id}")
                return False
            
            os.remove(file_path)
            
            # Eliminar PDF si existe
            pdf_path = os.path.join(self.pdf_output_dir, f"{recipe_id}.pdf")
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                
            return True
        
        except Exception as e:
            logger.error(f"Error al eliminar ficha técnica: {e}")
            return False
    
    def list_recipe_sheets(self) -> List[Dict[str, Any]]:
        """
        Lista todas las fichas técnicas disponibles.
        
        Returns:
            Lista con información resumida de todas las fichas
        """
        try:
            sheets = []
            
            for filename in os.listdir(self.sheets_dir):
                if filename.endswith(".json"):
                    recipe_id = filename[:-5]  # Quitar extensión .json
                    sheet = self._load_recipe_sheet(recipe_id)
                    
                    if sheet:
                        # Información resumida
                        sheets.append({
                            "id": sheet["id"],
                            "name": sheet["recipe_info"]["name"],
                            "version": sheet["version"],
                            "category": sheet["recipe_info"]["category"],
                            "updated_at": sheet["updated_at"]
                        })
            
            # Ordenar por fecha de actualización
            sheets.sort(key=lambda x: x["updated_at"], reverse=True)
            
            return sheets
        
        except Exception as e:
            logger.error(f"Error al listar fichas técnicas: {e}")
            return []
    
    def generate_pdf(self, recipe_id: str) -> Optional[str]:
        """
        Genera un PDF a partir de una ficha técnica.
        
        Args:
            recipe_id: ID de la receta
            
        Returns:
            Ruta al archivo PDF generado o None si falla
        """
        try:
            # Cargar la ficha técnica
            recipe_sheet = self._load_recipe_sheet(recipe_id)
            if not recipe_sheet:
                logger.warning(f"No se encontró la ficha técnica con ID {recipe_id}")
                return None
            
            # Cargar plantilla
            template = self.template_env.get_template("recipe_sheet_template.html")
            
            # Renderizar HTML
            html_content = template.render(
                recipe=recipe_sheet,
                current_date=datetime.now().strftime("%d/%m/%Y"),
                page_size="A4"
            )
            
            # Ruta del PDF de salida
            pdf_path = os.path.join(self.pdf_output_dir, f"{recipe_id}.pdf")
            
            # Generar PDF
            HTML(string=html_content).write_pdf(pdf_path)
            
            return pdf_path
        
        except Exception as e:
            logger.error(f"Error al generar PDF: {e}")
            return None
    
    def generate_production_sheet(self, recipe_id: str, batch_size: float) -> Optional[Dict[str, Any]]:
        """
        Genera una hoja de producción para un tamaño de lote específico.
        
        Args:
            recipe_id: ID de la receta
            batch_size: Tamaño del lote en kg o unidades
            
        Returns:
            Diccionario con la hoja de producción o None si falla
        """
        try:
            # Cargar la ficha técnica
            recipe_sheet = self._load_recipe_sheet(recipe_id)
            if not recipe_sheet:
                logger.warning(f"No se encontró la ficha técnica con ID {recipe_id}")
                return None
            
            # Calcular factor de escala
            base_yield = recipe_sheet["recipe_info"]["yield"]["amount"]
            if base_yield == 0:
                logger.warning("El rendimiento base es 0, no se puede calcular el factor de escala")
                return None
                
            scale_factor = batch_size / base_yield
            
            # Escalar ingredientes
            scaled_ingredients = []
            for ingredient in recipe_sheet["ingredients"]:
                scaled_ingredient = ingredient.copy()
                scaled_ingredient["amount"] *= scale_factor
                scaled_ingredients.append(scaled_ingredient)
            
            # Crear hoja de producción
            production_sheet = {
                "id": f"{recipe_id}-PROD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "recipe_id": recipe_id,
                "recipe_name": recipe_sheet["recipe_info"]["name"],
                "batch_size": batch_size,
                "batch_unit": recipe_sheet["recipe_info"]["yield"]["unit"],
                "production_date": datetime.now().isoformat(),
                "ingredients": scaled_ingredients,
                "process": recipe_sheet["process"],
                "quality_checks": recipe_sheet["quality_parameters"],
                "special_instructions": "",
                "equipment": recipe_sheet["equipment"]
            }
            
            return production_sheet
        
        except Exception as e:
            logger.error(f"Error al generar hoja de producción: {e}")
            return None
    
    def _format_ingredients(self, ingredients: List[Dict]) -> List[Dict]:
        """
        Formatea la lista de ingredientes para la ficha técnica.
        
        Args:
            ingredients: Lista de ingredientes
            
        Returns:
            Lista de ingredientes formateada
        """
        formatted = []
        
        for i, ingredient in enumerate(ingredients):
            formatted_ingredient = {
                "order": i + 1,
                "name": ingredient.get("name", ""),
                "amount": float(ingredient.get("amount", 0)),
                "unit": ingredient.get("unit", "g"),
                "percentage": 0,  # Se calculará después
                "function": ingredient.get("function", ""),
                "supplier": ingredient.get("supplier", ""),
                "substitutes": ingredient.get("substitutes", []),
                "critical": ingredient.get("critical", False)
            }
            
            formatted.append(formatted_ingredient)
        
        # Calcular porcentajes respecto al total de harina (panadería)
        flour_ingredients = [ing for ing in formatted if "harina" in ing["name"].lower()]
        total_flour = sum(ing["amount"] for ing in flour_ingredients)
        
        if total_flour > 0:
            for ingredient in formatted:
                ingredient["percentage"] = round((ingredient["amount"] / total_flour) * 100, 2)
        
        return formatted
    
    def _calculate_nutrition(self, ingredients: List[Dict]) -> Dict[str, Any]:
        """
        Calcula información nutricional aproximada.
        Este es un cálculo simplificado y debe ajustarse con datos reales.
        
        Args:
            ingredients: Lista de ingredientes
            
        Returns:
            Diccionario con información nutricional
        """
        # En una implementación real, esto consultaría una base de datos 
        # de valores nutricionales por ingrediente
        
        # Valores nutricionales aproximados por simplicidad
        nutrition = {
            "calories": 0,
            "protein": 0,
            "carbohydrates": 0,
            "sugars": 0,
            "fat": 0,
            "saturated_fat": 0,
            "fiber": 0,
            "sodium": 0,
            "per_serving": {
                "amount": 0,
                "unit": "g"
            },
            "per_100g": {},
            "daily_values": {}
        }
        
        # Aquí se implementaría un cálculo real
        # Este es solo un ejemplo simplificado
        
        total_weight = sum(
            ingredient.get("amount", 0) 
            for ingredient in ingredients 
            if ingredient.get("unit", "") in ["g", "ml"]
        )
        
        # Valores aproximados para ejemplificar
        if total_weight > 0:
            if any("harina" in ing.get("name", "").lower() for ing in ingredients):
                # Valores aproximados para masas
                nutrition["calories"] = total_weight * 2.5  # ~250 kcal/100g
                nutrition["protein"] = total_weight * 0.08  # ~8g/100g
                nutrition["carbohydrates"] = total_weight * 0.5  # ~50g/100g
                nutrition["fat"] = total_weight * 0.01  # ~1g/100g
                nutrition["fiber"] = total_weight * 0.03  # ~3g/100g
            
        # Normalizar a 100g
        if total_weight > 0:
            factor = 100 / total_weight
            nutrition["per_100g"] = {
                "calories": round(nutrition["calories"] * factor, 1),
                "protein": round(nutrition["protein"] * factor, 1),
                "carbohydrates": round(nutrition["carbohydrates"] * factor, 1),
                "sugars": round(nutrition["sugars"] * factor, 1),
                "fat": round(nutrition["fat"] * factor, 1),
                "saturated_fat": round(nutrition["saturated_fat"] * factor, 1),
                "fiber": round(nutrition["fiber"] * factor, 1),
                "sodium": round(nutrition["sodium"] * factor, 1)
            }
        
        return nutrition
    
    def _identify_allergens(self, ingredients: List[Dict]) -> Dict[str, bool]:
        """
        Identifica alérgenos presentes en los ingredientes.
        
        Args:
            ingredients: Lista de ingredientes
            
        Returns:
            Diccionario con alérgenos y su presencia
        """
        allergen_mapping = {
            "gluten": ["harina", "trigo", "cebada", "centeno", "avena", "espelta"],
            "lácteos": ["leche", "queso", "yogur", "mantequilla", "crema", "suero"],
            "huevos": ["huevo", "yema", "clara", "albumina"],
            "frutos secos": ["almendra", "nuez", "avellana", "pistacho", "anacardo"],
            "maní": ["cacahuete", "maní"],
            "soja": ["soja", "soya", "tofu", "lecitina"],
            "pescado": ["pescado", "atún", "salmón"],
            "mariscos": ["camarón", "langosta", "cangrejo", "marisco"],
            "sésamo": ["sésamo", "ajonjolí"],
            "sulfitos": ["sulfito", "dióxido de azufre", "metabisulfito"]
        }
        
        allergens = {allergen: False for allergen in self.allergens}
        
        # Detectar alérgenos en ingredientes
        for ingredient in ingredients:
            ingredient_name = ingredient.get("name", "").lower()
            
            for allergen, keywords in allergen_mapping.items():
                if any(keyword in ingredient_name for keyword in keywords):
                    allergens[allergen.capitalize()] = True
        
        return allergens
    
    def _save_recipe_sheet(self, recipe_id: str, recipe_sheet: Dict[str, Any]) -> bool:
        """
        Guarda una ficha técnica en el sistema de archivos.
        
        Args:
            recipe_id: ID de la receta
            recipe_sheet: Datos de la ficha técnica
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            file_path = os.path.join(self.sheets_dir, f"{recipe_id}.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(recipe_sheet, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            logger.error(f"Error al guardar ficha técnica: {e}")
            return False
    
    def _load_recipe_sheet(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Carga una ficha técnica desde el sistema de archivos.
        
        Args:
            recipe_id: ID de la receta
            
        Returns:
            Diccionario con la ficha técnica o None si no existe
        """
        try:
            file_path = os.path.join(self.sheets_dir, f"{recipe_id}.json")
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Error al cargar ficha técnica: {e}")
            return None


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar gestor de fichas técnicas
    recipe_sheet_manager = RecipeSheet()
    
    # Ejemplo de datos para una ficha técnica
    recipe_data = {
        "name": "Pan de Masa Madre",
        "description": "Pan artesanal con masa madre natural",
        "category": "Panadería artesanal",
        "yield": {
            "amount": 1000,
            "unit": "g"
        },
        "difficulty": "Media",
        "preparation_time": 30,
        "fermentation_time": 240,
        "baking_time": 45,
        "cooling_time": 60,
        "appearance": "Corteza crujiente, miga alveolada",
        "texture": "Crujiente por fuera, suave por dentro",
        "equipment": ["Amasadora", "Horno de piedra", "Cuchillas para corte"]
    }
    
    ingredients = [
        {"name": "Harina de trigo", "amount": 500, "unit": "g", "function": "Base", "critical": True},
        {"name": "Agua", "amount": 350, "unit": "ml", "function": "Hidratación"},
        {"name": "Masa madre activa", "amount": 150, "unit": "g", "function": "Fermentación", "critical": True},
        {"name": "Sal", "amount": 10, "unit": "g", "function": "Sabor y control de fermentación"}
    ]
    
    process_steps = [
        {
            "order": 1,
            "name": "Autólisis",
            "description": "Mezclar harina y agua, dejar reposar 30 minutos",
            "time": 30,
            "temperature": "Ambiente",
            "critical": False
        },
        {
            "order": 2,
            "name": "Incorporación de masa madre",
            "description": "Añadir la masa madre activa y mezclar hasta incorporar",
            "time": 5,
            "temperature": "Ambiente",
            "critical": True
        },
        {
            "order": 3,
            "name": "Incorporación de sal",
            "description": "Añadir la sal y amasar hasta desarrollar gluten",
            "time": 10,
            "temperature": "Ambiente",
            "critical": False
        },
        {
            "order": 4,
            "name": "Fermentación primaria",
            "description": "Dejar fermentar con pliegues cada 30 minutos",
            "time": 180,
            "temperature": "24°C",
            "critical": True
        },
        {
            "order": 5,
            "name": "División y formado",
            "description": "Dividir y formar la masa según formato deseado",
            "time": 15,
            "temperature": "Ambiente",
            "critical": False
        },
        {
            "order": 6,
            "name": "Fermentación secundaria",
            "description": "Fermentar en frío para desarrollar sabor",
            "time": 720,
            "temperature": "4°C",
            "critical": True
        },
        {
            "order": 7,
            "name": "Horneado",
            "description": "Hornear con vapor inicial y luego secar",
            "time": 45,
            "temperature": "230°C inicial, 210°C final",
            "critical": True
        },
        {
            "order": 8,
            "name": "Enfriamiento",
            "description": "Enfriar sobre rejilla antes de consumir",
            "time": 60,
            "temperature": "Ambiente",
            "critical": False
        }
    ]
    
    # Crear ficha técnica
    sheet = recipe_sheet_manager.create_recipe_sheet(recipe_data, ingredients, process_steps)
    
    if sheet:
        print(f"Ficha técnica creada: {sheet['id']}")
        
        # Generar PDF
        pdf_path = recipe_sheet_manager.generate_pdf(sheet['id'])
        if pdf_path:
            print(f"PDF generado en: {pdf_path}")
        
        # Generar hoja de producción
        production_sheet = recipe_sheet_manager.generate_production_sheet(sheet['id'], 5000)
        if production_sheet:
            print(f"Hoja de producción generada para 5kg: {production_sheet['id']}")
            print(f"Ingredientes escalados: {len(production_sheet['ingredients'])}") 