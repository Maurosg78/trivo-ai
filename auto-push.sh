#!/bin/bash

# Obtener la fecha y hora actual
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Mensaje del commit
COMMIT_MESSAGE="Auto-commit: $TIMESTAMP"

echo "### Automatización de Git ###"

# Agregar cambios
echo "Agregando archivos al área de staging..."
git add .

# Crear commit
echo "Creando commit con el mensaje: '$COMMIT_MESSAGE'..."
git commit -m "$COMMIT_MESSAGE"

# Subir al repositorio remoto
echo "Subiendo cambios al repositorio remoto..."
git push origin main

echo "### Proceso completado ###"

