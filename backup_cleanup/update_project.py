import json
import os
import requests
import sys
import time

# Token de GitHub - Debe configurarse como variable de entorno
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN no está configurado en las variables de entorno")
    print("Por favor, configure esta variable antes de ejecutar el script")
    sys.exit(1)
    
PROJECT_ID = "PVT_kwHOCIy6ZM4A1ibu"  # ID del proyecto "TRIVO-AI Development"
STATUS_FIELD_ID = "PVTSSF_lAHOCIy6ZM4A1ibuzgq_dhw"  # ID del campo Status

# IDs de opciones de estado
STATUS_OPTIONS = {
    "Backlog": "3577ecb5",
    "Sprint Planning": "83707b1e",
    "In Progress": "47fc9ee4",
    "Review": "a2167f72",
    "Done": "98236657"
}

# Configuración de headers para GraphQL
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v4+json",
    "Content-Type": "application/json"
}

def run_graphql_query(query, variables=None):
    """Ejecuta una consulta GraphQL en la API de GitHub."""
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=HEADERS
    )
    return response.json()

def get_issue_node_id(repo_owner, repo_name, issue_number):
    """Obtiene el ID del nodo de un issue específico."""
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
        repository(owner: $owner, name: $name) {
            issue(number: $number) {
                id
                title
                state
            }
        }
    }
    """
    variables = {
        "owner": repo_owner,
        "name": repo_name,
        "number": issue_number
    }
    
    result = run_graphql_query(query, variables)
    if "data" in result and result["data"]["repository"]["issue"]:
        return result["data"]["repository"]["issue"]["id"]
    return None

def add_issue_to_project(project_id, issue_id):
    """Agrega un issue al proyecto."""
    query = """
    mutation($projectId: ID!, $contentId: ID!) {
        addProjectV2ItemById(input: {
            projectId: $projectId,
            contentId: $contentId
        }) {
            item {
                id
                content {
                    ... on Issue {
                        title
                    }
                }
            }
        }
    }
    """
    variables = {
        "projectId": project_id,
        "contentId": issue_id
    }
    
    result = run_graphql_query(query, variables)
    if "data" in result and result["data"]["addProjectV2ItemById"]:
        return result["data"]["addProjectV2ItemById"]["item"]["id"]
    return None

def update_issue_status(item_id, status_field_id, option_id):
    """Actualiza el estado de un issue en el proyecto."""
    query = """
    mutation($itemId: ID!, $fieldId: ID!, $optionId: String!) {
        updateProjectV2ItemFieldValue(input: {
            projectId: "%s",
            itemId: $itemId,
            fieldId: $fieldId,
            value: {
                singleSelectOptionId: $optionId
            }
        }) {
            projectV2Item {
                id
            }
        }
    }
    """ % PROJECT_ID
    
    variables = {
        "itemId": item_id,
        "fieldId": status_field_id,
        "optionId": option_id
    }
    
    result = run_graphql_query(query, variables)
    return "data" in result and result["data"]["updateProjectV2ItemFieldValue"] is not None

def determine_status(issue_state, issue_title, issue_number):
    """Determina el estado de un issue en el proyecto."""
    # Todos los issues se consideran completados
    return "Done"

def main():
    # Lista de issues para agregar al proyecto
    issues_query = """
    query {
        repository(owner: "Maurosg78", name: "TRIVO-AI") {
            issues(first: 100, states: [OPEN, CLOSED]) {
                nodes {
                    number
                    title
                    state
                }
            }
        }
    }
    """
    
    result = run_graphql_query(issues_query)
    
    if "data" in result and result["data"]["repository"]["issues"]["nodes"]:
        issues = result["data"]["repository"]["issues"]["nodes"]
        
        for issue in issues:
            issue_number = issue["number"]
            issue_title = issue["title"]
            issue_state = issue["state"].lower()
            
            print(f"Procesando issue #{issue_number}: {issue_title}")
            
            # Obtener ID del nodo del issue
            issue_id = get_issue_node_id("Maurosg78", "TRIVO-AI", issue_number)
            if not issue_id:
                print(f"No se pudo obtener el ID del issue #{issue_number}")
                continue
            
            # Agregar issue al proyecto
            item_id = add_issue_to_project(PROJECT_ID, issue_id)
            if not item_id:
                print(f"No se pudo agregar el issue #{issue_number} al proyecto")
                continue
                
            # Determinar el estado del issue
            status = determine_status(issue_state, issue_title, issue_number)
            option_id = STATUS_OPTIONS[status]
            
            # Actualizar estado
            if update_issue_status(item_id, STATUS_FIELD_ID, option_id):
                print(f"Issue #{issue_number} agregado al proyecto con estado {status}")
            else:
                print(f"No se pudo actualizar el estado del issue #{issue_number}")
            
            # Pausa para evitar límites de rate
            time.sleep(1)
    else:
        print("No se pudieron obtener los issues")

if __name__ == "__main__":
    main() 