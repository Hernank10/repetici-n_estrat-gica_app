import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-super-segura-2024'
    MAX_EJEMPLOS = 100
    DATA_FILE = os.path.join('data', 'ejemplos.json')
    EJERCICIOS_FILE = os.path.join('data', 'ejercicios_completos.json')
    FLASHCARDS_FILE = os.path.join('data', 'flashcards.json')
    USUARIOS_FILE = os.path.join('data', 'usuarios.json')
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_PERMANENT = True
    
    # Configuración de medallas
    MEDALLAS = {
        'bronce': {'ejercicios': 10, 'correctos': 5, 'icono': '🥉'},
        'plata': {'ejercicios': 25, 'correctos': 15, 'icono': '🥈'},
        'oro': {'ejercicios': 50, 'correctos': 35, 'icono': '🥇'},
        'diamante': {'ejercicios': 100, 'correctos': 80, 'icono': '💎'},
        'maestro': {'ejercicios': 200, 'correctos': 180, 'icono': '🏆'}
    }
    
    # Puntos por acción
    PUNTOS = {
        'ejercicio_completado': 10,
        'respuesta_correcta': 20,
        'racha_3': 50,
        'racha_5': 100,
        'racha_10': 250,
        'flashcard_completada': 5,
        'ejemplo_creado': 15
    }

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
