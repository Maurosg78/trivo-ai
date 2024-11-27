#!/bin/bash
git add .
git commit -m "Respaldo automático $(date +"%Y-%m-%d %H:%M:%S")"
git push origin main
echo "Respaldo completado en el repositorio."
