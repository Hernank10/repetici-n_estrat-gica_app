#!/bin/bash

echo "=== LIMPIEZA DE ESPACIO EN DISCO ==="
echo ""

# Mostrar espacio actual
echo "Espacio actual:"
df -h ~ | tail -1
echo ""

# Preguntar antes de limpiar
read -p "¿Eliminar carpetas de proyectos anteriores? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]
then
    # Listar proyectos grandes
    echo "Proyectos encontrados:"
    find ~ -maxdepth 1 -type d -name "*flask*" -o -name "*django*" -o -name "*python*" | while read dir; do
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        echo "  $size - $dir"
    done
    
    read -p "¿Eliminar TODOS los proyectos listados? (s/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]
    then
        find ~ -maxdepth 1 -type d -name "*flask*" -o -name "*django*" -o -name "*python*" -exec rm -rf {} \;
        echo "✅ Proyectos eliminados"
    fi
fi

# Limpiar cachés
echo ""
echo "Limpiando cachés..."
pip cache purge > /dev/null 2>&1
rm -rf ~/.cache/pip
rm -rf /tmp/pip-*
rm -rf ~/.cache/*
find ~ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find ~ -name "*.pyc" -delete 2>/dev/null
echo "✅ Cachés limpiados"

# Mostrar espacio liberado
echo ""
echo "Espacio después de limpieza:"
df -h ~ | tail -1

echo ""
echo "=== LIMPIEZA COMPLETADA ==="
