#!/usr/bin/env python3
"""
Script para crear issues en GitHub desde un archivo JSON.
"""

import json
import os
from typing import List

import requests

# Configuración
REPO_OWNER = "Maurosg78"
REPO_NAME = "PizzaAI"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"


def create_github_issue(title: str, body: str, labels: List[str]) -> None:
    """Crea un issue en GitHub."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN no está configurado en las variables de entorno")

    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    data = {"title": title, "body": body, "labels": labels}

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code != 201:
        raise Exception(f"Error al crear issue: {response.text}")


def main():
    """Función principal."""
    try:
        with open("sprint1_issues.json", "r") as f:
            issues_data = json.load(f)

        for issue in issues_data["issues"]:
            create_github_issue(issue["title"], issue["body"], issue["labels"])

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
