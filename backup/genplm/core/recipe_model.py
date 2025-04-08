"""
Modelo de datos para recetas y sus componentes.

Este módulo define las clases principales para modelar recetas de alimentos,
sus ingredientes y propiedades asociadas.
"""

from typing import List, Dict, Any, Optional
import json
import os


class Ingredient:
    """
    Representa un ingrediente en una receta.
    
    Un ingrediente tiene un nombre, una cantidad y propiedades 
    opcionales que describen sus características.
    """
    
    def __init__(self, name: str, amount: float, properties: Optional[Dict[str, Any]] = None):
        """
        Inicializa un nuevo ingrediente.
        
        Args:
            name: Nombre del ingrediente
            amount: Cantidad en gramos
            properties: Diccionario de propiedades adicionales (opcional)
        """
        self.name = name
        self.amount = amount
        self.properties = properties or {}
    
    def copy(self) -> 'Ingredient':
        """
        Crea una copia del ingrediente.
        
        Returns:
            Nueva instancia de Ingredient con los mismos datos
        """
        return Ingredient(
            name=self.name,
            amount=self.amount,
            properties={k: v for k, v in self.properties.items()}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el ingrediente a un diccionario.
        
        Returns:
            Diccionario que representa el ingrediente
        """
        return {
            "name": self.name,
            "amount": self.amount,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ingredient':
        """
        Crea un ingrediente a partir de un diccionario.
        
        Args:
            data: Diccionario con los datos del ingrediente
            
        Returns:
            Instancia de Ingredient
        """
        return cls(
            name=data["name"],
            amount=data["amount"],
            properties=data.get("properties", {})
        )
    
    def __str__(self) -> str:
        """
        Representación en cadena del ingrediente.
        
        Returns:
            Cadena con la información básica del ingrediente
        """
        return f"{self.name}: {self.amount:.2f}g"


class Recipe:
    """
    Representa una receta completa.
    
    Una receta tiene un nombre, una lista de ingredientes y propiedades
    opcionales que pueden incluir información como tiempo de preparación,
    nivel de dificultad, etc.
    """
    
    def __init__(self, name: str, properties: Optional[Dict[str, Any]] = None):
        """
        Inicializa una nueva receta.
        
        Args:
            name: Nombre de la receta
            properties: Diccionario de propiedades adicionales (opcional)
        """
        self.name = name
        self.ingredients: List[Ingredient] = []
        self.properties = properties or {}
    
    def add_ingredient(self, ingredient: Ingredient) -> None:
        """
        Añade un ingrediente a la receta.
        
        Args:
            ingredient: Ingrediente a añadir
        """
        self.ingredients.append(ingredient)
    
    def remove_ingredient(self, ingredient_name: str) -> bool:
        """
        Elimina un ingrediente de la receta por su nombre.
        
        Args:
            ingredient_name: Nombre del ingrediente a eliminar
            
        Returns:
            True si el ingrediente fue eliminado, False si no se encontró
        """
        for i, ingredient in enumerate(self.ingredients):
            if ingredient.name == ingredient_name:
                self.ingredients.pop(i)
                return True
        return False
    
    def get_ingredient(self, name: str) -> Optional[Ingredient]:
        """
        Obtiene un ingrediente por su nombre.
        
        Args:
            name: Nombre del ingrediente a buscar
            
        Returns:
            El objeto Ingredient si se encuentra, None en caso contrario
        """
        for ingredient in self.ingredients:
            if ingredient.name == name:
                return ingredient
        return None
    
    def update_ingredient_amount(self, name: str, amount: float) -> bool:
        """
        Actualiza la cantidad de un ingrediente existente.
        
        Args:
            name: Nombre del ingrediente
            amount: Nueva cantidad
            
        Returns:
            True si se actualizó, False si no se encontró el ingrediente
        """
        ingredient = self.get_ingredient(name)
        if ingredient:
            ingredient.amount = amount
            return True
        return False
    
    def get_total_weight(self) -> float:
        """
        Calcula el peso total de la receta.
        
        Returns:
            Suma de las cantidades de todos los ingredientes en gramos
        """
        return sum(ingredient.amount for ingredient in self.ingredients)
    
    def get_ingredient_percentage(self, name: str) -> float:
        """
        Calcula el porcentaje que representa un ingrediente respecto al total.
        
        Args:
            name: Nombre del ingrediente
            
        Returns:
            Porcentaje (0-100) del ingrediente respecto al peso total
        """
        ingredient = self.get_ingredient(name)
        if not ingredient:
            return 0.0
        
        total_weight = self.get_total_weight()
        if total_weight == 0:
            return 0.0
        
        return (ingredient.amount / total_weight) * 100
    
    def get_nutritional_summary(self) -> Dict[str, float]:
        """
        Calcula el resumen nutricional de la receta.
        
        Returns:
            Diccionario con los totales nutricionales
        """
        nutrition = {}
        
        for ingredient in self.ingredients:
            # Obtener valores nutricionales del ingrediente
            ingredient_nutrition = ingredient.properties.get("nutrition", {})
            
            # Sumar proporciones a los totales
            for nutrient, value in ingredient_nutrition.items():
                if nutrient in nutrition:
                    nutrition[nutrient] += value * ingredient.amount / 100  # value normalmente por 100g
                else:
                    nutrition[nutrient] = value * ingredient.amount / 100
        
        return nutrition
    
    def scale(self, factor: float) -> 'Recipe':
        """
        Crea una nueva receta escalando las cantidades por un factor.
        
        Args:
            factor: Factor de escala (por ejemplo, 2.0 duplica todas las cantidades)
            
        Returns:
            Nueva instancia de Recipe con cantidades escaladas
        """
        scaled_recipe = Recipe(name=f"{self.name} ({factor}x)", properties=self.properties.copy())
        
        for ingredient in self.ingredients:
            scaled_ingredient = ingredient.copy()
            scaled_ingredient.amount *= factor
            scaled_recipe.add_ingredient(scaled_ingredient)
        
        return scaled_recipe
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la receta a un diccionario.
        
        Returns:
            Diccionario que representa la receta
        """
        return {
            "name": self.name,
            "ingredients": [ing.to_dict() for ing in self.ingredients],
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recipe':
        """
        Crea una receta a partir de un diccionario.
        
        Args:
            data: Diccionario con los datos de la receta
            
        Returns:
            Instancia de Recipe
        """
        recipe = cls(
            name=data["name"],
            properties=data.get("properties", {})
        )
        
        for ing_data in data.get("ingredients", []):
            recipe.add_ingredient(Ingredient.from_dict(ing_data))
        
        return recipe
    
    def save_to_file(self, file_path: str) -> None:
        """
        Guarda la receta en un archivo JSON.
        
        Args:
            file_path: Ruta al archivo donde guardar la receta
        """
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Recipe':
        """
        Carga una receta desde un archivo JSON.
        
        Args:
            file_path: Ruta al archivo de la receta
            
        Returns:
            Instancia de Recipe con los datos cargados
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """
        Representación en cadena de la receta.
        
        Returns:
            Cadena con la información de la receta
        """
        ingredients_str = "\n".join([f"- {str(ing)}" for ing in self.ingredients])
        return f"Receta: {self.name}\n{ingredients_str}\nTotal: {self.get_total_weight():.2f}g" 