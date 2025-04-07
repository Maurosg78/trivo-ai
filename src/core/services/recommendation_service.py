import logging
from typing import Dict, List

from src.core.services.usda_service import USDAService

logger = logging.getLogger(__name__)


class RecommendationService:
    """Servicio para generar recomendaciones de ingredientes."""

    def __init__(self, usda_service: USDAService):
        """Inicializa el servicio con las dependencias necesarias."""
        self.usda_service = usda_service
        self._cache = {}  # Cache simple en memoria para pruebas
        # Base de datos de vegetales y sus propiedades para masas
        self.vegetable_properties = {
            "cauliflower": {
                "water_content": 92,  # % de agua
                "starch": 1,          # % de almidón
                "binding": "low",     # Capacidad de unión
                "texture": "crumbly", # Textura que aporta
                "flavor": "mild",     # Sabor
                "color": "white"      # Color
            },
            "sweet potato": {
                "water_content": 77,
                "starch": 12,
                "binding": "medium",
                "texture": "elastic",
                "flavor": "sweet",
                "color": "orange"
            },
            "beetroot": {
                "water_content": 88,
                "starch": 1.5,
                "binding": "medium",
                "texture": "moist",
                "flavor": "earthy",
                "color": "red"
            },
            "zucchini": {
                "water_content": 95,
                "starch": 1,
                "binding": "low",
                "texture": "moist",
                "flavor": "mild",
                "color": "green"
            },
            "carrot": {
                "water_content": 88,
                "starch": 1,
                "binding": "low",
                "texture": "moist",
                "flavor": "sweet",
                "color": "orange"
            },
            "chickpea": {
                "water_content": 60,
                "starch": 22,
                "binding": "high",
                "texture": "dense",
                "flavor": "nutty",
                "color": "beige"
            },
            "lentils": {
                "water_content": 70,
                "starch": 20,
                "binding": "high",
                "texture": "dense",
                "flavor": "earthy",
                "color": "brown"
            }
        }

    def get_recommendations(self, base_ingredient: str, limit: int = 5) -> List[Dict]:
        """
        Genera recomendaciones basadas en un ingrediente base.

        Args:
            base_ingredient: Nombre del ingrediente base
            limit: Número máximo de recomendaciones

        Returns:
            Lista de ingredientes recomendados
        """
        # Obtener datos del ingrediente base
        base_data = self.usda_service.get_food_nutrition(base_ingredient)
        if not base_data:
            return []

        # Buscar ingredientes similares
        similar_foods = self.usda_service.search_foods(base_ingredient, page_size=limit + 1)

        # Filtrar el ingrediente base y limitar resultados
        recommendations = [
            food for food in similar_foods if str(food["fdcId"]) != str(base_data.get("fdcId"))
        ][:limit]

        # Enriquecer con detalles nutricionales
        return [self._enrich_recommendation(food) for food in recommendations]

    def get_vegetable_recommendations(self, recipe_type: str, desired_properties: Dict[str, str] = None, limit: int = 5) -> List[Dict]:
        """
        Genera recomendaciones de vegetales basadas en el tipo de receta y propiedades deseadas.
        
        Args:
            recipe_type: Tipo de receta (e.g., 'pizza', 'bread', 'pasta')
            desired_properties: Propiedades deseadas (e.g., {'texture': 'elastic', 'flavor': 'mild'})
            limit: Número máximo de recomendaciones
            
        Returns:
            Lista de vegetales recomendados con sus propiedades
        """
        if desired_properties is None:
            desired_properties = {}
            
        scored_vegetables = []
        
        for veggie_name, properties in self.vegetable_properties.items():
            # Calcular puntuación basada en propiedades
            score = self._calculate_vegetable_score(properties, desired_properties, recipe_type)
            
            # Preparar recomendación
            recommendation = {
                "name": veggie_name,
                "score": score,
                "properties": properties,
                "usage_tips": self._get_usage_tips(veggie_name, recipe_type),
                "substitution_ratio": self._get_substitution_ratio(veggie_name)
            }
            
            scored_vegetables.append(recommendation)
        
        # Ordenar por puntuación y limitar resultados
        scored_vegetables.sort(key=lambda x: x["score"], reverse=True)
        return scored_vegetables[:limit]
    
    def _calculate_vegetable_score(self, properties: Dict, desired_properties: Dict, recipe_type: str) -> float:
        """Calcula la puntuación de un vegetal basado en sus propiedades y el tipo de receta."""
        score = 0.0
        
        # Puntuar basado en propiedades deseadas
        for prop, desired_value in desired_properties.items():
            if prop in properties:
                # Para propiedades numéricas
                if isinstance(properties[prop], (int, float)) and isinstance(desired_value, (int, float)):
                    # Mayor cercanía, mayor puntuación
                    proximity = 1 - min(abs(properties[prop] - desired_value) / max(properties[prop], desired_value), 1)
                    score += proximity * 2  # Peso mayor para coincidencias exactas
                # Para propiedades categóricas
                elif properties[prop] == desired_value:
                    score += 2
                elif prop == "texture" and properties[prop] != desired_value:
                    # Penalización mayor para texturas incompatibles
                    score -= 1
        
        # Ajustes según tipo de receta
        if recipe_type == "pizza":
            # Para pizza, preferimos vegetales con menor contenido de agua
            score += (100 - properties["water_content"]) / 20  # Máximo 5 puntos
            # Y mayor capacidad de unión
            binding_scores = {"low": 1, "medium": 2, "high": 3}
            score += binding_scores.get(properties["binding"], 0)
        elif recipe_type == "bread":
            # Para pan, valoramos el almidón
            score += properties["starch"] / 5  # Máximo 5 puntos para 25% de almidón
            # Y textura elástica
            if properties["texture"] == "elastic":
                score += 2
            
        return max(score, 0)  # Asegurar que el score no sea negativo
    
    def _get_usage_tips(self, vegetable: str, recipe_type: str) -> List[str]:
        """Obtiene consejos de uso para el vegetal en el tipo de receta específico."""
        tips = []
        properties = self.vegetable_properties.get(vegetable, {})
        
        # Consejos generales
        if properties.get("water_content", 0) > 90:
            tips.append("Pre-cocinar y escurrir bien para reducir exceso de humedad")
        
        # Consejos específicos por vegetal
        if vegetable == "cauliflower":
            tips.append("Pulverizar finamente y hornear brevemente antes de usar en la masa")
            if recipe_type == "pizza":
                tips.append("Mezclar con queso para mejor cohesión de la masa")
        elif vegetable == "sweet potato":
            tips.append("Hornear o cocer al vapor antes de incorporar a la masa")
            tips.append("Combina bien con especias como canela o nuez moscada")
        elif vegetable == "beetroot":
            tips.append("Proporciona un color intenso, dosificar según el resultado deseado")
            tips.append("Combinar con cítricos para equilibrar el sabor terroso")
        elif vegetable == "zucchini":
            tips.append("Rallar y exprimir bien para eliminar exceso de agua")
            tips.append("Mezclar con harinas con mayor poder de absorción")
        elif vegetable == "chickpea":
            tips.append("Moler finamente para obtener harina de garbanzo casera")
            tips.append("Excelente para aumentar el contenido proteico")
            
        # Consejos específicos por tipo de receta
        if recipe_type == "pizza":
            tips.append("Combinar con harinas con gluten para mejor elasticidad")
        elif recipe_type == "bread":
            tips.append("Aumentar el tiempo de fermentación para mejor desarrollo de sabor")
            
        return tips
    
    def _get_substitution_ratio(self, vegetable: str) -> Dict[str, float]:
        """Obtiene la ratio de sustitución para un vegetal respecto a la harina tradicional."""
        substitution_ratios = {
            "cauliflower": {"flour": 0.7},  # 70g de coliflor por 100g de harina
            "sweet potato": {"flour": 0.5},
            "beetroot": {"flour": 0.3},
            "zucchini": {"flour": 0.25},
            "carrot": {"flour": 0.3},
            "chickpea": {"flour": 1.0},  # La harina de garbanzo puede sustituir 1:1
            "lentils": {"flour": 0.8}
        }
        
        return substitution_ratios.get(vegetable, {"flour": 0.5})

    def _enrich_recommendation(self, food: Dict) -> Dict:
        """Enriquece una recomendación con datos nutricionales."""
        details = self.usda_service.get_food_details(str(food["fdcId"]))

        return {
            "id": food["fdcId"],
            "name": food["description"],
            "score": self._calculate_similarity_score(details),
            "nutrients": self._extract_key_nutrients(details),
        }

    def _calculate_similarity_score(self, food_details: Dict) -> float:
        """Calcula un puntaje de similitud basado en nutrientes."""
        nutrients = food_details.get("foodNutrients", [])
        if not nutrients:
            return 0.0

        # Puntaje basado en presencia de nutrientes clave
        score = 0.0
        total_nutrients = len(nutrients)

        for nutrient in nutrients:
            if nutrient.get("nutrientName", "").lower() in {
                "protein",
                "total lipid (fat)",
                "carbohydrate",
                "fiber",
                "calcium",
                "iron",
                "magnesium",
                "phosphorus",
                "potassium",
                "sodium",
                "zinc",
                "vitamin c",
                "vitamin b6",
                "vitamin b12",
            }:
                score += 1

        return score / max(total_nutrients, 1) * 10

    def _extract_key_nutrients(self, food_details: Dict) -> Dict[str, float]:
        """Extrae los nutrientes clave de los detalles del alimento."""
        nutrients = {}
        for nutrient in food_details.get("foodNutrients", []):
            name = nutrient.get("nutrientName", "").lower()
            if name in {
                "protein",
                "total lipid (fat)",
                "carbohydrate",
                "fiber",
                "calcium",
                "iron",
                "magnesium",
                "potassium",
                "sodium",
            }:
                nutrients[name] = nutrient.get("value", 0.0)

        return nutrients

    def get_nutritional_comparison(self, ingredient1: str, ingredient2: str) -> Dict:
        """Compara el perfil nutricional de dos ingredientes."""
        try:
            # Verificar cache
            cache_key = f"comp:{ingredient1}:{ingredient2}"
            if cache_key in self._cache:
                logger.info(f"Usando comparación en caché para: {ingredient1} y {ingredient2}")
                return self._cache[cache_key]

            # Obtener detalles de ambos ingredientes
            search1 = self.usda_service.search_foods(ingredient1, page_size=1)
            search2 = self.usda_service.search_foods(ingredient2, page_size=1)

            if not search1.get("foods") or not search2.get("foods"):
                return {}

            details1 = self.usda_service.get_food_details(search1["foods"][0]["fdcId"])
            details2 = self.usda_service.get_food_details(search2["foods"][0]["fdcId"])

            # Comparar nutrientes clave
            key_nutrients = {
                "Protein": "Proteína",
                "Total lipid (fat)": "Grasa total",
                "Carbohydrate, by difference": "Carbohidratos",
                "Energy": "Calorías",
                "Fiber, total dietary": "Fibra",
                "Sodium, Na": "Sodio",
            }

            comparison = {}
            for nutrient_id, nutrient_name in key_nutrients.items():
                value1 = next(
                    (
                        n.get("amount", 0)
                        for n in details1.get("foodNutrients", [])
                        if n.get("nutrient", {}).get("name") == nutrient_id
                    ),
                    0,
                )
                value2 = next(
                    (
                        n.get("amount", 0)
                        for n in details2.get("foodNutrients", [])
                        if n.get("nutrient", {}).get("name") == nutrient_id
                    ),
                    0,
                )

                comparison[nutrient_name] = {
                    "ingredient1": value1,
                    "ingredient2": value2,
                    "difference": value2 - value1,
                }

            # Almacenar en caché
            self._cache[cache_key] = comparison

            return comparison

        except Exception as e:
            logger.error(f"Error al comparar ingredientes: {str(e)}")
            return {}
