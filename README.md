# MasaAI

Sistema inteligente para creación y validación de recetas de masas utilizando tecnologías de IA.

## Descripción

MasaAI es una aplicación que utiliza procesamiento de lenguaje natural e inteligencia artificial para:

1. Crear recetas de masas a partir de descripciones en lenguaje natural
2. Analizar recetas existentes para verificar su conformidad con estándares de calidad
3. Proporcionar retroalimentación y sugerencias para mejorar las recetas
4. Aprender de la retroalimentación del supervisor humano

## Características principales

- **Procesador de lenguaje natural**: Convierte descripciones en lenguaje natural a recetas estructuradas
- **Supervisor LLM**: Revisa recetas automáticamente usando reglas aprendidas
- **Sistema de retroalimentación**: Permite a los supervisores proporcionar feedback y crear nuevas reglas
- **Interfaz web**: Facilita la interacción con el sistema a través de un navegador
- **CLI**: Herramientas de línea de comandos para interacción rápida con el sistema

## Estructura del proyecto

```
MasaAI/
├── app/                      # Aplicación principal
│   ├── static/               # Archivos estáticos (CSS, JS, imágenes)
│   ├── templates/            # Plantillas HTML
│   ├── app.py                # Aplicación Flask principal
│   ├── mock_language_processor.py  # Versión mock del procesador de lenguaje
│   └── mock_supervisor.py    # Versión mock del supervisor LLM
├── config.py                 # Configuración centralizada
├── data/                     # Directorio para almacenamiento de datos
├── scripts/                  # Scripts de utilidad
│   ├── cli.py                # Interfaz de línea de comandos
│   └── test_system.py        # Script de prueba del sistema
└── README.md                 # Este archivo
```

## Requisitos

- Python 3.8+
- Flask
- OpenAI API Key (opcional, para uso con modelos reales en lugar de mocks)
- Dependencias adicionales listadas en `requirements.txt`

## Instalación

1. Clone el repositorio:
   ```
   git clone https://github.com/tuorganizacion/MasaAI.git
   cd MasaAI
   ```

2. Instale las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Configure sus variables de entorno (opcional para usar con modelos reales):
   ```
   export OPENAI_API_KEY="su-clave-api"
   ```

## Uso

### Interfaz web

Para iniciar la aplicación web:

```
python -m app.app
```

Luego visite `http://localhost:5000` en su navegador.

### Línea de comandos

La aplicación incluye una interfaz de línea de comandos para interactuar con el sistema:

```
# Crear una nueva receta
python scripts/cli.py crear "Masa para pan con harina integral y semillas"

# Analizar una descripción
python scripts/cli.py analizar "Masa para galletas con chocolate"

# Revisar una receta existente
python scripts/cli.py revisar data/recipe_12345.json

# Mostrar reglas aprendidas
python scripts/cli.py reglas
```

## Seguridad

El sistema utiliza un enfoque de "mocks por defecto" para garantizar que funcione sin necesidad de credenciales de API externas:

- Si las credenciales de API necesarias no están disponibles, se utilizan implementaciones mock
- Los datos sensibles se almacenan de manera segura utilizando las mejores prácticas
- Las interacciones con APIs externas están aisladas y pueden ser desactivadas fácilmente

## Contribuir

Las contribuciones son bienvenidas. Por favor, siga estos pasos:

1. Haga un fork del repositorio
2. Cree una rama para su característica (`git checkout -b feature/amazing-feature`)
3. Realice sus cambios
4. Ejecute las pruebas (`python scripts/test_system.py`)
5. Haga commit de sus cambios (`git commit -m 'Add some amazing feature'`)
6. Haga push a la rama (`git push origin feature/amazing-feature`)
7. Abra un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo LICENSE para más detalles. 