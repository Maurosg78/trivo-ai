# Guía de Configuración para PizzaAI

Este documento describe el sistema de configuración y las decisiones de diseño implementadas para gestionar variables de entorno, claves API y otros parámetros del sistema.

## Estructura de Configuración

La configuración de PizzaAI se centraliza en el archivo `config.py` ubicado en la raíz del proyecto. Este archivo carga automáticamente las variables de entorno y define valores por defecto para configuraciones importantes.

### Variables de Entorno (.env)

Las variables de entorno se cargan usando `python-dotenv` desde un archivo `.env` en la raíz del proyecto. Puedes crear este archivo a partir del ejemplo `.env.example`:

```bash
cp .env.example .env
```

Luego edítalo para configurar tus claves API y otras opciones.

### Variables Críticas

Las siguientes variables de entorno son cruciales para el funcionamiento completo del sistema:

- `OPENAI_API_KEY`: Clave API para acceder a OpenAI (necesaria para LLMSupervisor)
- `USDA_API_KEY`: Clave API para acceder a la base de datos nutricional de USDA
- `SECRET_KEY`: Clave secreta para sesiones Flask y tokens

Si alguna de estas variables no está configurada, el sistema mostrará advertencias en el log y usará versiones mock cuando sea posible.

## Módulos Mock

El sistema implementa versiones simuladas (mock) de componentes clave para permitir el desarrollo y pruebas sin depender de servicios externos:

- `app/mock_supervisor.py`: Versión simulada del supervisor LLM
- `app/mock_language_processor.py`: Versión simulada del procesador de lenguaje natural

Estos módulos se usan automáticamente cuando:
1. Las dependencias reales no están disponibles
2. Las claves API necesarias no están configuradas
3. Se ejecuta en modo de prueba

## Estructura de Directorios

La configuración define y crea varios directorios críticos:

- `DATA_DIR`: Para almacenar datos persistentes como recetas, feedbacks y reglas
- `LOGS_DIR`: Para almacenar archivos de registro

## Mejores Prácticas de Seguridad

### Claves API

- **Nunca** almacenes claves API en el código fuente
- **Siempre** usa variables de entorno para las claves API
- El sistema verificará la configuración y mostrará advertencias si faltan claves importantes

### Manejo de Secretos

Para proyectos en producción, considera:
- Usar un servicio de gestión de secretos como AWS Secrets Manager, Vault o similar
- Implementar rotación periódica de claves
- Diferentes claves para entornos de desarrollo, prueba y producción

## Uso en el Código

Para usar la configuración en tu código:

```python
from config import OPENAI_API_KEY, DATA_DIR, DEBUG

# Usar directamente las variables
if DEBUG:
    print(f"Datos almacenados en: {DATA_DIR}")
```

## Problemas Comunes

1. **Error: "OPENAI_API_KEY no configurada correctamente"**
   - Asegúrate de copiar tu clave API de OpenAI válida en el archivo .env

2. **Error al importar módulos**
   - Verifica que hayas instalado todas las dependencias con `pip install -r requirements.txt`

3. **Error cuando ejecutas scripts desde subdirectorios**
   - Los scripts están configurados para importar la configuración desde la raíz del proyecto
   - Ejecuta siempre desde la raíz usando `python -m scripts.nombre_script` 