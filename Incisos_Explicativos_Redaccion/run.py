#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run.py - Punto de entrada para ejecutar la aplicación Flask
Ejecutar con: python run.py
"""

from app import app

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Incisos Explicativos - Aplicación Flask")
    print("=" * 50)
    print("📌 Servidor iniciado en: http://localhost:5000")
    print("📌 Presiona Ctrl+C para detener el servidor")
    print("=" * 50)
    
    # Configuración del servidor
    app.run(
        host='0.0.0.0',  # Escucha en todas las interfaces de red
        port=5000,        # Puerto por defecto
        debug=True,       # Modo debug (recarga automática)
        threaded=True     # Soporte para múltiples conexiones
    )
