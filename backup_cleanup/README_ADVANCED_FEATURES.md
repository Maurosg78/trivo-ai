# Funcionalidades Avanzadas de Formulación para PizzaAI

Este módulo extiende la plataforma PizzaAI con capacidades avanzadas para interpretar descripciones en lenguaje natural y generar recetas personalizadas adaptadas a requisitos específicos de color, textura y restricciones alimentarias.

## Características Principales

### 1. Interpretación de Lenguaje Natural
- Extracción automática de características deseadas a partir de descripciones textuales
- Detección de colores, texturas y restricciones alimentarias
- Soporte para múltiples idiomas (incluye términos en español e inglés)

### 2. Generación de Recetas Personalizadas
- Creación de recetas a partir de descripciones como "pizza roja sin gluten" o "pan de calabaza para Halloween"
- Ajuste automático de pesos para obtener la cantidad deseada
- Optimización para mantener propiedades organolépticas similares a recetas tradicionales

### 3. Gestión Avanzada de Restricciones Alimentarias
- Soporte para múltiples dietas y restricciones: sin gluten, vegano, keto, etc.
- Sustitución automática de ingredientes restringidos
- Mantenimiento de propiedades funcionales al reemplazar ingredientes

### 4. Sistema de Colores y Texturas
- Base de datos de ingredientes categorizados por color
- Recomendaciones de ingredientes para lograr colores específicos
- Sistema para mantener texturas deseadas al cambiar ingredientes base

## Uso del Optimizador Avanzado

El optimizador avanzado permite crear recetas personalizadas mediante descripción textual o parámetros específicos.

### Método 1: Usando Descripción en Lenguaje Natural

```python
from src.core.services.usda_service import USDAService
from src.features.nutrition.nutrition_analyzer import NutritionAnalyzer
from src.core.services.recommendation_service import RecommendationService
from src.features.nutrition.recipe_optimizer_advanced import AdvancedRecipeOptimizer

# Inicializar servicios
usda_service = USDAService()
nutrition_analyzer = NutritionAnalyzer(usda_service)
recommendation_service = RecommendationService(usda_service)
optimizer = AdvancedRecipeOptimizer(nutrition_analyzer, recommendation_service)

# Crear receta a partir de descripción
description = "250 gramos de masa de pizza sin gluten de color rojo"
recipe, recommendations = optimizer.create_recipe_from_description(
    description=description,
    recipe_type="pizza",
    base_weight=250.0
)
```

### Método 2: Usando Parámetros Específicos

```python
# Receta base sin gluten
base_recipe = {
    "rice flour": 100.0,
    "tapioca starch": 25.0,
    "potato starch": 25.0,
    "psyllium husk": 10.0,
    "xanthan gum": 3.0,
    "olive oil": 15.0,
    "salt": 3.0,
    "yeast": 2.0
}

# Optimizar la receta con parámetros específicos
recipe, recommendations = optimizer.optimize_recipe_advanced(
    base_recipe=base_recipe,
    target_weight=250.0,
    desired_color="red",
    desired_texture="elastic",
    dietary_restrictions=["gluten_free"],
    recipe_type="pizza"
)
```

## Colores Disponibles

El sistema soporta los siguientes colores y sus ingredientes asociados:

| Color  | Ingredientes Principales |
|--------|--------------------------|
| Rojo   | Remolacha, pimiento rojo, tomate, col roja, fresa |
| Naranja | Zanahoria, calabaza, batata, pimiento naranja |
| Amarillo | Maíz, pimiento amarillo, cúrcuma, azafrán |
| Verde  | Espinaca, kale, brócoli, perejil, albahaca, aguacate |
| Púrpura | Col morada, berenjena, patata morada, mora |
| Negro  | Carbón activado, semillas de sésamo negro, frijoles negros, arroz negro |
| Blanco | Coliflor, judías blancas, harina de coco, harina de almendra |

## Texturas Disponibles

El sistema puede adaptar recetas para lograr las siguientes texturas:

| Textura | Ingredientes Clave |
|---------|-------------------|
| Elástica | Psyllium, goma xantana, gluten vital, huevos, harina de garbanzo |
| Crujiente | Almidón de maíz, harina de arroz, almidón de tapioca |
| Masticable | Harina de avena, gluten vital, almidón de patata |
| Esponjosa | Harina de patata, harina de tapioca, levadura química |
| Húmeda | Puré de manzana, plátano, yogur, puré de calabaza |

## Restricciones Alimentarias Soportadas

El sistema detecta automáticamente las siguientes restricciones alimentarias:

- `gluten_free`: Sin gluten
- `dairy_free`: Sin lácteos
- `egg_free`: Sin huevo
- `nut_free`: Sin frutos secos
- `vegan`: Vegano
- `keto`: Ketogénico (bajo en carbohidratos)
- `low_fodmap`: Bajo en FODMAPs

## Demo Interactiva

Para probar el sistema de forma interactiva, ejecute:

```bash
# Demostración de pizza sin gluten roja
python demo_advanced_recipe_optimizer.py --demo pizza

# Demostración de pan de calabaza para Halloween
python demo_advanced_recipe_optimizer.py --demo halloween

# Crear una receta personalizada
python demo_advanced_recipe_optimizer.py --demo custom
```

## Integración con Otros Módulos

Este sistema avanzado integra perfectamente con:

- Sistema de análisis nutricional para optimizar perfiles nutricionales
- Motor de recomendaciones para sugerir ingredientes adicionales
- Optimizador básico de recetas como capa subyacente

## Próximas Mejoras

- Soporte para más idiomas en la interpretación de lenguaje natural
- Sistema de aprendizaje automático para mejorar la interpretación de descripciones
- Más colores y efectos visuales (marmoleado, degradado, etc.)
- Expansión de la base de datos de ingredientes para colores 