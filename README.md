# TRIVO-AI: Sistema de Formulación Inteligente de Masas

## Descripción

TRIVO-AI es un sistema avanzado de formulación inteligente para masas de pizza, que utiliza algoritmos genéticos y procesamiento de lenguaje natural para optimizar recetas según requisitos específicos. El sistema permite:

- **Creación de recetas mediante lenguaje natural**: Describe lo que necesitas y el sistema genera una receta optimizada.
- **Optimización de recetas**: Utiliza algoritmos genéticos para encontrar la combinación perfecta de ingredientes.
- **Validación de recetas**: Verifica que las recetas sean viables para diferentes escalas de producción.
- **Generación de instrucciones**: Proporciona instrucciones paso a paso para la preparación de las masas.

La principal innovación es la combinación de algoritmos genéticos y procesamiento de lenguaje natural, permitiendo a usuarios de todos los niveles obtener recetas profesionales optimizadas sin necesidad de conocimientos avanzados.

## Estructura del Proyecto

```
trivo-ai/
├── app/                    # Aplicación web principal
│   ├── app.py                 # Punto de entrada de la aplicación Flask
│   ├── recipe_optimizer.py    # Interfaz para el optimizador de recetas
│   ├── templates/             # Plantillas HTML
│   └── static/                # Archivos estáticos (CSS, JS, imágenes)
├── src/                    # Código fuente principal
│   ├── features/              # Características principales
│   │   ├── nlp/                  # Procesamiento de lenguaje natural
│   │   ├── optimizer/            # Optimizadores de recetas
│   │   └── validator/            # Validación de recetas
│   ├── core/                  # Componentes fundamentales
│   └── data/                  # Datos y configuraciones
├── scripts/                # Scripts de utilidad
└── tests/                  # Pruebas automatizadas
```

## Características Principales

1. **Procesamiento de Lenguaje Natural**: Interpreta descripciones en lenguaje natural para generar recetas.
2. **Optimización Genética**: Utiliza algoritmos genéticos para encontrar la combinación óptima de ingredientes.
3. **Sistema de Validación Crítico**: Verifica que las recetas sean válidas para diferentes escalas de producción.
4. **Soporte para Masas Sin Gluten**: Optimización especializada para recetas sin gluten.
5. **Interfaz Web Intuitiva**: Interfaz moderna y fácil de usar para interactuar con el sistema.

## Comenzando

### Prerrequisitos

- Python 3.8+
- Flask
- NumPy
- Pandas
- SciKit-Learn

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/usuario/trivo-ai.git
cd trivo-ai

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución

Para iniciar la aplicación web:

```bash
python -m app.app
```

Visita `http://localhost:8080` en tu navegador para acceder a la interfaz.

## Ejemplos de Uso

### Creación de recetas mediante lenguaje natural

Puedes ingresar descripciones como:

- "Quiero una masa de pizza familiar, de color rojo, sin gluten, nutricionalmente optimizada para mis hijos. Tipo margarita."
- "Necesito una masa pequeña, crujiente y ligera para pizza de pepperoni."
- "Masa para pizza vegana con sabores mediterráneos."

### Optimización manual

También puedes especificar manualmente los ingredientes y parámetros para que el sistema los optimice según tus preferencias.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, siga estos pasos:

1. Fork del repositorio
2. Crear una rama (`git checkout -b feature/mejora`)
3. Commit de cambios (`git commit -m 'Añadir mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Crear Pull Request

## Licencia

Este proyecto está licenciado bajo [MIT License](LICENSE).

## Contacto

Para soporte y consultas, contacte a [info@trivo-ai.com](mailto:info@trivo-ai.com). 