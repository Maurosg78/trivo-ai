# API de TRIVO-AI

Este directorio contiene la implementación de la API REST para el sistema TRIVO-AI.

## Estructura

- `main.py`: Punto de entrada principal de la aplicación FastAPI
- `help_endpoints.py`: Implementación de los endpoints relacionados con los registros de ayuda
- `project_endpoints.py`: Implementación de los endpoints relacionados con la gestión de proyectos

## Endpoints de ayuda

Los siguientes endpoints están disponibles para gestionar los registros de ayuda:

### GET /help/history

Obtiene el historial de interacciones de ayuda.

**Parámetros opcionales:**
- `user_id` (int): Filtrar por ID de usuario
- `recipe_id` (int): Filtrar por ID de receta
- `limit` (int, default=100): Número máximo de registros a devolver
- `offset` (int, default=0): Desplazamiento para paginación

**Requiere:**
- Usuarios normales solo pueden ver sus propios registros
- Administradores pueden ver todos los registros

### GET /help/search

Busca registros de ayuda basados en diferentes criterios.

**Parámetros opcionales:**
- `query` (str): Término de búsqueda en el texto
- `start_date` (str): Fecha de inicio en formato ISO (YYYY-MM-DD)
- `end_date` (str): Fecha de fin en formato ISO (YYYY-MM-DD)
- `user_id` (int): Filtrar por ID de usuario
- `recipe_id` (int): Filtrar por ID de receta
- `limit` (int, default=50): Número máximo de registros a devolver
- `offset` (int, default=0): Desplazamiento para paginación

**Requiere:**
- Usuarios normales solo pueden buscar sus propios registros
- Administradores pueden buscar todos los registros

### GET /help/statistics

Obtiene estadísticas sobre las interacciones de ayuda.

**Requiere:**
- Solo disponible para administradores

### DELETE /help/log/{log_id}

Elimina un registro de ayuda específico.

**Parámetros:**
- `log_id` (path): ID del registro a eliminar

**Requiere:**
- Solo disponible para administradores

## Endpoints de proyectos

Los siguientes endpoints están disponibles para gestionar proyectos:

### POST /projects

Crea un nuevo proyecto.

**Parámetros:**
- `name` (str): Nombre del proyecto (obligatorio)
- `description` (str): Descripción del proyecto
- `is_public` (bool): Si el proyecto es público o privado
- `status` (str): Estado del proyecto (active, archived, completed)
- `tags` (array): Etiquetas del proyecto
- `config` (object): Configuración adicional del proyecto

**Requiere:**
- Usuario autenticado (el usuario actual se convierte en creador y miembro del proyecto)

### GET /projects

Lista proyectos.

**Parámetros opcionales:**
- `status` (str): Filtrar por estado
- `is_public` (bool): Filtrar por visibilidad
- `limit` (int, default=50): Número máximo de registros a devolver
- `offset` (int, default=0): Desplazamiento para paginación

**Requiere:**
- Usuario autenticado
- Usuarios normales solo ven sus propios proyectos
- Administradores pueden ver todos los proyectos

### GET /projects/{project_id}

Obtiene un proyecto específico por su ID.

**Parámetros:**
- `project_id` (path): ID del proyecto a consultar

**Requiere:**
- Usuario autenticado
- Para proyectos privados, solo creador, miembros y administradores

### PUT /projects/{project_id}

Actualiza un proyecto existente.

**Parámetros:**
- `project_id` (path): ID del proyecto a actualizar
- Campos a actualizar en el cuerpo de la solicitud

**Requiere:**
- Solo el creador del proyecto y administradores

### DELETE /projects/{project_id}

Elimina un proyecto.

**Parámetros:**
- `project_id` (path): ID del proyecto a eliminar

**Requiere:**
- Solo el creador del proyecto y administradores

### POST /projects/{project_id}/users/{user_id}

Añade un usuario a un proyecto.

**Parámetros:**
- `project_id` (path): ID del proyecto
- `user_id` (path): ID del usuario a añadir

**Requiere:**
- Solo el creador del proyecto y administradores

### DELETE /projects/{project_id}/users/{user_id}

Elimina un usuario de un proyecto.

**Parámetros:**
- `project_id` (path): ID del proyecto
- `user_id` (path): ID del usuario a eliminar

**Requiere:**
- Solo el creador del proyecto y administradores
- No se puede eliminar al creador del proyecto

### POST /projects/{project_id}/recipes/{recipe_id}

Añade una receta a un proyecto.

**Parámetros:**
- `project_id` (path): ID del proyecto
- `recipe_id` (path): ID de la receta a añadir

**Requiere:**
- Creador, miembros del proyecto y administradores

### DELETE /projects/{project_id}/recipes/{recipe_id}

Elimina una receta de un proyecto.

**Parámetros:**
- `project_id` (path): ID del proyecto
- `recipe_id` (path): ID de la receta a eliminar

**Requiere:**
- Creador, miembros del proyecto y administradores

## Cómo ejecutar

Para ejecutar la API, utiliza el script `run.py` en el directorio raíz:

```bash
# Modo de desarrollo con recarga automática
python src/run.py --reload

# Modo de producción con múltiples trabajadores
python src/run.py --workers 4
```

## Documentación de la API

Una vez que el servidor está en ejecución, puedes acceder a la documentación interactiva de la API en:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 