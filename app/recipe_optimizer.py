import sys
import os
import json
from typing import Dict, List, Tuple, Any

# Añadir la ruta del proyecto para importar desde src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar el optimizador genético
try:
    from src.features.genetic_optimizer import GeneticRecipeOptimizer
except ImportError:
    # Si no lo encuentra, definir un stub para desarrollo
    class GeneticRecipeOptimizer:
        def optimize(self, base_recipe, recipe_type, properties):
            return base_recipe, ["Optimizador genético no disponible"]

class RecipeOptimizer:
    """
    Clase para optimizar recetas de masa utilizando algoritmos genéticos
    y heurísticas nutricionales.
    """
    
    def __init__(self):
        """Inicializar el optimizador de recetas."""
        self.genetic_optimizer = GeneticRecipeOptimizer(
            population_size=30,  # Tamaño reducido para la versión MVP
            generations=20,      # Menos generaciones para la versión MVP
            mutation_rate=0.2,
            crossover_rate=0.7,
            elitism_count=2
        )
        
        # Reglas heurísticas para optimización rápida
        self.optimization_rules = {
            "pizza": {
                "hydration": (0.55, 0.65),      # Rango óptimo de hidratación (agua/harina)
                "salt": (0.018, 0.022),         # Rango óptimo de sal (1.8-2.2%)
                "yeast": (0.005, 0.015),        # Rango óptimo de levadura (0.5-1.5%)
                "oil": (0.03, 0.08)             # Rango óptimo de aceite (3-8%)
            },
            "pan": {
                "hydration": (0.65, 0.75),      # Pan requiere más hidratación
                "salt": (0.018, 0.022),         # Similar a pizza
                "yeast": (0.005, 0.015),        # Similar a pizza
                "oil": (0.01, 0.03)             # Menos aceite que pizza
            },
            "flatbread": {
                "hydration": (0.60, 0.70),      # Intermedio
                "salt": (0.015, 0.020),         # Ligeramente menos sal
                "yeast": (0.003, 0.010),        # Menos levadura
                "oil": (0.05, 0.10)             # Más aceite
            }
        }

    def optimize_recipe(self, recipe_data: Dict[str, float], recipe_type: str = "pizza") -> Tuple[Dict[str, float], List[str]]:
        """
        Optimiza una receta utilizando algoritmos genéticos.
        
        Args:
            recipe_data: Diccionario con los ingredientes y cantidades de la receta
            recipe_type: Tipo de receta (pizza, pan, flatbread, etc.)
            
        Returns:
            Tuple con la receta optimizada y una lista de recomendaciones
        """
        # Preservar nombre y ID de la receta si existen
        recipe_name = recipe_data.get("recipe_name", "Receta Optimizada")
        recipe_id = recipe_data.get("recipe_id", "optimized_" + str(hash(recipe_name) % 10000))
        
        # Hacer una copia limpia de la receta
        clean_recipe = {k: float(v) if isinstance(v, (int, float)) else 0.0 
                        for k, v in recipe_data.items() 
                        if k not in ["recipe_name", "recipe_id"]}
        
        # Detectar propiedades especiales de la receta
        properties = self._detect_recipe_properties(clean_recipe)
        
        # Realizar optimización con el algoritmo genético
        try:
            optimized_recipe, recommendations = self.genetic_optimizer.optimize(
                clean_recipe, recipe_type, properties
            )
        except Exception as e:
            print(f"Error en optimización genética: {e}")
            # Fallback: usar optimización heurística simple
            optimized_recipe, recommendations = self._heuristic_optimization(
                clean_recipe, recipe_type, properties
            )
        
        # Restaurar nombre e ID
        optimized_recipe["recipe_name"] = recipe_name
        optimized_recipe["recipe_id"] = recipe_id
        
        return optimized_recipe, recommendations

    def _detect_recipe_properties(self, recipe: Dict[str, float]) -> Dict[str, Any]:
        """
        Detecta propiedades especiales de la receta como si es sin gluten,
        si tiene color especial, etc.
        
        Args:
            recipe: Diccionario con los ingredientes y cantidades
            
        Returns:
            Diccionario con propiedades detectadas
        """
        properties = {
            "es_sin_gluten": False,
            "es_nutricional": False,
            "colores": {
                "rojo": False,
                "verde": False,
                "negro": False
            }
        }
        
        # Detectar si es sin gluten
        gluten_ingredients = ["harina"]
        gluten_free_ingredients = ["harina_de_arroz", "harina_de_maíz", "almidón_de_maíz", 
                                  "harina_de_arroz", "goma_xantana"]
        
        has_gluten = any(ing in recipe for ing in gluten_ingredients)
        has_gluten_free = any(ing in recipe for ing in gluten_free_ingredients)
        
        if not has_gluten and has_gluten_free:
            properties["es_sin_gluten"] = True
        
        # Detectar color
        if "remolacha" in recipe:
            properties["colores"]["rojo"] = True
        if "espinaca" in recipe:
            properties["colores"]["verde"] = True
        if "carbón_activado" in recipe:
            properties["colores"]["negro"] = True
        
        # Detectar si es nutricional
        nutrition_ingredients = ["semillas_de_lino", "semillas_de_chía", "semillas_de_girasol", 
                                "salvado", "harina_integral"]
        
        if any(ing in recipe for ing in nutrition_ingredients):
            properties["es_nutricional"] = True
        
        return properties

    def _heuristic_optimization(self, recipe: Dict[str, float], recipe_type: str, 
                              properties: Dict[str, Any]) -> Tuple[Dict[str, float], List[str]]:
        """
        Optimiza la receta utilizando reglas heurísticas cuando el algoritmo genético no está disponible.
        
        Args:
            recipe: Diccionario con ingredientes y cantidades
            recipe_type: Tipo de receta
            properties: Propiedades especiales de la receta
            
        Returns:
            Receta optimizada y lista de recomendaciones
        """
        # Crear una copia de la receta para no modificar la original
        optimized = recipe.copy()
        
        # Obtener las reglas para este tipo de receta
        rules = self.optimization_rules.get(recipe_type, self.optimization_rules["pizza"])
        
        # Calcular cantidad total de harina
        flour_amount = 0
        for key in recipe:
            if "harina" in key:
                flour_amount += recipe[key]
        
        if flour_amount == 0:
            # Si no hay harina, no podemos optimizar
            return recipe, ["La receta debe contener algún tipo de harina."]
        
        # Ajustar valores clave según las reglas
        
        # 1. Hidratación (agua/harina)
        liquid_amount = sum(recipe.get(liquid, 0) for liquid in ["agua", "leche", "yogur"])
        current_hydration = liquid_amount / flour_amount
        target_hydration = sum(rules["hydration"]) / 2  # Punto medio del rango óptimo
        
        # Si hay agua, ajustarla; si no, añadirla
        if "agua" in optimized:
            optimized["agua"] = flour_amount * target_hydration
        else:
            optimized["agua"] = flour_amount * target_hydration
        
        # 2. Sal
        salt_amount = recipe.get("sal", 0)
        target_salt = flour_amount * sum(rules["salt"]) / 2
        optimized["sal"] = target_salt
        
        # 3. Levadura
        if "levadura" in recipe:
            target_yeast = flour_amount * sum(rules["yeast"]) / 2
            optimized["levadura"] = target_yeast
        
        # 4. Aceite
        if "aceite_de_oliva" in recipe:
            target_oil = flour_amount * sum(rules["oil"]) / 2
            optimized["aceite_de_oliva"] = target_oil
        
        # Aplicar propiedades especiales
        
        # Masa sin gluten
        if properties.get("es_sin_gluten", False):
            if "harina" in optimized:
                # Reemplazar harina normal con alternativas sin gluten
                flour_amount = optimized.pop("harina")
                optimized["harina_de_arroz"] = flour_amount * 0.7
                optimized["almidón_de_maíz"] = flour_amount * 0.3
                
                # Añadir goma xantana si no la tiene
                if "goma_xantana" not in optimized:
                    optimized["goma_xantana"] = flour_amount * 0.03
        
        # Colores
        colores = properties.get("colores", {})
        if colores.get("rojo", False) and "remolacha" not in optimized:
            optimized["remolacha"] = flour_amount * 0.15
        elif colores.get("verde", False) and "espinaca" not in optimized:
            optimized["espinaca"] = flour_amount * 0.15
        elif colores.get("negro", False) and "carbón_activado" not in optimized:
            optimized["carbón_activado"] = flour_amount * 0.05
        
        # Nutricional
        if properties.get("es_nutricional", False):
            if "semillas_de_lino" not in optimized:
                optimized["semillas_de_lino"] = flour_amount * 0.05
            if "semillas_de_chía" not in optimized:
                optimized["semillas_de_chía"] = flour_amount * 0.03
        
        # Generar recomendaciones
        recommendations = self._generate_heuristic_recommendations(optimized, recipe_type, properties)
        
        return optimized, recommendations

    def _generate_heuristic_recommendations(self, recipe: Dict[str, float], recipe_type: str, 
                                         properties: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en la receta optimizada con reglas heurísticas."""
        recommendations = []
        
        # Calcular hidratación
        flour_amount = sum(recipe[key] for key in recipe if "harina" in key)
        liquid_amount = sum(recipe.get(liquid, 0) for liquid in ["agua", "leche", "yogur"])
        hydration = (liquid_amount / flour_amount) * 100
        
        if recipe_type == "pizza":
            recommendations.append(f"La hidratación óptima para pizza está entre 55% y 65%. Tu receta tiene {hydration:.1f}%.")
        elif recipe_type == "pan":
            recommendations.append(f"La hidratación óptima para pan está entre 65% y 75%. Tu receta tiene {hydration:.1f}%.")
        elif recipe_type == "flatbread":
            recommendations.append(f"La hidratación óptima para pan plano está entre 60% y 70%. Tu receta tiene {hydration:.1f}%.")
        
        # Masa sin gluten
        if properties.get("es_sin_gluten", False):
            recommendations.append("Para masas sin gluten, es importante tener una combinación de harinas y almidones.")
            if "goma_xantana" in recipe:
                recommendations.append("La goma xantana ayuda a dar elasticidad a la masa sin gluten, similar al gluten.")
            else:
                recommendations.append("Considera añadir goma xantana para mejorar la elasticidad de la masa sin gluten.")
        
        # Fermentación
        yeast_amount = recipe.get("levadura", 0)
        if yeast_amount > 0:
            yeast_ratio = (yeast_amount / flour_amount) * 100
            if yeast_ratio < 0.5:
                recommendations.append("La cantidad de levadura es baja. Considera una fermentación larga (12-24h) en frío.")
            elif yeast_ratio > 2:
                recommendations.append("La cantidad de levadura es alta. La fermentación será rápida (1-3h) a temperatura ambiente.")
        
        return recommendations 