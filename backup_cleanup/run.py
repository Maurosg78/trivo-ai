#!/usr/bin/env python
"""
Script de inicio para la aplicación TRIVO-AI.
Este script inicia el servidor Flask sin abrir automáticamente el navegador.
"""

import os
import sys
import logging

# Asegurarse de que el directorio raíz está en el path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación
from app.app import app

if __name__ == '__main__':
    # Configurar el logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Obtener puerto de las variables de entorno o usar 8000 por defecto
    port = int(os.environ.get('PORT', 8000))
    
    # Mensaje informativo
    print(f"Iniciando TRIVO-AI en http://localhost:{port}")
    print("Presiona Ctrl+C para detener el servidor")
    
    # Iniciar servidor sin abrir navegador
    app.run(host='0.0.0.0', port=port, debug=True) 