# Funcionalidades de Vegetales para PizzaAI

Este módulo añade soporte completo para la creación y optimización de recetas con base de vegetales en la plataforma PizzaAI.

## Características Principales

### 1. Análisis Nutricional para Vegetales
- Cálculo de perfiles nutricionales para ingredientes vegetales
- Determinación del índice glucémico para formulaciones
- Optimización nutricional específica para recetas con vegetales

### 2. Sistema de Recomendaciones para Vegetales
- Recomendaciones basadas en tipo de receta (pizza, pan, etc.)
- Sugerencias adaptadas a restricciones dietéticas (bajo carbohidrato, alergias)
- Consejos de uso específicos para cada vegetal

### 3. Optimizador de Recetas
- Integración del análisis nutricional y el sistema de recomendaciones
- Ajuste automático de ingredientes para alcanzar objetivos nutricionales
- Visualización comparativa de perfiles nutricionales

## Uso del Optimizador de Recetas

El optimizador de recetas permite transformar una formulación inicial en una versión nutricionalmente optimizada.

```python
from src.core.services.usda_service import USDAService
from src.features.nutrition.nutrition_analyzer import NutritionAnalyzer, NutritionalProfile
from src.core.services.recommendation_service import RecommendationService
from src.features.nutrition.recipe_optimizer import RecipeOptimizer

# Inicializar servicios
usda_service = USDAService()
nutrition_analyzer = NutritionAnalyzer(usda_service)
recommendation_service = RecommendationService(usda_service)
recipe_optimizer = RecipeOptimizer(nutrition_analyzer, recommendation_service)

# Definir receta inicial
initial_recipe = {
    "cauliflower": 200.0,
    "rice flour": 100.0,
    "egg": 50.0,
    "olive oil": 15.0,
    "salt": 5.0
}

# Definir perfil nutricional objetivo (opcional)
target_profile = NutritionalProfile(
    macronutrients={"protein": 15.0, "fat": 7.0, "carbohydrates": 25.0},
    micronutrients={},
    fiber=10.0,
    calories=230.0,
    glycemic_index=45.0
)

# Optimizar receta
optimized_recipe, recommendations = recipe_optimizer.optimize_recipe(
    initial_recipe, 
    target_profile=target_profile,
    recipe_type="pizza",
    constraints={"low_carb": True}
)

# Visualizar datos nutricionales
visualization_data = recipe_optimizer.visualize_nutritional_profile(
    optimized_recipe, target_profile=target_profile
)
```

## Lista de Vegetales Soportados

El sistema incluye datos específicos para los siguientes vegetales:

| Vegetal      | Propiedades Principales              | Ratio de Sustitución |
|--------------|--------------------------------------|----------------------|
| Coliflor     | Bajo índice glucémico, alta humedad  | 0.7:1                |
| Calabacín    | Muy alta humedad, sabor suave        | 0.25:1               |
| Remolacha    | Color intenso, sabor terroso         | 0.3:1                |
| Zanahoria    | Dulzor natural, color atractivo      | 0.3:1                |
| Batata       | Buen contenido de almidón, elasticidad| 0.5:1               |
| Garbanzo     | Alto contenido proteico, buena unión | 1:1                  |
| Lentejas     | Alta proteína, buena textura         | 0.8:1                |

## Ejecución de Pruebas

Para ejecutar las pruebas unitarias del módulo:

```bash
# Pruebas del analizador nutricional
python -m pytest tests/features/test_vegetable_analyzer.py -v

# Pruebas del sistema de recomendaciones
python -m pytest tests/features/recommendations/test_vegetable_recommendations.py -v

# Pruebas del optimizador de recetas
python -m pytest tests/features/test_recipe_optimizer.py -v
```

## Demo

Para ver una demostración de las capacidades del optimizador, ejecute:

```bash
python demo_recipe_optimizer.py
```

Este script muestra dos ejemplos prácticos:
1. Optimización de una pizza con base de coliflor
2. Optimización de un pan con vegetales variados

## Próximas Mejoras

- Integración con sistemas de análisis sensorial
- Mejora de la visualización con gráficos interactivos
- Expansión del catálogo de vegetales soportados
- Personalización basada en preferencias de usuario 