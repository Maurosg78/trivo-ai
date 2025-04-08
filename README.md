# TRIVO-AI: PLM para PYMEs Alimentarias

TRIVO-AI es una plataforma de gestión del ciclo de vida del producto (PLM) especializada para pequeñas y medianas empresas del sector alimentario, comenzando con un MVP enfocado en la optimización de masas para panaderías y pizzerías.

## Características Principales

- **Optimización de Recetas**: Algoritmo genético para optimizar recetas según costos y calidad
- **Validación de Producción**: Sistema de validación con reglas críticas para diferentes escalas
- **Procesamiento de Lenguaje Natural**: Creación de recetas a partir de descripciones en lenguaje natural
- **Interfaz Web Moderna**: Diseño intuitivo con colores corporativos (verde, naranja y negro)

## Estructura del Proyecto

```
TRIVO-AI/
├── app/                  # Aplicación web
│   ├── static/           # Archivos estáticos (CSS, JS)
│   └── templates/        # Plantillas HTML
├── docs/                 # Documentación
│   ├── KANBAN.md         # Tablero Kanban del proyecto
│   ├── TRIVO-PLM_KANBAN.md  # Tablero Kanban detallado con sprints 
│   └── TRIVO-PLM_ROADMAP.md # Roadmap completo del producto
├── scripts/              # Scripts de utilidad
│   ├── validation_system/  # Sistema de validación
│   └── create_github_issues.py  # Script para crear issues en GitHub
└── src/                  # Código fuente principal
    ├── features/         # Características principales
    │   ├── optimizer/    # Algoritmo genético
    │   ├── validator/    # Sistema de validación
    │   └── nlp/          # Procesamiento de lenguaje natural
    └── utils/            # Utilidades
```

## Configuración del Entorno de Desarrollo

### Requisitos Previos

- Python 3.8+
- pip
- Git

### Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Maurosg78/trivo-ai.git
   cd trivo-ai
   ```

2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución de la Aplicación

Iniciar la aplicación web:
```bash
python -m app.app
```

Acceder a la aplicación en http://localhost:8000

## Creación de Issues en GitHub

Para crear automáticamente issues en GitHub basados en los archivos KANBAN:

1. Instalar la dependencia necesaria:
   ```bash
   pip install PyGithub
   ```

2. Configurar token de GitHub:
   ```bash
   export GITHUB_TOKEN=tu_token_personal  # En Windows: set GITHUB_TOKEN=tu_token_personal
   ```

3. Ejecutar el script:
   ```bash
   python scripts/create_github_issues.py
   ```

## Roadmap

El proyecto está organizado en las siguientes fases:

1. **MVP "Masas Express" (8 semanas)**
   - Implementación inicial enfocada en optimización de costos
   - Interfaz de usuario simplificada
   - Validación básica de viabilidad

2. **Consolidación (3 meses)**
   - Ampliación de capacidades a diferentes tipos de masas
   - Herramientas específicas para PYMEs
   - Documentación de casos de éxito

3. **Expansión (6 meses)**
   - Soporte para nuevos segmentos alimentarios (lácteos, embutidos)
   - Integración con sistemas de gestión
   - Conexión con proveedores

4. **PLM Completa (12 meses)**
   - Gestión completa del ciclo de vida del producto
   - Inteligencia de negocio avanzada
   - Marketplace de fórmulas verificadas

## Licencia

Este proyecto está licenciado bajo [Licencia Propietaria] - ver el archivo LICENSE para más detalles.

## Contacto

Para más información, contactar con info@trivo-ai.com 