# Plan de Desarrollo MVP TRIVO-AI

## Visión General del MVP

El MVP de TRIVO-AI se centrará en la optimización de costos para formulaciones de masa, manteniendo las propiedades físicas deseadas. Este MVP demostrará el valor central de la plataforma: reducir costos de ingredientes sin sacrificar calidad.

### Objetivos del MVP

1. Permitir a usuarios ingresar una receta existente
2. Optimizar la receta para reducir costos
3. Validar que la receta optimizada mantenga propiedades físicas esenciales
4. Mostrar el ahorro estimado y las diferencias entre recetas
5. Exportar la receta optimizada en formato utilizable

## Plan de Sprints

Duración total: 6 semanas (3 sprints de 2 semanas)

### Sprint 1: Fundamentos y Algoritmo Base (Semanas 1-2)

#### Objetivos del Sprint
- Establecer arquitectura básica del sistema
- Implementar algoritmo de optimización por costos
- Crear base de datos de ingredientes con costos

#### Issues

| ID | Título | Descripción | Prioridad | Asignado a | Puntos |
|----|--------|-------------|-----------|------------|--------|
| S1-01 | Arquitectura del MVP | Definir componentes, flujo de datos y tecnologías | Alta | - | 5 |
| S1-02 | Modelo de datos de ingredientes | Esquema con nombre, costo, propiedades físicas | Alta | - | 3 |
| S1-03 | Importar base de datos inicial | Poblar DB con 40-50 ingredientes comunes y precios | Media | - | 5 |
| S1-04 | API básica de ingredientes | Endpoints para consultar ingredientes y precios | Media | - | 3 |
| S1-05 | Algoritmo de optimización: Estructura | Framework para algoritmo genético de optimización | Alta | - | 8 |
| S1-06 | Función objetivo: Costo | Implementar función para minimizar costo total | Alta | - | 5 |
| S1-07 | Restricciones básicas | Implementar restricciones para mantener propiedades clave | Alta | - | 8 |
| S1-08 | Pruebas unitarias - Optimización | Verificar resultados con casos de prueba conocidos | Media | - | 5 |

### Sprint 2: Validación y API (Semanas 3-4)

#### Objetivos del Sprint
- Implementar sistema de validación de propiedades
- Crear API completa para optimización
- Desarrollar componentes iniciales de UI

#### Issues

| ID | Título | Descripción | Prioridad | Asignado a | Puntos |
|----|--------|-------------|-----------|------------|--------|
| S2-01 | Sistema de validación física | Verificación de hidratación, fermentación y elasticidad | Alta | - | 8 |
| S2-02 | API de optimización | Endpoint para optimizar recetas con parámetros configurables | Alta | - | 5 |
| S2-03 | API de validación | Endpoint para validar recetas contra reglas técnicas | Alta | - | 5 |
| S2-04 | Autenticación básica | Sistema simple de registro y login | Baja | - | 5 |
| S2-05 | Frontend: Formulario de receta | UI para ingresar y editar recetas | Media | - | 5 |
| S2-06 | Frontend: Visualización comparativa | UI para mostrar receta original vs optimizada | Media | - | 8 |
| S2-07 | Cálculo de ahorro | Lógica para calcular y mostrar ahorro total y porcentual | Alta | - | 3 |
| S2-08 | Exportación básica | Generar PDF/CSV con receta optimizada | Baja | - | 5 |

### Sprint 3: UI, Pruebas y Preparación para Lanzamiento (Semanas 5-6)

#### Objetivos del Sprint
- Completar la interfaz de usuario
- Realizar pruebas con casos reales
- Preparar el sistema para demostración a primeros usuarios

#### Issues

| ID | Título | Descripción | Prioridad | Asignado a | Puntos |
|----|--------|-------------|-----------|------------|--------|
| S3-01 | UI completa | Interfaz completa con todas las funcionalidades integradas | Alta | - | 13 |
| S3-02 | Dashboard de ahorros | Visualización de métricas de ahorro y ROI | Media | - | 5 |
| S3-03 | Pruebas con 10 recetas reales | Validar resultados con recetas de panaderías reales | Alta | - | 8 |
| S3-04 | Ajuste fino de algoritmos | Calibrar en base a resultados de pruebas reales | Alta | - | 8 |
| S3-05 | Documentación de usuario | Guías básicas de uso para primeros usuarios | Media | - | 5 |
| S3-06 | Sistema de feedback | Mecanismo para recopilar comentarios de usuarios | Baja | - | 3 |
| S3-07 | Despliegue en entorno demo | Preparar entorno para demostraciones a inversores | Alta | - | 5 |
| S3-08 | Seguridad básica | Revisión de seguridad para datos sensibles | Media | - | 5 |

## Estructura del Tablero Kanban

```
+----------------+----------------+----------------+----------------+----------------+
|    BACKLOG     |     TODO       |  IN PROGRESS   |   REVIEW       |     DONE       |
+----------------+----------------+----------------+----------------+----------------+
|                |                |                |                |                |
|  Issues futuras| Issues del     | Issues en      | Esperando      | Issues         |
|  y pendientes  | sprint actual  | desarrollo     | revisión/testing| completadas    |
|                |                |                |                |                |
|                |                |                |                |                |
|                |                |                |                |                |
+----------------+----------------+----------------+----------------+----------------+
```

## Métricas de Éxito del MVP

1. **Métricas Técnicas**:
   - Tiempo de optimización < 30 segundos
   - Reducción de costo promedio > 5%
   - 100% de recetas optimizadas mantienen propiedades clave

2. **Métricas de Usuario**:
   - > 80% de usuarios logran optimizar su primera receta en < 10 minutos
   - NPS (Net Promoter Score) > 30 en primeras pruebas
   - > 50% de usuarios reportan intención de usar regularmente

3. **Métricas de Negocio**:
   - Al menos 5 casos de éxito documentados con ahorro real medido
   - Al menos 3 testimonios de usuarios para marketing
   - Base para presentación a inversores completada

## Integración con Codebase Existente

Para aprovechar el código actual de TRIVO-AI, nos enfocaremos en:

1. **Reutilización de componentes**:
   - Sistema de validación existente (ajustar para enfoque en costos)
   - Modelos de datos de recetas e ingredientes
   - Base de conocimiento sobre propiedades físicas

2. **Refactorización necesaria**:
   - Simplificar interfaz de usuario para MVP
   - Reorientar algoritmos de optimización hacia costos
   - Conectar con base de datos de precios

3. **Nuevos desarrollos**:
   - Dashboard comparativo
   - Exportación de recetas
   - API simplificada

## Plan Post-MVP

Tras la validación del MVP con usuarios reales y potenciales inversores, se expandirá en tres direcciones principales:

1. **Ampliación de funcionalidades**:
   - Más tipos de masas y productos
   - Optimización multi-objetivo (costo, nutrición, propiedades)
   - Recomendaciones inteligentes

2. **Mejora técnica**:
   - Algoritmos más sofisticados y rápidos
   - Integración con proveedores de ingredientes
   - API completa para integración con otros sistemas

3. **Expansión comercial**:
   - Lanzamiento oficial de planes de suscripción
   - Marketplace de recetas
   - Servicios de consultoría especializados 