import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario:
    def __init__(self, id=None, nombre=None, email=None, password=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.fecha_registro = datetime.now().isoformat()
        self.estadisticas = {
            'ejercicios_completados': 0,
            'respuestas_correctas': 0,
            'rachas': {
                'actual': 0,
                'maxima': 0
            },
            'puntos': 0,
            'medallas': [],
            'estrellas': 0,
            'por_categoria': {
                'Comas': {'intentos': 0, 'correctos': 0},
                'Paréntesis': {'intentos': 0, 'correctos': 0},
                'Rayas': {'intentos': 0, 'correctos': 0},
                'Geográficos': {'intentos': 0, 'correctos': 0},
                'Siglas': {'intentos': 0, 'correctos': 0}
            },
            'flashcards_completadas': 0,
            'ejemplos_creados': 0,
            'logros': []
        }
        self.historial = []
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'password_hash': self.password_hash,
            'fecha_registro': self.fecha_registro,
            'estadisticas': self.estadisticas,
            'historial': self.historial
        }
    
    @staticmethod
    def from_dict(data):
        usuario = Usuario()
        usuario.id = data.get('id')
        usuario.nombre = data.get('nombre')
        usuario.email = data.get('email')
        usuario.password_hash = data.get('password_hash')
        usuario.fecha_registro = data.get('fecha_registro')
        usuario.estadisticas = data.get('estadisticas', {})
        usuario.historial = data.get('historial', [])
        return usuario

class SistemaMedallas:
    def __init__(self, config):
        self.medallas = config.MEDALLAS
        self.puntos_config = config.PUNTOS
    
    def verificar_logros(self, usuario):
        stats = usuario.estadisticas
        nuevos_logros = []
        
        # Verificar medallas por ejercicios
        for medalla, requisitos in self.medallas.items():
            if (stats['ejercicios_completados'] >= requisitos['ejercicios'] and 
                stats['respuestas_correctas'] >= requisitos['correctos'] and
                medalla not in stats['medallas']):
                stats['medallas'].append(medalla)
                nuevos_logros.append(f"¡Has obtenido la medalla de {medalla}!")
        
        # Verificar rachas
        if stats['rachas']['actual'] >= 3 and 'racha_3' not in stats['logros']:
            stats['logros'].append('racha_3')
            stats['puntos'] += self.puntos_config['racha_3']
            nuevos_logros.append("¡Logro desbloqueado: Racha de 3!")
        
        if stats['rachas']['actual'] >= 5 and 'racha_5' not in stats['logros']:
            stats['logros'].append('racha_5')
            stats['puntos'] += self.puntos_config['racha_5']
            nuevos_logros.append("¡Logro desbloqueado: Racha de 5!")
        
        if stats['rachas']['actual'] >= 10 and 'racha_10' not in stats['logros']:
            stats['logros'].append('racha_10')
            stats['puntos'] += self.puntos_config['racha_10']
            nuevos_logros.append("¡Logro desbloqueado: Racha de 10!")
        
        # Verificar categorías dominadas
        for cat, datos in stats['por_categoria'].items():
            if datos['intentos'] >= 10 and datos['correctos'] >= 8:
                logro = f"maestro_{cat.lower()}"
                if logro not in stats['logros']:
                    stats['logros'].append(logro)
                    stats['puntos'] += 50
                    nuevos_logros.append(f"¡Maestro en {cat}!")
        
        # Calcular estrellas (1 estrella por cada 100 puntos)
        stats['estrellas'] = stats['puntos'] // 100
        
        return nuevos_logros
    
    def registrar_ejercicio(self, usuario, correcto, categoria):
        stats = usuario.estadisticas
        
        # Actualizar contadores
        stats['ejercicios_completados'] += 1
        stats['puntos'] += self.puntos_config['ejercicio_completado']
        
        if correcto:
            stats['respuestas_correctas'] += 1
            stats['puntos'] += self.puntos_config['respuesta_correcta']
            stats['rachas']['actual'] += 1
            
            # Actualizar récord de racha
            if stats['rachas']['actual'] > stats['rachas']['maxima']:
                stats['rachas']['maxima'] = stats['rachas']['actual']
            
            # Actualizar estadísticas por categoría
            if categoria in stats['por_categoria']:
                stats['por_categoria'][categoria]['intentos'] += 1
                stats['por_categoria'][categoria]['correctos'] += 1
        else:
            stats['rachas']['actual'] = 0
            if categoria in stats['por_categoria']:
                stats['por_categoria'][categoria]['intentos'] += 1
        
        # Registrar en historial
        usuario.historial.append({
            'fecha': datetime.now().isoformat(),
            'tipo': 'ejercicio',
            'correcto': correcto,
            'categoria': categoria,
            'puntos_ganados': self.puntos_config['ejercicio_completado'] + 
                             (self.puntos_config['respuesta_correcta'] if correcto else 0)
        })
        
        # Verificar nuevos logros
        nuevos_logros = self.verificar_logros(usuario)
        
        return nuevos_logros
    
    def registrar_flashcard(self, usuario):
        stats = usuario.estadisticas
        stats['flashcards_completadas'] += 1
        stats['puntos'] += self.puntos_config['flashcard_completada']
        
        usuario.historial.append({
            'fecha': datetime.now().isoformat(),
            'tipo': 'flashcard',
            'puntos_ganados': self.puntos_config['flashcard_completada']
        })
    
    def registrar_ejemplo_creado(self, usuario):
        stats = usuario.estadisticas
        stats['ejemplos_creados'] += 1
        stats['puntos'] += self.puntos_config['ejemplo_creado']
        
        usuario.historial.append({
            'fecha': datetime.now().isoformat(),
            'tipo': 'ejemplo_creado',
            'puntos_ganados': self.puntos_config['ejemplo_creado']
        })
