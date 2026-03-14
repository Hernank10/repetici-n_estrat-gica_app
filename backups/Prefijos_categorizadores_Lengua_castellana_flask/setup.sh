#!/bin/bash

echo "🚀 Instalando Ecosistema de Morfología"
echo "======================================"

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Inicializar base de datos
echo "🗄️  Inicializando base de datos..."
python -c "
from app import db, init_db
init_db()
print('✅ Base de datos inicializada correctamente')
"

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "Para ejecutar la aplicación:"
echo "1. Activa el entorno virtual: source venv/bin/activate"
echo "2. Ejecuta: flask run --port=5001"
echo "3. Abre: http://localhost:5001"
echo ""
echo "Usuario demo: demo / demo123"
