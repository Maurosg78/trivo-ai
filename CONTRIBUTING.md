# Guías de Contribución

## Estructura del Proyecto

```
pizzaai/
├── src/
│   ├── core/           # Componentes core del sistema
│   ├── features/       # Módulos de características
│   └── api/           # Endpoints de la API
├── tests/             # Tests unitarios y de integración
├── docs/              # Documentación
└── scripts/           # Scripts de utilidad
```

## Flujo de Trabajo

1. **Ramas**
   - `main`: Rama principal de producción
   - `develop`: Rama de desarrollo
   - `feature/*`: Nuevas características
   - `bugfix/*`: Correcciones de bugs
   - `release/*`: Preparación de releases

2. **Commits**
   - Usar commits semánticos:
     - `feat`: Nueva característica
     - `fix`: Corrección de bug
     - `docs`: Cambios en documentación
     - `style`: Cambios de formato
     - `refactor`: Refactorización de código
     - `test`: Añadir/modificar tests
     - `chore`: Tareas de mantenimiento

3. **Pull Requests**
   - Crear PRs desde `develop` a `main`
   - Incluir descripción detallada
   - Añadir tests
   - Actualizar documentación
   - Solicitar revisión de código

## Estándares de Código

1. **Python**
   - Seguir PEP 8
   - Usar type hints
   - Documentar funciones y clases
   - Mantener cobertura de tests > 80%

2. **Tests**
   - Tests unitarios para cada componente
   - Tests de integración para flujos completos
   - Usar pytest
   - Mantener tests actualizados

3. **Documentación**
   - Docstrings en todas las funciones
   - README actualizado
   - Documentación de API
   - Guías de usuario

## Proceso de Revisión

1. **Code Review**
   - Revisar cambios de código
   - Verificar tests
   - Comprobar documentación
   - Validar estándares

2. **QA**
   - Pruebas manuales
   - Pruebas de integración
   - Verificación de rendimiento
   - Validación de seguridad

3. **Deployment**
   - Pruebas en staging
   - Verificación de configuración
   - Monitoreo post-deployment
   - Rollback plan

## Herramientas

1. **Desarrollo**
   - Python 3.11+
   - VS Code/PyCharm
   - Git
   - Docker

2. **Testing**
   - pytest
   - pytest-cov
   - black
   - isort
   - mypy

3. **CI/CD**
   - GitHub Actions
   - Dependabot
   - Codecov
   - SonarQube

## Seguridad

1. **Código**
   - Escaneo de vulnerabilidades
   - Análisis estático
   - Revisión de dependencias
   - Buenas prácticas OWASP

2. **Datos**
   - Encriptación de datos sensibles
   - Gestión de secretos
   - Backups
   - Políticas de retención

## Monitoreo y Mantenimiento

1. **Rendimiento**
   - Métricas de aplicación
   - Logs estructurados
   - Alertas
   - Optimización continua

2. **Mantenimiento**
   - Actualizaciones de dependencias
   - Limpieza de código
   - Optimización de recursos
   - Plan de escalabilidad 