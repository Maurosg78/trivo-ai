#!/usr/bin/env python3
"""
Script para crear automáticamente issues en GitHub basados en los archivos KANBAN.
Requiere tener instalado PyGithub:
pip install PyGithub
"""

import os
import sys
import re
from github import Github
from github.GithubException import GithubException

# Configuración
REPO_NAME = "Maurosg78/trivo-ai"
# El token debe configurarse como variable de entorno GITHUB_TOKEN

def parse_kanban_file(file_path):
    """Extrae tareas del archivo KANBAN."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer secciones TODO e IN PROGRESS
    todo_section = re.search(r'## Por Hacer \(To Do\)(.*?)##', content, re.DOTALL)
    in_progress_section = re.search(r'## En Progreso \(In Progress\)(.*?)##', content, re.DOTALL)
    
    issues = []
    
    # Procesar sección TODO
    if todo_section:
        todo_text = todo_section.group(1)
        todo_items = re.findall(r'- \[ \] (.*)', todo_text)
        for item in todo_items:
            issues.append({
                'title': item.strip(),
                'body': f"Tarea extraída del Kanban: {item}",
                'labels': ['enhancement', 'todo']
            })
    
    # Procesar sección IN PROGRESS
    if in_progress_section:
        in_progress_text = in_progress_section.group(1)
        in_progress_items = re.findall(r'- \[ \] (.*)', in_progress_text)
        for item in in_progress_items:
            issues.append({
                'title': item.strip(),
                'body': f"Tarea extraída del Kanban: {item}",
                'labels': ['enhancement', 'in-progress']
            })
    
    return issues

def parse_sprint_kanban(file_path):
    """Extrae tareas del archivo KANBAN de sprint."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer sección de sprint actual
    sprint_section = re.search(r'## MVP "Masas Express" - Sprint 1.*?### DONE', content, re.DOTALL)
    if not sprint_section:
        return []
    
    # Extraer tareas TODO e IN PROGRESS
    todo_section = re.search(r'### TODO(.*?)### IN PROGRESS', sprint_section.group(0), re.DOTALL)
    in_progress_section = re.search(r'### IN PROGRESS(.*?)### REVIEW', sprint_section.group(0), re.DOTALL)
    
    issues = []
    
    # Procesar tareas TODO
    if todo_section:
        todo_text = todo_section.group(1)
        todo_rows = re.findall(r'\|\s*([T]\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(\d+)\s*\|', todo_text)
        for row in todo_rows:
            task_id, task_name, task_desc, priority, points = row
            issues.append({
                'title': f"[{task_id}] {task_name}",
                'body': f"**Descripción:** {task_desc}\n\n**Prioridad:** {priority}\n**Puntos:** {points}",
                'labels': ['enhancement', 'todo', f'priority:{priority.lower()}', f'points:{points}']
            })
    
    # Procesar tareas IN PROGRESS
    if in_progress_section:
        in_progress_text = in_progress_section.group(1)
        in_progress_rows = re.findall(r'\|\s*([P]\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(\d+)\s*\|', in_progress_text)
        for row in in_progress_rows:
            task_id, task_name, task_desc, priority, points = row
            issues.append({
                'title': f"[{task_id}] {task_name}",
                'body': f"**Descripción:** {task_desc}\n\n**Prioridad:** {priority}\n**Puntos:** {points}",
                'labels': ['enhancement', 'in-progress', f'priority:{priority.lower()}', f'points:{points}']
            })
    
    return issues

def create_milestone(repo, title, description, due_on=None):
    """Crea un milestone en GitHub."""
    try:
        milestone = repo.create_milestone(
            title=title,
            description=description,
            due_on=due_on
        )
        print(f"Milestone creado: {title}")
        return milestone
    except GithubException as e:
        print(f"Error al crear milestone {title}: {e}")
        return None

def create_issues(issues, repo, milestone=None):
    """Crea issues en GitHub."""
    created_issues = []
    
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
                        color = "0366d6" if "enhancement" in label_name else "d4c5f9"
                        labels.append(repo.create_label(label_name, color))
                except GithubException:
                    print(f"No se pudo crear la etiqueta: {label_name}")
            
            # Crear el issue
            issue = repo.create_issue(
                title=issue_data['title'],
                body=issue_data['body'],
                labels=labels,
                milestone=milestone
            )
            created_issues.append(issue)
            print(f"Issue creado: {issue_data['title']}")
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
        
        # Crear milestone para Sprint 1
        sprint1_milestone = create_milestone(
            repo,
            "Sprint 1 - MVP Masas Express",
            "Primer sprint para desarrollar el MVP de TRIVO-AI enfocado en optimización de masas."
        )
        
        # Obtener issues del KANBAN general
        kanban_issues = parse_kanban_file("docs/KANBAN.md")
        
        # Obtener issues del KANBAN de sprint
        sprint_issues = parse_sprint_kanban("docs/TRIVO-PLM_KANBAN.md")
        
        # Crear issues
        if sprint_issues:
            print("Creando issues del sprint...")
            create_issues(sprint_issues, repo, sprint1_milestone)
        
        if kanban_issues:
            print("Creando issues del KANBAN general...")
            create_issues(kanban_issues, repo)
        
        print("Proceso completado con éxito.")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 