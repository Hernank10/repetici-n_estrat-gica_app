import os
from datetime import timedelta

class Config:
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-para-desarrollo-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///combinatoria.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Configuración de Bootstrap
    BOOTSTRAP_SERVE_LOCAL = False
    BOOTSTRAP_BOOTSWATCH_THEME = None  # Puedes cambiar a: 'cerulean', 'cosmo', 'cyborg', 'darkly', 'flatly', 'journal', 'litera', 'lumen', 'lux', 'materia', 'minty', 'pulse', 'sandstone', 'simplex', 'sketchy', 'slate', 'solar', 'spacelab', 'superhero', 'united', 'yeti'
    
    # Configuración de niveles y progresión
    NIVELES = {
        'principiante': {
            'xp_requerido': 0,
            'color': 'bronce',
            'color_bootstrap': 'secondary',
            'icono': '🌱',
            'titulo': 'Principiante',
            'descripcion': 'Comienza tu viaje en la combinatoria léxica'
        },
        'intermedio': {
            'xp_requerido': 500,
            'color': 'plata',
            'color_bootstrap': 'info',
            'icono': '🌿',
            'titulo': 'Intermedio',
            'descripcion': 'Ya dominas las combinaciones básicas'
        },
        'avanzado': {
            'xp_requerido': 1500,
            'color': 'oro',
            'color_bootstrap': 'success',
            'icono': '🌳',
            'titulo': 'Avanzado',
            'descripcion': 'Manejas con soltura las restricciones semánticas'
        },
        'experto': {
            'xp_requerido': 3000,
            'color': 'diamante',
            'color_bootstrap': 'warning',
            'icono': '🏆',
            'titulo': 'Experto',
            'descripcion': 'Conoces las combinaciones como un lingüista'
        },
        'maestro': {
            'xp_requerido': 5000,
            'color': 'legendario',
            'color_bootstrap': 'danger',
            'icono': '👑',
            'titulo': 'Maestro',
            'descripcion': 'Eres un verdadero experto en combinatoria léxica'
        }
    }
    
    # Configuración de medallas actualizada
    MEDALLAS = {
        'rapidez': {
            'nombre': 'Velocista',
            'icono': '⚡',
            'color_bootstrap': 'warning',
            'descripcion': 'Responde 10 ejercicios en menos de 30 segundos',
            'condicion': 'tiempo_respuesta < 30'
        },
        'precision': {
            'nombre': 'Preciso', 
            'icono': '🎯',
            'color_bootstrap': 'success',
            'descripcion': '10 respuestas correctas consecutivas',
            'condicion': 'racha >= 10'
        },
        'dedicacion': {
            'nombre': 'Dedicado',
            'icono': '📚',
            'color_bootstrap': 'primary',
            'descripcion': 'Completa 50 ejercicios',
            'condicion': 'ejercicios_completados >= 50'
        },
        'creatividad': {
            'nombre': 'Creativo',
            'icono': '🎨',
            'color_bootstrap': 'info',
            'descripcion': 'Guarda 20 oraciones originales',
            'condicion': 'oraciones_guardadas >= 20'
        },
        'coleccionista': {
            'nombre': 'Coleccionista',
            'icono': '🏆',
            'color_bootstrap': 'warning',
            'descripcion': 'Desbloquea 10 medallas',
            'condicion': 'medallas_desbloqueadas >= 10'
        },
        'estudioso': {
            'nombre': 'Estudioso',
            'icono': '📇',
            'color_bootstrap': 'secondary',
            'descripcion': 'Completa 50 flashcards',
            'condicion': 'flashcards_completadas >= 50'
        },
        'perfeccionista': {
            'nombre': 'Perfeccionista',
            'icono': '💯',
            'color_bootstrap': 'danger',
            'descripcion': '100% de aciertos en un nivel',
            'condicion': 'nivel_perfecto'
        },
        'madrugador': {
            'nombre': 'Madrugador',
            'icono': '🌅',
            'color_bootstrap': 'warning',
            'descripcion': 'Practica antes de las 8 AM',
            'condicion': 'horario_matutino'
        },
        'nocturno': {
            'nombre': 'Nocturno',
            'icono': '🌙',
            'color_bootstrap': 'dark',
            'descripcion': 'Practica después de las 10 PM',
            'condicion': 'horario_nocturno'
        },
        'social': {
            'nombre': 'Social',
            'icono': '🤝',
            'color_bootstrap': 'info',
            'descripcion': 'Comparte 5 oraciones en redes',
            'condicion': 'compartido >= 5'
        }
    }
    
    # Configuración de XP por acción
    XP_CONFIG = {
        'ejercicio_facil': 10,
        'ejercicio_medio': 20,
        'ejercicio_dificil': 30,
        'flashcard_estudiada': 5,
        'oracion_guardada': 15,
        'racha_bonus': 50,
        'primer_ejercicio_dia': 25,
        'logro_desbloqueado': 100
    }
    
    # Configuración de colores Bootstrap para temas
    COLORES_TEMA = {
        'light': {
            'fondo': 'bg-light',
            'texto': 'text-dark',
            'navbar': 'navbar-light bg-primary',
            'card': 'bg-white',
            'borde': 'border-light'
        },
        'dark': {
            'fondo': 'bg-dark',
            'texto': 'text-white',
            'navbar': 'navbar-dark bg-dark',
            'card': 'bg-secondary',
            'borde': 'border-dark'
        },
        'auto': {
            'fondo': 'bg-auto',
            'texto': 'text-auto',
            'navbar': 'navbar-auto',
            'card': 'bg-auto',
            'borde': 'border-auto'
        }
    }
    
    # Configuración de notificaciones
    NOTIFICACIONES = {
        'duracion': 5000,  # milisegundos
        'posicion': 'top-right',
        'max_visible': 3
    }
    
    # Configuración de paginación
    ITEMS_POR_PAGINA = 10
    
    # Configuración de caché
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav'}
