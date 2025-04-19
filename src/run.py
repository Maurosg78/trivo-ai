#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para ejecutar la aplicación TRIVO-AI.

Este script proporciona una forma conveniente de iniciar la aplicación,
ya sea en modo de desarrollo o producción.
"""

import os
import sys
import argparse
import uvicorn

def parse_args():
    """
    Analiza los argumentos de línea de comandos.
    
    Returns:
        Namespace: Argumentos analizados
    """
    parser = argparse.ArgumentParser(description='Ejecutar servidor TRIVO-AI')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host donde se ejecutará el servidor (predeterminado: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Puerto donde se ejecutará el servidor (predeterminado: 8000)')
    parser.add_argument('--reload', action='store_true',
                        help='Habilitar recarga automática para desarrollo')
    parser.add_argument('--workers', type=int, default=1,
                        help='Número de trabajadores (predeterminado: 1)')
    
    return parser.parse_args()

def main():
    """
    Función principal para ejecutar la aplicación.
    """
    args = parse_args()
    
    # Configurar Uvicorn
    config = {
        "app": "src.api.main:app",
        "host": args.host,
        "port": args.port,
        "reload": args.reload,
        "workers": args.workers,
        "log_level": "info"
    }
    
    # Iniciar servidor
    print(f"Iniciando servidor en {args.host}:{args.port}...")
    uvicorn.run(**config)

if __name__ == "__main__":
    main() 