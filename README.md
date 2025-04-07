# TRIVO-AI

Sistema inteligente para formulación y validación de recetas de masas.

## Descripción

TRIVO-AI es un sistema avanzado que utiliza algoritmos genéticos e inteligencia artificial para optimizar recetas de pizza y otros productos a base de masa. El sistema permite:

- Crear recetas óptimas según parámetros específicos
- Validar recetas existentes según estándares industriales
- Adaptar recetas a diferentes escalas de producción
- Procesar peticiones en lenguaje natural para interpretar requisitos de recetas

## Características principales

- **Algoritmo genético** para optimización de recetas
- **Sistema de validación crítica** para garantizar viabilidad industrial
- **Procesador de lenguaje natural** para interpretar requisitos en texto libre
- **Interfaz web** intuitiva y moderna
- **API RESTful** para integración con otros sistemas

## Estructura del proyecto

```
TRIVO-AI/
├── app/                    # Aplicación web
│   ├── templates/          # Plantillas HTML
│   ├── static/             # Archivos estáticos (CSS, JS)
│   └── app.py              # Servidor web Flask
├── data/                   # Datos y recetas de ejemplo
├── models/                 # Modelos entrenados
├── notebooks/              # Jupyter notebooks para prototipado
├── reports/                # Informes y resultados de validación
├── src/                    # Código fuente principal
│   ├── data/               # Procesamiento de datos
│   ├── features/           # Características y funcionalidades
│   │   ├── genetic/        # Algoritmo genético
│   │   ├── nlp/            # Procesamiento de lenguaje natural
│   │   └── validation/     # Sistema de validación
│   ├── models/             # Implementación de modelos
│   └── visualization/      # Visualización de datos y resultados
├── scripts/                # Scripts de utilidad
│   └── validation_system/  # Scripts para validación independiente
├── tests/                  # Pruebas automatizadas
├── .env                    # Variables de entorno
├── requirements.txt        # Dependencias
└── README.md               # Este archivo
```

## Sistema de Validación (Sprint 4)

El Sistema de Validación implementado en el Sprint 4 permite verificar que las recetas cumplen con los estándares industriales y son viables para su producción. El sistema incluye:

### Reglas de Validación

- **Ratio de hidratación**: Verifica que la proporción de líquidos respecto a la harina sea adecuada según el tipo de masa.
- **Proporción de sal**: Asegura que la cantidad de sal está dentro de los límites aceptables.
- **Proporción de levadura**: Valida que la cantidad de levadura sea correcta según el tipo de masa y escala.
- **Ingredientes esenciales**: Confirma que las masas especiales incluyen todos los ingredientes necesarios.
- **Límites de escala**: Verifica que los volúmenes son adecuados para la escala de producción.
- **Parámetros de fermentación**: Comprueba que los tiempos y temperaturas de fermentación son adecuados para el tipo de masa.

### Niveles de Severidad

- **Crítico**: Problemas que hacen la receta inviable para producción.
- **Medio**: Problemas importantes que pueden afectar la calidad del producto.
- **Bajo**: Sugerencias para mejorar la receta.

### Uso desde línea de comandos

```bash
# Verificar la integridad del sistema
python run_validation.py check

# Crear una receta de ejemplo
python run_validation.py sample --recipe-type pizza --production-scale small_business

# Validar una receta
python run_validation.py validate path/to/recipe.json --production-scale industrial
```

### Integración con la interfaz web

El sistema de validación está completamente integrado con la interfaz web, permitiendo a los usuarios:

- Validar recetas subiendo archivos JSON
- Crear y validar recetas directamente desde el navegador
- Visualizar resultados detallados con recomendaciones específicas
- Identificar problemas categorizados por severidad

Para acceder a la interfaz de validación, simplemente dirígete a la sección "Validar Receta" en la aplicación web.

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/TRIVO-AI.git
cd TRIVO-AI
```

2. Crear un entorno virtual e instalar dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con los valores apropiados
```

## Uso

### Iniciar la interfaz web:

```bash
python -m app.app
```

Acceder a `http://localhost:8000` en el navegador.

### Ejecutar el algoritmo genético desde la línea de comandos:

```bash
python -m src.features.genetic.optimizer --ingredients data/ingredients.json --generations 100
```

## Desarrollo

Para contribuir al proyecto:

1. Crea una rama para tu funcionalidad:
```bash
git checkout -b feature/nueva-funcionalidad
```

2. Realiza tus cambios y comitea:
```bash
git commit -am "Añadir nueva funcionalidad"
```

3. Envía tu rama al repositorio:
```bash
git push origin feature/nueva-funcionalidad
```

4. Crea un Pull Request para revisión.

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. Ver el archivo LICENSE para más detalles. 