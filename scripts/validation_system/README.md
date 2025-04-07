# Sistema de Validación Crítica para PizzaAI

Este sistema implementa un conjunto de validaciones críticas y medias para garantizar la viabilidad técnica y científica de las recetas de pizza y productos de panadería en diferentes escalas de producción.

## Características

- Validación exhaustiva de recetas basada en reglas científicas y técnicas
- Soporte para diferentes escalas de producción: individual, pequeño negocio e industrial
- Detección de errores críticos y advertencias medias
- Recomendaciones específicas para resolver problemas
- Verificación de compatibilidad de ingredientes
- Validación de parámetros técnicos para escala industrial

## Componentes

El sistema consta de los siguientes componentes:

- **validation_system.py**: Módulo principal con la lógica de validación
- **validation_rules.json**: Reglas de validación críticas y medias
- **ingredient_limits.json**: Límites y propiedades de los ingredientes
- **process_parameters.json**: Parámetros de proceso para cada escala
- **check_system.py**: Script para verificar la integridad del sistema
- **example_recipe.json**: Receta de ejemplo para probar el sistema

## Uso

### Validación de recetas

```bash
python validation_system.py <archivo_receta.json> --scale [individual|small_business|industrial] [--output resultado.json]
```

Ejemplo:
```bash
python validation_system.py example_recipe.json --scale industrial
```

### Verificación del sistema

Para comprobar que todos los componentes están presentes y funcionando correctamente:

```bash
python check_system.py [--output verificacion.json]
```

## Escalas de Producción

El sistema soporta tres escalas de producción, cada una con diferentes requisitos y tolerancias:

1. **Individual**: Para uso doméstico o familiar (hasta 2 kg)
   - Mayor tolerancia en parámetros
   - Menos requisitos de equipamiento

2. **Pequeño Negocio**: Para pequeños negocios o artesanos (2-20 kg)
   - Tolerancia media en parámetros
   - Requisitos básicos de equipamiento profesional

3. **Industrial**: Para producción a escala industrial (20-500 kg)
   - Tolerancia muy estricta en parámetros
   - Requisitos específicos de equipamiento industrial
   - Controles de calidad obligatorios

## Matriz de Validación

| Categoría | Reglas Individuales | Pequeño Negocio | Industrial |
|-----------|---------------------|-----------------|------------|
| Hidratación | 45-75% (±5%) | 45-75% (±3%) | 45-75% (±1%) |
| Sal | 1.0-2.5% (±0.5%) | 1.0-2.5% (±0.3%) | 1.0-2.5% (±0.1%) |
| Temperatura | 22-28°C (±3°C) | 23-26°C (±2°C) | 22-25°C (±1°C) |
| Equipamiento | Básico | Profesional | Industrial completo |
| Control Calidad | No requerido | Recomendado | Obligatorio |

## Estructura de las Recetas

Para obtener los mejores resultados de validación, las recetas deben seguir una estructura específica:

```json
{
  "id": "id_unico_receta",
  "name": "Nombre de la Receta",
  "type": "pizza|bread|gluten_free|vegetable_base",
  "scale": "individual|small_business|industrial",
  "batch_size": 100,
  "ingredients": {
    "flour": {
      "type": "wheat_flour",
      "quantity": 100,
      "unit": "kg"
    },
    "water": {
      "quantity": 65,
      "unit": "kg"
    },
    // Otros ingredientes...
  },
  "process": {
    // Parámetros del proceso...
  },
  "technical_specs": {
    // Especificaciones técnicas para escala industrial...
  }
}
```

## Errores y Recomendaciones

El sistema genera dos tipos de errores:

- **CRITICAL**: Errores que impiden la viabilidad de la receta y deben corregirse.
- **MEDIUM**: Advertencias que podrían afectar la calidad pero no impiden la ejecución.

Cada error incluye:
- Código único
- Descripción del problema
- Parámetros afectados
- Recomendación para la solución 