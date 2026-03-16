from datetime import datetime, timedelta
from config import Config
import random
import re

def calcular_nivel(xp):
    """
    Calcula el nivel del usuario basado en su XP
    Retorna el nombre del nivel y su información
    """
    nivel_actual = 'principiante'
    for nivel, datos in Config.NIVELES.items():
        if xp >= datos['xp_requerido']:
            nivel_actual = nivel
        else:
            break
    
    return {
        'nombre': nivel_actual,
        'datos': Config.NIVELES[nivel_actual]
    }

def calcular_xp(dificultad, tiempo, es_correcto):
    """
    Calcula el XP ganado por un ejercicio
    """
    if not es_correcto:
        return 0
    
    # XP base por dificultad
    xp_base = {
        'principiante': Config.XP_CONFIG['ejercicio_facil'],
        'intermedio': Config.XP_CONFIG['ejercicio_medio'],
        'avanzado': Config.XP_CONFIG['ejercicio_dificil'],
        'experto': 50
    }.get(dificultad, Config.XP_CONFIG['ejercicio_medio'])
    
    # Bonus por tiempo (menos tiempo = más XP)
    tiempo_estimado = {
        'principiante': 30,
        'intermedio': 45,
        'avanzado': 60,
        'experto': 75
    }.get(dificultad, 45)
    
    if tiempo <= 0:
        return xp_base
    
    if tiempo <= tiempo_estimado * 0.5:
        bonus_tiempo = int(xp_base * 0.5)  # 50% bonus
    elif tiempo <= tiempo_estimado:
        bonus_tiempo = int(xp_base * 0.25)  # 25% bonus
    else:
        bonus_tiempo = 0
    
    return xp_base + bonus_tiempo

def verificar_logros(user):
    """
    Verifica si el usuario ha desbloqueado nuevos logros
    Retorna lista de nuevos logros desbloqueados
    """
    from models import Achievement
    
    nuevos_logros = []
    logros_actuales = user.get_achievements_ids()
    todos_logros = Achievement.query.all()
    
    # Obtener estadísticas del usuario
    stats = user.get_stats()
    
    for logro in todos_logros:
        if logro.id not in logros_actuales:
            if evaluar_condicion_logro(logro.id, user, stats):
                if user.add_achievement(logro.id):
                    # Añadir XP por logro
                    user.xp += Config.XP_CONFIG['logro_desbloqueado']
                    nuevos_logros.append(logro.id)
    
    return nuevos_logros

def evaluar_condicion_logro(logro_id, user, stats):
    """
    Evalúa si se cumple la condición para un logro específico
    """
    if logro_id == 'novato':
        return stats['ejercicios_completados'] >= 5
    
    elif logro_id == 'aprendiz':
        return stats['ejercicios_completados'] >= 20
    
    elif logro_id == 'experto':
        return stats['ejercicios_completados'] >= 50
    
    elif logro_id == 'racha5':
        return stats['racha_maxima'] >= 5
    
    elif logro_id == 'racha10':
        return stats['racha_maxima'] >= 10
    
    elif logro_id == 'precision':
        return (stats['ejercicios_completados'] >= 10 and 
                stats['accuracy'] == 100)
    
    elif logro_id == 'escritor':
        return len(user.sentences) >= 10
    
    elif logro_id == 'rapidez':
        # Verificar si tiene 10 ejercicios en menos de 30 segundos
        ejercicios_rapidos = [e for e in user.exercise_records 
                             if e.tiempo < 30 and e.was_correct]
        return len(ejercicios_rapidos) >= 10
    
    elif logro_id == 'dedicacion':
        return stats['ejercicios_completados'] >= 100
    
    elif logro_id == 'creatividad':
        return len(user.sentences) >= 20
    
    elif logro_id == 'coleccionista':
        return len(user.achievements) >= 10
    
    elif logro_id == 'estudioso':
        return user.flashcards_estudiadas >= 50
    
    elif logro_id == 'madrugador':
        # Verificar si practicó antes de las 8 AM
        hoy = datetime.now()
        ejercicios_temprano = [e for e in user.exercise_records 
                              if e.fecha.hour < 8 and 
                              e.fecha.date() == hoy.date()]
        return len(ejercicios_temprano) >= 1
    
    elif logro_id == 'nocturno':
        # Verificar si practicó después de las 10 PM
        hoy = datetime.now()
        ejercicios_noche = [e for e in user.exercise_records 
                           if e.fecha.hour >= 22 and 
                           e.fecha.date() == hoy.date()]
        return len(ejercicios_noche) >= 1
    
    return False

def generar_recomendaciones(user):
    """
    Genera recomendaciones personalizadas basadas en el progreso del usuario
    Retorna lista de recomendaciones con colores Bootstrap
    """
    recomendaciones = []
    stats = user.get_stats()
    
    # Recomendación por pocos ejercicios
    if stats['ejercicios_completados'] < 10:
        recomendaciones.append({
            'tipo': 'ejercicios',
            'mensaje': '¡Comienza con los ejercicios básicos!',
            'accion': '/ejercicios',
            'icono': '📝',
            'color': 'primary',
            'prioridad': 1
        })
    
    # Recomendación por precisión baja
    if stats['ejercicios_completados'] >= 10 and stats['accuracy'] < 60:
        recomendaciones.append({
            'tipo': 'estudio',
            'mensaje': 'Revisa las flashcards para mejorar tu precisión',
            'accion': '/flashcards',
            'icono': '📇',
            'color': 'warning',
            'prioridad': 2
        })
    
    # Recomendación por racha perdida
    if stats['racha_actual'] == 0 and stats['racha_maxima'] > 0:
        recomendaciones.append({
            'tipo': 'motivacion',
            'mensaje': '¡Recupera tu racha! Vuelve a practicar hoy',
            'accion': '/ejercicios',
            'icono': '🔥',
            'color': 'danger',
            'prioridad': 1
        })
    
    # Recomendación por nivel
    if stats['nivel']['actual'] == 'principiante' and stats['ejercicios_completados'] >= 20:
        recomendaciones.append({
            'tipo': 'nivel',
            'mensaje': '¡Estás listo para el nivel intermedio! Prueba ejercicios más difíciles',
            'accion': '/ejercicios?nivel=intermedio',
            'icono': '⬆️',
            'color': 'success',
            'prioridad': 3
        })
    
    # Recomendación de flashcards
    if user.flashcards_estudiadas < 20:
        recomendaciones.append({
            'tipo': 'flashcards',
            'mensaje': 'Amplía tu conocimiento con nuestras flashcards',
            'accion': '/flashcards',
            'icono': '🎴',
            'color': 'info',
            'prioridad': 2
        })
    
    # Recomendación de oraciones
    if len(user.sentences) < 5:
        recomendaciones.append({
            'tipo': 'creatividad',
            'mensaje': 'Guarda tus propias oraciones para practicar',
            'accion': '/practica',
            'icono': '✍️',
            'color': 'secondary',
            'prioridad': 3
        })
    
    # Recomendación de logros cercanos
    logros_cercanos = encontrar_logros_cercanos(user)
    for logro in logros_cercanos[:2]:  # Máximo 2 recomendaciones de logros
        recomendaciones.append({
            'tipo': 'logro',
            'mensaje': f'Estás cerca de desbloquear: {logro["nombre"]}',
            'accion': '/logros',
            'icono': '🏆',
            'color': 'warning',
            'prioridad': 2,
            'progreso': logro['progreso']
        })
    
    # Ordenar por prioridad
    recomendaciones.sort(key=lambda x: x['prioridad'])
    
    return recomendaciones

def encontrar_logros_cercanos(user):
    """
    Encuentra logros que el usuario está cerca de desbloquear
    """
    from models import Achievement
    
    logros_cercanos = []
    stats = user.get_stats()
    logros_actuales = user.get_achievements_ids()
    
    # Definir progreso para logros comunes
    progresos = {
        'novato': (stats['ejercicios_completados'], 5),
        'aprendiz': (stats['ejercicios_completados'], 20),
        'experto': (stats['ejercicios_completados'], 50),
        'racha5': (stats['racha_maxima'], 5),
        'racha10': (stats['racha_maxima'], 10),
        'escritor': (len(user.sentences), 10),
        'dedicacion': (stats['ejercicios_completados'], 100),
        'creatividad': (len(user.sentences), 20)
    }
    
    for logro_id, (actual, necesario) in progresos.items():
        if logro_id not in logros_actuales and necesario > 0:
            progreso = int((actual / necesario) * 100)
            if progreso >= 50 and progreso < 100:  # Logros con más del 50% de progreso
                logro = Achievement.query.get(logro_id)
                if logro:
                    logros_cercanos.append({
                        'id': logro_id,
                        'nombre': logro.nombre,
                        'progreso': progreso,
                        'actual': actual,
                        'necesario': necesario
                    })
    
    # Ordenar por progreso descendente
    logros_cercanos.sort(key=lambda x: x['progreso'], reverse=True)
    
    return logros_cercanos

def formatear_tiempo(segundos):
    """
    Formatea segundos a formato legible (mm:ss)
    """
    minutos = segundos // 60
    segs = segundos % 60
    return f"{minutos}:{segs:02d}"

def obtener_color_por_nivel(nivel):
    """
    Obtiene el color Bootstrap correspondiente a un nivel
    """
    colores = {
        'principiante': 'secondary',
        'intermedio': 'info',
        'avanzado': 'success',
        'experto': 'warning',
        'maestro': 'danger'
    }
    return colores.get(nivel, 'primary')

def obtener_icono_por_categoria(categoria):
    """
    Obtiene el icono Font Awesome para una categoría
    """
    iconos = {
        'verbos_movimiento': 'fa-arrows-up-down',
        'metaforas': 'fa-cloud',
        'restricciones': 'fa-ban',
        'ejemplos': 'fa-example',
        'economia': 'fa-chart-line',
        'social': 'fa-users',
        'naturaleza': 'fa-tree',
        'ceremonial': 'fa-flag'
    }
    return iconos.get(categoria, 'fa-circle')

def validar_oracion(oracion):
    """
    Valida que una oración tenga sentido y use verbos adecuados
    """
    if len(oracion) < 10:
        return False, "La oración es demasiado corta"
    
    if len(oracion) > 500:
        return False, "La oración es demasiado larga"
    
    # Lista de verbos de movimiento permitidos
    verbos_permitidos = ['subir', 'bajar', 'caer', 'levantar', 'izar', 
                        'arriar', 'ascender', 'descender', 'elevar', 'alzar']
    
    # Verificar si contiene al menos un verbo permitido
    contiene_verbo = any(verbo in oracion.lower() for verbo in verbos_permitidos)
    
    if not contiene_verbo:
        return False, "La oración debe incluir un verbo de movimiento"
    
    return True, "Oración válida"

def calcular_tendencia(estadisticas, dias=7):
    """
    Calcula la tendencia de progreso en los últimos días
    """
    if len(estadisticas) < 2:
        return 0
    
    ultimos = estadisticas[-dias:]
    if not ultimos:
        return 0
    
    # Calcular promedio móvil simple
    valores = [d['ejercicios'] for d in ultimos]
    if len(valores) < 2:
        return 0
    
    tendencia = (valores[-1] - valores[0]) / len(valores)
    
    # Normalizar a porcentaje
    if valores[0] > 0:
        tendencia_pct = (tendencia / valores[0]) * 100
    else:
        tendencia_pct = tendencia * 10
    
    return round(tendencia_pct, 1)

def obtener_mensaje_motivacional(racha, nivel):
    """
    Genera un mensaje motivacional basado en la racha y nivel del usuario
    """
    mensajes = {
        'principiante': [
            "¡Cada paso cuenta! Sigue así 🌱",
            "El conocimiento es poder, ¡sigue aprendiendo! 📚",
            "Los expertos fueron alguna vez principiantes 💪"
        ],
        'intermedio': [
            "¡Vas por buen camino! 🚀",
            "Dominando los conceptos paso a paso 🎯",
            "¡Sigue rompiendo tus propios récords! 🔥"
        ],
        'avanzado': [
            "¡Impresionante progreso! 🌟",
            "Cada vez más cerca de la maestría 👑",
            "Tu dedicación da frutos 🌳"
        ],
        'experto': [
            "¡Eres un ejemplo a seguir! 🏆",
            "El conocimiento fluye en ti 💫",
            "¡Ya eres todo un experto! ⚡"
        ],
        'maestro': [
            "¡Leyenda absoluta! 👑",
            "Maestro de la combinatoria léxica 🎓",
            "Tu sabiduría es inspiradora ✨"
        ]
    }
    
    if racha > 0:
        mensajes_racha = [
            f"¡Llevas {racha} días de racha! 🔥",
            f"Racha de {racha} días, ¡imparable! ⚡",
            f"{racha} días seguidos, ¡qué disciplina! 💪"
        ]
        return random.choice(mensajes_racha)
    
    nivel_mensajes = mensajes.get(nivel, mensajes['principiante'])
    return random.choice(nivel_mensajes)
