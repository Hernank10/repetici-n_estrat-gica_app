#!/bin/bash
echo "Limpiando cachés y archivos temporales..."
pip cache purge
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
rm -rf ~/.cache/pip
rm -f *.log
echo "Limpieza completada."
df -h .
