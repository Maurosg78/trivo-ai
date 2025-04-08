#!/usr/bin/env python3
"""
Script para configurar los milestones del proyecto TRIVO-AI según el roadmap.
Este script crea hitos en GitHub correspondientes a las fases del roadmap.
"""

import os
import sys
from datetime import datetime, timedelta
from github import Github
from github.GithubException import GithubException

# Configuración
REPO_NAME = "Maurosg78/trivo-ai"
# El token debe configurarse como variable de entorno GITHUB_TOKEN

def create_milestones(repo):
    """
    Crea los hitos del proyecto según el roadmap.
    
    Args:
        repo: Objeto de repositorio GitHub
    """
    # Fecha actual como punto de partida
    today = datetime.now()
    
    # Definir los milestones del roadmap
    milestones = [
        {
            "title": "Sprint 1: Fundamentos MVP",
            "description": "Desarrollo del núcleo de optimización, interfaz PYME básica y modelo de negocio.",
            "due_on": today + timedelta(weeks=4)
        },
        {
            "title": "Sprint 2: Validación MVP",
            "description": "Implementación de piloto con PYMEs y mejoras iniciales basadas en feedback.",
            "due_on": today + timedelta(weeks=8)
        },
        {
            "title": "Fase 2: Consolidación (Mes 1)",
            "description": "Desarrollo de biblioteca de masas y herramientas para PYMEs.",
            "due_on": today + timedelta(weeks=12)
        },
        {
            "title": "Fase 2: Consolidación (Mes 2)",
            "description": "Validación extendida con 15-20 PYMEs y mejoras de proceso.",
            "due_on": today + timedelta(weeks=16)
        },
        {
            "title": "Fase 2: Consolidación (Mes 3)",
            "description": "Preparación para escala: infraestructura y marketing.",
            "due_on": today + timedelta(weeks=20)
        },
        {
            "title": "Fase 3: Expansión (Mes 1-3)",
            "description": "Desarrollo de módulos para nuevos segmentos: lácteos y embutidos.",
            "due_on": today + timedelta(weeks=32)
        },
        {
            "title": "Fase 3: Expansión (Mes 4-6)",
            "description": "Integración con sistemas de gestión y proveedores.",
            "due_on": today + timedelta(weeks=44)
        },
        {
            "title": "Fase 4: PLM Completa (Mes 1-6)",
            "description": "Implementación de funcionalidades avanzadas: ciclo de vida y BI.",
            "due_on": today + timedelta(weeks=70)
        },
        {
            "title": "Fase 4: PLM Completa (Mes 7-12)",
            "description": "Desarrollo del ecosistema: marketplace y comunidad.",
            "due_on": today + timedelta(weeks=96)
        }
    ]
    
    created_milestones = []
    
    # Crear cada milestone
    for ms in milestones:
        try:
            # Verificar si ya existe
            existing = [m for m in repo.get_milestones() if m.title == ms["title"]]
            if existing:
                print(f"El milestone '{ms['title']}' ya existe.")
                created_milestones.append(existing[0])
                continue
            
            # Crear nuevo milestone
            milestone = repo.create_milestone(
                title=ms["title"],
                description=ms["description"],
                due_on=ms["due_on"]
            )
            created_milestones.append(milestone)
            print(f"✓ Creado milestone: {ms['title']}")
        except GithubException as e:
            print(f"Error al crear milestone '{ms['title']}': {e}")
    
    return created_milestones

def create_project_board(repo, milestones):
    """
    Crea un tablero de proyecto con columnas para seguimiento.
    
    Args:
        repo: Objeto de repositorio GitHub
        milestones: Lista de milestones creados
    """
    try:
        # Verificar si ya existe un proyecto con el mismo nombre
        existing = [p for p in repo.get_projects() if p.name == "TRIVO-AI Roadmap"]
        if existing:
            print(f"El proyecto 'TRIVO-AI Roadmap' ya existe.")
            return existing[0]
        
        # Crear nuevo proyecto
        project = repo.create_project(
            name="TRIVO-AI Roadmap",
            body="Roadmap completo del proyecto TRIVO-AI para PYMEs alimentarias"
        )
        
        # Crear columnas
        columns = [
            "Backlog",
            "Sprint 1 - En Progreso",
            "Sprint 2 - Planificado",
            "Consolidación",
            "Expansión",
            "PLM Completa",
            "Completado"
        ]
        
        for column_name in columns:
            project.create_column(column_name)
            print(f"✓ Creada columna: {column_name}")
        
        print(f"✓ Creado proyecto: TRIVO-AI Roadmap")
        return project
    except GithubException as e:
        print(f"Error al crear proyecto: {e}")
        return None

def create_sprint_issues(repo, milestone):
    """
    Crea issues para el primer sprint basados en el KANBAN.
    
    Args:
        repo: Objeto de repositorio GitHub
        milestone: Objeto de milestone para el sprint
    """
    # Issues del Sprint 1
    issues = [
        {
            "title": "[T001] Simplificación UI",
            "body": """**Descripción:** Reducir la interfaz a funciones esenciales para PYMEs

**Prioridad:** Alta
**Puntos:** 8

Tareas:
- [ ] Identificar elementos esenciales de la UI
- [ ] Eliminar funcionalidades complejas o innecesarias
- [ ] Diseñar flujos simplificados
- [ ] Validar con usuarios objetivo""",
            "labels": ["enhancement", "ui/ux", "priority:alta", "points:8"]
        },
        {
            "title": "[T002] Onboarding Express",
            "body": """**Descripción:** Crear flujo de registro e inicio en menos de 1 día

**Prioridad:** Alta
**Puntos:** 8

Tareas:
- [ ] Diseñar flujo de onboarding simplificado
- [ ] Implementar formulario mínimo
- [ ] Crear sistema de plantillas predefinidas
- [ ] Automatizar configuración inicial""",
            "labels": ["enhancement", "ui/ux", "priority:alta", "points:8"]
        },
        {
            "title": "[T003] Calculadora ROI",
            "body": """**Descripción:** Herramienta visual para demostrar ahorro inmediato

**Prioridad:** Alta
**Puntos:** 5

Tareas:
- [ ] Desarrollar algoritmo de cálculo de ROI
- [ ] Crear visualización gráfica de ahorros
- [ ] Implementar comparador de costos
- [ ] Integrar con optimizador de recetas""",
            "labels": ["enhancement", "feature", "priority:alta", "points:5"]
        },
        {
            "title": "[T004] Módulo \"Paga si Ahorras\"",
            "body": """**Descripción:** Implementar modelo de pago basado en ahorro verificado

**Prioridad:** Alta
**Puntos:** 8

Tareas:
- [ ] Diseñar sistema de medición de ahorro
- [ ] Implementar cálculo de ahorro basado en ingredientes
- [ ] Crear panel de verificación de ahorros
- [ ] Desarrollar modelo de facturación""",
            "labels": ["enhancement", "feature", "priority:alta", "points:8"]
        },
        {
            "title": "[T005] Optimizador de Costos Rápido",
            "body": """**Descripción:** Algoritmo simplificado enfocado solo en reducción de costos

**Prioridad:** Alta
**Puntos:** 13

Tareas:
- [ ] Simplificar algoritmo genético
- [ ] Optimizar para velocidad de ejecución
- [ ] Implementar biblioteca básica de ingredientes
- [ ] Crear función de cálculo de costos""",
            "labels": ["enhancement", "algorithm", "priority:alta", "points:13"]
        },
        {
            "title": "[P001] Validador Express",
            "body": """**Descripción:** Sistema de validación con 5-7 reglas críticas para viabilidad

**Prioridad:** Alta
**Puntos:** 8

Tareas:
- [ ] Identificar reglas críticas de viabilidad
- [ ] Implementar validador simplificado
- [ ] Crear sistema de alertas
- [ ] Desarrollar recomendaciones automáticas""",
            "labels": ["enhancement", "in-progress", "priority:alta", "points:8"]
        },
        {
            "title": "[P002] Dashboard Simplificado",
            "body": """**Descripción:** Interfaz visual simple para mostrar ahorro en tiempo real

**Prioridad:** Alta
**Puntos:** 8

Tareas:
- [ ] Diseñar dashboard minimalista
- [ ] Implementar visualización de métricas clave
- [ ] Crear sistema de alertas y notificaciones
- [ ] Desarrollar panel de controles simplificado""",
            "labels": ["enhancement", "in-progress", "priority:alta", "points:8"]
        }
    ]
    
    created_issues = []
    
    # Crear cada issue
    for issue_data in issues:
        try:
            # Convertir etiquetas a minúsculas y crear si no existen
            labels = []
            for label_name in issue_data['labels']:
                label_name = label_name.lower()
                try:
                    # Intentar obtener la etiqueta existente
                    label = [l for l in repo.get_labels() if l.name.lower() == label_name]
                    if label:
                        labels.append(label[0])
                    else:
                        # Crear la etiqueta si no existe
                        if "enhancement" in label_name:
                            color = "0366d6"
                        elif "priority:alta" in label_name:
                            color = "d93f0b"
                        elif "priority:media" in label_name:
                            color = "fbca04"
                        elif "priority:baja" in label_name:
                            color = "c2e0c6"
                        elif "ui/ux" in label_name:
                            color = "cc317c"
                        elif "algorithm" in label_name:
                            color = "5319e7"
                        elif "feature" in label_name:
                            color = "1d76db"
                        elif "in-progress" in label_name:
                            color = "0e8a16"
                        else:
                            color = "d4c5f9"
                        labels.append(repo.create_label(label_name, color))
                except GithubException:
                    print(f"No se pudo crear la etiqueta: {label_name}")
            
            # Verificar si el issue ya existe
            existing = [i for i in repo.get_issues() if i.title == issue_data["title"]]
            if existing:
                print(f"El issue '{issue_data['title']}' ya existe.")
                continue
            
            # Crear el issue
            issue = repo.create_issue(
                title=issue_data['title'],
                body=issue_data['body'],
                labels=labels,
                milestone=milestone
            )
            created_issues.append(issue)
            print(f"✓ Creado issue: {issue_data['title']}")
        except GithubException as e:
            print(f"Error al crear issue {issue_data['title']}: {e}")
    
    return created_issues

def main():
    """Función principal."""
    # Verificar token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("Error: No se encontró el token de GitHub. Configure la variable de entorno GITHUB_TOKEN.")
        sys.exit(1)
    
    try:
        g = Github(github_token)
        repo = g.get_repo(REPO_NAME)
        print(f"Conectado al repositorio: {REPO_NAME}")
        
        # Crear milestones
        print("\nCreando milestones del proyecto...")
        milestones = create_milestones(repo)
        
        # Crear tablero de proyecto
        print("\nCreando tablero de proyecto...")
        project = create_project_board(repo, milestones)
        
        # Crear issues para el primer sprint
        if milestones:
            sprint1_milestone = [m for m in milestones if "Sprint 1" in m.title]
            if sprint1_milestone:
                print("\nCreando issues para el Sprint 1...")
                create_sprint_issues(repo, sprint1_milestone[0])
        
        print("\nConfiguración del proyecto completada con éxito.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 