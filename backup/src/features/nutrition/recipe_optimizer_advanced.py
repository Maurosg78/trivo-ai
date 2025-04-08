"""
Optimizador avanzado de recetas con soporte para características especiales.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union

from src.features.nutrition.nutrition_analyzer import NutritionAnalyzer, NutritionalProfile
from src.core.services.recommendation_service import RecommendationService
from src.features.nutrition.recipe_optimizer import RecipeOptimizer

logger = logging.getLogger(__name__)


class ColorProfile:
    """Perfil de color para ingredientes y recetas."""
    
    # Mapeo de colores a sus ingredientes principales
    COLOR_INGREDIENTS = {
        "red": ["beetroot", "red bell pepper", "tomato", "red cabbage", "strawberry"],
        "orange": ["carrot", "pumpkin", "sweet potato", "orange bell pepper"],
        "yellow": ["corn", "yellow bell pepper", "turmeric", "saffron"],
        "green": ["spinach", "kale", "broccoli", "parsley", "basil", "avocado"],
        "purple": ["purple cabbage", "eggplant", "purple potato", "blackberry"],
        "black": ["activated charcoal", "black sesame seeds", "black beans", "black rice"],
        "white": ["cauliflower", "white beans", "coconut flour", "almond flour"]
    }
    
    # Intensidad de color por ingrediente (0-10)
    COLOR_INTENSITY = {
        "beetroot": 9,
        "turmeric": 8,
        "spinach": 7,
        "activated charcoal": 10,
        "pumpkin": 6,
        "purple cabbage": 8,
        "carrot": 7,
        "red cabbage": 7,
        "saffron": 9,
        "spirulina": 8
        # Más ingredientes pueden ser añadidos aquí
    }
    
    @classmethod
    def get_ingredients_for_color(cls, color: str) -> List[str]:
        """Obtiene ingredientes que proporcionan un color específico."""
        return cls.COLOR_INGREDIENTS.get(color.lower(), [])
    
    @classmethod
    def get_color_intensity(cls, ingredient: str) -> int:
        """Obtiene la intensidad de color de un ingrediente."""
        return cls.COLOR_INTENSITY.get(ingredient.lower(), 0)


class TextureProfile:
    """Perfil de textura para ingredientes y recetas."""
    
    # Mapeo de texturas a sus ingredientes principales
    TEXTURE_INGREDIENTS = {
        "elastic": ["psyllium husk", "xanthan gum", "vital wheat gluten", "eggs", "chickpea flour"],
        "crispy": ["cornstarch", "rice flour", "tapioca starch"],
        "chewy": ["oat flour", "vital wheat gluten", "potato starch"],
        "fluffy": ["potato flour", "tapioca flour", "baking powder"],
        "moist": ["apple puree", "banana", "yogurt", "pumpkin puree"]
    }
    
    # Efectividad de textura por ingrediente (0-10)
    TEXTURE_EFFECTIVENESS = {
        "psyllium husk": 9,
        "xanthan gum": 8,
        "vital wheat gluten": 10,
        "eggs": 7,
        "cornstarch": 6,
        "tapioca starch": 7,
        "potato starch": 6,
        "baking powder": 8,
        "yogurt": 7,
        "apple puree": 6
        # Más ingredientes pueden ser añadidos aquí
    }
    
    @classmethod
    def get_ingredients_for_texture(cls, texture: str) -> List[str]:
        """Obtiene ingredientes que proporcionan una textura específica."""
        return cls.TEXTURE_INGREDIENTS.get(texture.lower(), [])
    
    @classmethod
    def get_texture_effectiveness(cls, ingredient: str) -> int:
        """Obtiene la efectividad de textura de un ingrediente."""
        return cls.TEXTURE_EFFECTIVENESS.get(ingredient.lower(), 0)


class DietaryRestrictions:
    """Manejo de restricciones alimentarias."""
    
    # Ingredientes a evitar por tipo de restricción
    RESTRICTED_INGREDIENTS = {
        "gluten_free": ["wheat flour", "rye flour", "barley", "spelt", "farro", 
                    "semolina", "vital wheat gluten", "wheat starch", "wheat bran"],
        "dairy_free": ["milk", "cheese", "butter", "cream", "yogurt", "whey"],
        "egg_free": ["egg", "egg white", "egg yolk", "mayonnaise", "meringue"],
        "nut_free": ["almond", "walnut", "pecan", "cashew", "pistachio", "hazelnut", 
                 "almond flour", "almond milk", "peanut", "pine nut"],
        "vegan": ["egg", "milk", "cheese", "butter", "cream", "yogurt", "honey", 
               "gelatin", "whey", "casein", "meat", "fish"],
        "keto": ["wheat flour", "rice flour", "corn flour", "potato", "sugar", 
              "honey", "maple syrup", "banana", "dried fruit"],
        "low_fodmap": ["wheat", "onion", "garlic", "apple", "pear", "watermelon", 
                    "cauliflower", "mushroom", "honey"]
    }
    
    # Sustituciones comunes por restricción
    COMMON_SUBSTITUTIONS = {
        "gluten_free": {
            "wheat flour": ["rice flour", "almond flour", "chickpea flour", "buckwheat flour"],
            "vital wheat gluten": ["psyllium husk", "xanthan gum"]
        },
        "dairy_free": {
            "milk": ["almond milk", "oat milk", "soy milk", "coconut milk"],
            "butter": ["coconut oil", "olive oil", "vegan butter"]
        },
        "egg_free": {
            "egg": ["flax egg", "chia egg", "applesauce", "banana", "tofu"]
        },
        "vegan": {
            "egg": ["flax egg", "chia egg", "applesauce", "banana", "tofu"],
            "butter": ["coconut oil", "olive oil", "vegan butter"],
            "honey": ["maple syrup", "agave nectar"]
        }
    }
    
    @classmethod
    def get_restricted_ingredients(cls, restriction: str) -> List[str]:
        """Obtiene ingredientes restringidos para una dieta específica."""
        return cls.RESTRICTED_INGREDIENTS.get(restriction.lower(), [])
    
    @classmethod
    def get_substitutions(cls, restriction: str, ingredient: str) -> List[str]:
        """Obtiene sustituciones para un ingrediente bajo una restricción específica."""
        restriction_subs = cls.COMMON_SUBSTITUTIONS.get(restriction.lower(), {})
        return restriction_subs.get(ingredient.lower(), [])
    
    @classmethod
    def is_compliant(cls, ingredients: Dict[str, float], restrictions: List[str]) -> bool:
        """Verifica si una receta cumple con las restricciones especificadas."""
        for restriction in restrictions:
            restricted_items = cls.get_restricted_ingredients(restriction)
            for ingredient in ingredients:
                if any(restricted in ingredient.lower() for restricted in restricted_items):
                    return False
        return True


class AdvancedRecipeOptimizer(RecipeOptimizer):
    """
    Optimizador avanzado de recetas con soporte para características especiales.
    
    Extiende el optimizador básico con funcionalidades para:
    - Control de colores específicos
    - Texturas personalizadas
    - Restricciones alimentarias detalladas
    - Ajuste de peso/cantidad final
    """
    
    def __init__(
        self, 
        nutrition_analyzer: NutritionAnalyzer, 
        recommendation_service: RecommendationService
    ):
        """Inicializa el optimizador avanzado de recetas."""
        super().__init__(nutrition_analyzer, recommendation_service)
        self.color_profile = ColorProfile()
        self.texture_profile = TextureProfile()
        self.dietary_restrictions = DietaryRestrictions()
    
    def optimize_recipe_advanced(
        self,
        base_recipe: Dict[str, float],
        target_weight: Optional[float] = None,
        desired_color: Optional[str] = None,
        desired_texture: Optional[str] = None,
        dietary_restrictions: Optional[List[str]] = None,
        target_profile: Optional[NutritionalProfile] = None,
        recipe_type: str = "pizza",
        additional_constraints: Optional[Dict[str, any]] = None
    ) -> Tuple[Dict[str, float], List[Dict]]:
        """
        Optimiza una receta con características avanzadas.
        
        Args:
            base_recipe: Receta base a optimizar
            target_weight: Peso total deseado en gramos
            desired_color: Color deseado ("red", "green", etc.)
            desired_texture: Textura deseada ("elastic", "crispy", etc.)
            dietary_restrictions: Lista de restricciones ("gluten_free", "vegan", etc.)
            target_profile: Perfil nutricional objetivo
            recipe_type: Tipo de receta
            additional_constraints: Restricciones adicionales
            
        Returns:
            Receta optimizada y recomendaciones
        """
        recipe = base_recipe.copy()
        
        # Construir restricciones combinadas
        all_constraints = additional_constraints.copy() if additional_constraints else {}
        
        # Paso 1: Manejar restricciones alimentarias
        if dietary_restrictions:
            # Verificar si la receta base ya cumple con las restricciones
            for restriction in dietary_restrictions:
                restricted_ingredients = self.dietary_restrictions.get_restricted_ingredients(restriction)
                
                # Eliminar ingredientes restringidos
                for ingredient in list(recipe.keys()):
                    if any(restricted.lower() in ingredient.lower() for restricted in restricted_ingredients):
                        # Buscar sustitutos
                        substitutes = self.dietary_restrictions.get_substitutions(restriction, ingredient)
                        if substitutes:
                            # Añadir el primer sustituto con la misma cantidad
                            recipe[substitutes[0]] = recipe[ingredient]
                        # Eliminar el ingrediente restringido
                        del recipe[ingredient]
            
            # Añadir restricciones a las constraints para el optimizador base
            all_constraints["allergies"] = dietary_restrictions
        
        # Paso 2: Manejar color deseado
        if desired_color:
            color_ingredients = self.color_profile.get_ingredients_for_color(desired_color)
            
            # Verificar si ya hay ingredientes de color en la receta
            has_color_ingredient = any(ingredient in recipe for ingredient in color_ingredients)
            
            if not has_color_ingredient and color_ingredients:
                # Añadir ingrediente de color principal
                main_color_ingredient = color_ingredients[0]
                # Cantidad estándar inicial (ajustar según intensidad necesaria)
                recipe[main_color_ingredient] = 30.0  
            
            # Añadir preferencia de color a las constraints
            all_constraints["color_preference"] = desired_color
        
        # Paso 3: Manejar textura deseada
        if desired_texture:
            texture_ingredients = self.texture_profile.get_ingredients_for_texture(desired_texture)
            
            # Verificar si ya hay ingredientes de textura en la receta
            has_texture_ingredient = any(ingredient in recipe for ingredient in texture_ingredients)
            
            if not has_texture_ingredient and texture_ingredients:
                # Añadir ingrediente de textura principal
                main_texture_ingredient = texture_ingredients[0]
                # Cantidad estándar inicial
                if "gum" in main_texture_ingredient or "psyllium" in main_texture_ingredient:
                    recipe[main_texture_ingredient] = 5.0  # Cantidades pequeñas para gomas
                else:
                    recipe[main_texture_ingredient] = 20.0  # Cantidades mayores para otros
            
            # Añadir preferencia de textura a las constraints
            all_constraints["texture_preference"] = desired_texture
        
        # Paso 4: Optimizar con el optimizador base
        optimized_recipe, recommendations = super().optimize_recipe(
            recipe, target_profile, recipe_type, all_constraints
        )
        
        # Paso 5: Ajustar al peso objetivo si se especificó
        if target_weight is not None:
            current_weight = sum(optimized_recipe.values())
            if current_weight > 0:
                # Factor de ajuste para alcanzar el peso objetivo
                adjustment_factor = target_weight / current_weight
                
                # Ajustar todas las cantidades
                for ingredient in optimized_recipe:
                    optimized_recipe[ingredient] *= adjustment_factor
        
        return optimized_recipe, recommendations
    
    def create_recipe_from_description(
        self,
        description: str,
        recipe_type: str = "pizza",
        base_weight: float = 250.0
    ) -> Tuple[Dict[str, float], List[Dict]]:
        """
        Crea una receta a partir de una descripción en lenguaje natural.
        
        Args:
            description: Descripción de la receta deseada
            recipe_type: Tipo de receta
            base_weight: Peso base en gramos
            
        Returns:
            Receta optimizada y recomendaciones
        """
        # Analizar la descripción para extraer características
        color = self._extract_color(description)
        texture = self._extract_texture(description)
        restrictions = self._extract_restrictions(description)
        
        # Crear una receta base según el tipo
        if recipe_type == "pizza":
            base_recipe = self._get_base_pizza_recipe()
        elif recipe_type == "bread":
            base_recipe = self._get_base_bread_recipe()
        else:
            base_recipe = self._get_base_generic_recipe()
        
        # Aplicar restricciones básicas a la receta base
        if "gluten_free" in restrictions:
            # Reemplazar harinas con gluten por alternativas
            for ingredient in list(base_recipe.keys()):
                if "flour" in ingredient and ingredient not in ["rice flour", "chickpea flour", "almond flour"]:
                    del base_recipe[ingredient]
            
            # Añadir harinas sin gluten
            base_recipe["rice flour"] = 100.0
            base_recipe["tapioca starch"] = 25.0
            base_recipe["potato starch"] = 25.0
            
            # Añadir aglutinantes para mejorar textura
            base_recipe["psyllium husk"] = 10.0
            base_recipe["xanthan gum"] = 3.0
        
        # Optimizar la receta con las características extraídas
        return self.optimize_recipe_advanced(
            base_recipe=base_recipe,
            target_weight=base_weight,
            desired_color=color,
            desired_texture=texture,
            dietary_restrictions=restrictions,
            recipe_type=recipe_type
        )
    
    def _extract_color(self, description: str) -> Optional[str]:
        """Extrae información de color de una descripción."""
        description = description.lower()
        for color in self.color_profile.COLOR_INGREDIENTS.keys():
            if color in description:
                return color
                
        # Buscar asociaciones de ingredientes con colores
        for color, ingredients in self.color_profile.COLOR_INGREDIENTS.items():
            for ingredient in ingredients:
                if ingredient in description:
                    return color
                    
        return None
    
    def _extract_texture(self, description: str) -> Optional[str]:
        """Extrae información de textura de una descripción."""
        description = description.lower()
        texture_keywords = {
            "elastic": ["elástica", "elastic", "stretchy", "traditional", "tradicional"],
            "crispy": ["crispy", "crunchy", "crujiente", "thin"],
            "chewy": ["chewy", "masticable", "dense", "densa"],
            "fluffy": ["fluffy", "esponjosa", "soft", "blanda"],
            "moist": ["moist", "húmeda", "jugosa", "wet"]
        }
        
        for texture, keywords in texture_keywords.items():
            if any(keyword in description for keyword in keywords):
                return texture
                
        return "elastic"  # Textura por defecto para masas
    
    def _extract_restrictions(self, description: str) -> List[str]:
        """Extrae restricciones alimentarias de una descripción."""
        description = description.lower()
        restrictions = []
        
        restriction_keywords = {
            "gluten_free": ["gluten free", "sin gluten", "gluten-free", "free from gluten"],
            "dairy_free": ["dairy free", "sin lácteos", "lactose free", "sin lactosa"],
            "egg_free": ["egg free", "sin huevo", "no eggs", "sin huevos"],
            "vegan": ["vegan", "vegana", "plant based", "plant-based"],
            "keto": ["keto", "ketogenic", "low carb", "bajo en carbohidratos"],
            "low_fodmap": ["low fodmap", "fodmap", "bajo fodmap"]
        }
        
        for restriction, keywords in restriction_keywords.items():
            if any(keyword in description for keyword in keywords):
                restrictions.append(restriction)
                
        return restrictions
    
    def _get_base_pizza_recipe(self) -> Dict[str, float]:
        """Obtiene una receta base para pizza."""
        return {
            "wheat flour": 150.0,
            "water": 90.0,
            "olive oil": 15.0,
            "salt": 3.0,
            "yeast": 2.0
        }
    
    def _get_base_bread_recipe(self) -> Dict[str, float]:
        """Obtiene una receta base para pan."""
        return {
            "wheat flour": 200.0,
            "water": 120.0,
            "olive oil": 10.0,
            "salt": 4.0,
            "yeast": 3.0
        }
    
    def _get_base_generic_recipe(self) -> Dict[str, float]:
        """Obtiene una receta base genérica."""
        return {
            "wheat flour": 100.0,
            "water": 60.0,
            "olive oil": 10.0,
            "salt": 2.0,
            "yeast": 2.0
        } 