from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import json
from config import Config

db = SQLAlchemy()

# Modelo de Usuario
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Estadísticas de progreso
    xp = db.Column(db.Integer, default=0)
    ejercicios_completados = db.Column(db.Integer, default=0)
    ejercicios_correctos = db.Column(db.Integer, default=0)
    ejercicios_incorrectos = db.Column(db.Integer, default=0)
    racha_actual = db.Column(db.Integer, default=0)
    racha_maxima = db.Column(db.Integer, default=0)
    tiempo_total = db.Column(db.Integer, default=0)  # en segundos
    nivel_actual = db.Column(db.String(50), default='principiante')
    nivel_id = db.Column(db.Integer, default=1)
    
    # Estadísticas de flashcards
    flashcards_estudiadas = db.Column(db.Integer, default=0)
    flashcards_dominadas = db.Column(db.Integer, default=0)
    
    # Estadísticas de oraciones
    oraciones_guardadas = db.Column(db.Integer, default=0)
    oraciones_compartidas = db.Column(db.Integer, default=0)
    oraciones_publicas = db.Column(db.Integer, default=0)
    
    # Preferencias de usuario
    theme_preference = db.Column(db.String(10), default='light')
    bootstrap_theme = db.Column(db.String(50), default='default')
    font_size = db.Column(db.String(10), default='medium')
    notifications_enabled = db.Column(db.Boolean, default=True)
    sound_enabled = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(10), default='es')
    
    # Logros y medallas
    ultimo_logro = db.Column(db.DateTime, nullable=True)
    logros_totales = db.Column(db.Integer, default=0)
    medallas_totales = db.Column(db.Integer, default=0)
    estrellas_totales = db.Column(db.Integer, default=0)
    
    # Relaciones
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade='all, delete-orphan')
    sentences = db.relationship('UserSentence', backref='user', lazy=True, cascade='all, delete-orphan')
    exercise_records = db.relationship('UserExercise', backref='user', lazy=True, cascade='all, delete-orphan')
    flashcard_studies = db.relationship('UserFlashCard', backref='user', lazy=True, cascade='all, delete-orphan')
    daily_stats = db.relationship('DailyStat', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('UserGoal', backref='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def get_achievements_ids(self):
        return [a.achievement_id for a in self.achievements]
    
    def get_achievements_count(self):
        return len(self.achievements)
    
    def add_achievement(self, achievement_id):
        if achievement_id not in self.get_achievements_ids():
            achievement = Achievement.query.get(achievement_id)
            if achievement:
                user_achievement = UserAchievement(
                    user_id=self.id,
                    achievement_id=achievement_id
                )
                db.session.add(user_achievement)
                self.ultimo_logro = datetime.utcnow()
                self.logros_totales += 1
                self.xp += achievement.xp_recompensa
                
                # Crear notificación
                notif = Notification(
                    user_id=self.id,
                    tipo='logro',
                    titulo='¡Nuevo logro desbloqueado!',
                    mensaje=f"Has obtenido el logro: {achievement.nombre}",
                    icono=achievement.icono
                )
                db.session.add(notif)
                db.session.commit()
                return True
        return False
    
    def get_nivel_info(self):
        """Obtiene información del nivel actual con colores Bootstrap"""
        from data.niveles import NIVELES_DATA
        
        nivel = self.nivel_actual
        niveles = {n['nombre'].lower(): n for n in NIVELES_DATA['niveles']}
        
        if nivel not in niveles:
            nivel = 'principiante'
        
        nivel_data = niveles[nivel]
        
        # Calcular progreso al siguiente nivel
        niveles_lista = list(niveles.keys())
        idx_actual = niveles_lista.index(nivel)
        
        if idx_actual < len(niveles_lista) - 1:
            siguiente_nivel = niveles_lista[idx_actual + 1]
            xp_actual_nivel = niveles[nivel]['xp_requerido']
            xp_siguiente_nivel = niveles[siguiente_nivel]['xp_requerido']
            xp_en_nivel = self.xp - xp_actual_nivel
            xp_necesario = xp_siguiente_nivel - xp_actual_nivel
            progreso = int((xp_en_nivel / xp_necesario) * 100) if xp_necesario > 0 else 0
            siguiente_nivel_data = niveles[siguiente_nivel]
        else:
            progreso = 100
            siguiente_nivel_data = nivel_data
        
        return {
            'actual': nivel,
            'id': nivel_data['id'],
            'nombre': nivel_data['nombre'],
            'siguiente': siguiente_nivel_data['nombre'] if idx_actual < len(niveles_lista) - 1 else nivel,
            'progreso': progreso,
            'color_bootstrap': nivel_data['color_bootstrap'],
            'color_hex': nivel_data['color_hex'],
            'icono': nivel_data['icono'],
            'icono_bootstrap': nivel_data['icono_bootstrap'],
            'titulo': nivel_data['nombre'],
            'descripcion': nivel_data['descripcion'],
            'objetivos': nivel_data['objetivos'],
            'xp_requerido': nivel_data['xp_requerido'],
            'xp_maximo': nivel_data['xp_maximo'],
            'recompensas': nivel_data['recompensas']
        }
    
    def update_nivel(self):
        """Actualiza el nivel del usuario basado en su XP"""
        from data.niveles import NIVELES_DATA
        
        for nivel in NIVELES_DATA['niveles']:
            if self.xp >= nivel['xp_requerido']:
                self.nivel_actual = nivel['nombre'].lower()
                self.nivel_id = nivel['id']
        
        db.session.commit()
    
    def get_stats(self):
        """Obtiene estadísticas completas del usuario"""
        accuracy = 0
        if self.ejercicios_completados > 0:
            accuracy = int((self.ejercicios_correctos / self.ejercicios_completados) * 100)
        
        nivel_info = self.get_nivel_info()
        
        # Calcular tiempo promedio por ejercicio
        tiempo_promedio = 0
        if self.ejercicios_completados > 0:
            tiempo_promedio = self.tiempo_total // self.ejercicios_completados
        
        return {
            'username': self.username,
            'email': self.email,
            'xp': self.xp,
            'ejercicios_completados': self.ejercicios_completados,
            'ejercicios_correctos': self.ejercicios_correctos,
            'ejercicios_incorrectos': self.ejercicios_incorrectos,
            'accuracy': accuracy,
            'racha_actual': self.racha_actual,
            'racha_maxima': self.racha_maxima,
            'tiempo_total': self.tiempo_total,
            'tiempo_promedio': tiempo_promedio,
            'flashcards_estudiadas': self.flashcards_estudiadas,
            'flashcards_dominadas': self.flashcards_dominadas,
            'oraciones_guardadas': self.oraciones_guardadas,
            'logros_totales': self.logros_totales,
            'medallas_totales': self.medallas_totales,
            'estrellas_totales': self.estrellas_totales,
            'nivel': nivel_info,
            'ultimo_acceso': self.last_active.strftime('%d/%m/%Y %H:%M') if self.last_active else None,
            'fecha_registro': self.created_at.strftime('%d/%m/%Y'),
            'dias_activo': (datetime.utcnow().date() - self.created_at.date()).days
        }
    
    def get_daily_progress(self, days=7):
        """Obtiene el progreso diario de los últimos días"""
        hoy = datetime.utcnow().date()
        stats = []
        
        for i in range(days-1, -1, -1):
            dia = hoy - timedelta(days=i)
            stat = DailyStat.query.filter_by(
                user_id=self.id,
                date=dia
            ).first()
            
            if stat:
                stats.append({
                    'fecha': dia.strftime('%d/%m'),
                    'ejercicios': stat.ejercicios,
                    'flashcards': stat.flashcards,
                    'xp_ganado': stat.xp_ganado,
                    'tiempo_activo': stat.tiempo_activo
                })
            else:
                stats.append({
                    'fecha': dia.strftime('%d/%m'),
                    'ejercicios': 0,
                    'flashcards': 0,
                    'xp_ganado': 0,
                    'tiempo_activo': 0
                })
        
        return stats
    
    def update_daily_stat(self, ejercicios=0, flashcards=0, xp=0, tiempo=0):
        """Actualiza las estadísticas diarias"""
        hoy = datetime.utcnow().date()
        stat = DailyStat.query.filter_by(
            user_id=self.id,
            date=hoy
        ).first()
        
        if not stat:
            stat = DailyStat(
                user_id=self.id,
                date=hoy,
                ejercicios=ejercicios,
                flashcards=flashcards,
                xp_ganado=xp,
                tiempo_activo=tiempo
            )
            db.session.add(stat)
        else:
            stat.ejercicios += ejercicios
            stat.flashcards += flashcards
            stat.xp_ganado += xp
            stat.tiempo_activo += tiempo
        
        db.session.commit()
    
    def add_notification(self, tipo, titulo, mensaje, icono=None):
        """Añade una notificación para el usuario"""
        notif = Notification(
            user_id=self.id,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            icono=icono
        )
        db.session.add(notif)
        db.session.commit()
    
    def get_unread_notifications(self):
        """Obtiene notificaciones no leídas"""
        return Notification.query.filter_by(
            user_id=self.id,
            leida=False
        ).order_by(Notification.created_at.desc()).all()
    
    def to_dict(self):
        """Convierte el usuario a diccionario para APIs"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'xp': self.xp,
            'nivel': self.nivel_actual,
            'racha': self.racha_actual,
            'logros': self.logros_totales
        }


# Modelo de Logros
class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    icono = db.Column(db.String(10), nullable=False)
    color_bootstrap = db.Column(db.String(20), default='primary')
    descripcion = db.Column(db.String(200), nullable=False)
    descripcion_larga = db.Column(db.Text)
    condicion = db.Column(db.String(200))
    xp_recompensa = db.Column(db.Integer, default=50)
    orden = db.Column(db.Integer, default=0)
    categoria = db.Column(db.String(50))
    
    users = db.relationship('UserAchievement', backref='achievement', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'icono': self.icono,
            'color': self.color_bootstrap,
            'descripcion': self.descripcion,
            'xp_recompensa': self.xp_recompensa,
            'categoria': self.categoria
        }


# Modelo de Logros de Usuario
class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.String(50), db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),)


# Modelo de Oraciones de Usuario
class UserSentence(db.Model):
    __tablename__ = 'user_sentences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sentence = db.Column(db.String(500), nullable=False)
    verb = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))
    is_public = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('user_sentences', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'sentence': self.sentence,
            'verb': self.verb,
            'category': self.category,
            'is_public': self.is_public,
            'likes': self.likes,
            'fecha': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'usuario': self.user.username if self.user else None
        }


# Modelo de Ejercicios de Usuario
class UserExercise(db.Model):
    __tablename__ = 'user_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, nullable=False)
    was_correct = db.Column(db.Boolean, nullable=False)
    tiempo = db.Column(db.Integer, default=0)  # tiempo en segundos
    xp_ganado = db.Column(db.Integer, default=0)
    dificultad = db.Column(db.String(20))
    categoria = db.Column(db.String(50))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('user_exercises', lazy=True))


# Modelo de Flashcards de Usuario
class UserFlashCard(db.Model):
    __tablename__ = 'user_flashcards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    flashcard_id = db.Column(db.Integer, nullable=False)
    fecha_estudio = db.Column(db.DateTime, default=datetime.utcnow)
    dificultad = db.Column(db.String(20))  # facil, medio, dificil
    veces_estudiado = db.Column(db.Integer, default=1)
    dominado = db.Column(db.Boolean, default=False)
    ultima_revision = db.Column(db.DateTime, default=datetime.utcnow)
    proxima_revision = db.Column(db.DateTime, nullable=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'flashcard_id', name='unique_user_flashcard'),)
    
    user = db.relationship('User', backref=db.backref('user_flashcards', lazy=True))
    
    def calcular_proxima_revision(self):
        """Calcula la próxima revisión según el sistema de repaso espaciado"""
        if self.dificultad == 'facil':
            dias = 7
        elif self.dificultad == 'medio':
            dias = 3
        else:
            dias = 1
        
        self.proxima_revision = datetime.utcnow() + timedelta(days=dias)
        db.session.commit()


# Modelo de Estadísticas Diarias
class DailyStat(db.Model):
    __tablename__ = 'daily_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    ejercicios = db.Column(db.Integer, default=0)
    flashcards = db.Column(db.Integer, default=0)
    xp_ganado = db.Column(db.Integer, default=0)
    tiempo_activo = db.Column(db.Integer, default=0)  # en minutos
    
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)
    
    user = db.relationship('User', backref=db.backref('daily_stats_rel', lazy=True))


# Modelo de Metas de Usuario
class UserGoal(db.Model):
    __tablename__ = 'user_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # ejercicios_dia, racha, xp_semana, flashcards
    cantidad = db.Column(db.Integer, nullable=False)
    progreso = db.Column(db.Integer, default=0)
    completada = db.Column(db.Boolean, default=False)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_limite = db.Column(db.DateTime, nullable=True)
    fecha_completada = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref=db.backref('user_goals', lazy=True))
    
    def actualizar_progreso(self, valor):
        """Actualiza el progreso de la meta"""
        self.progreso += valor
        if self.progreso >= self.cantidad and not self.completada:
            self.completada = True
            self.fecha_completada = datetime.utcnow()
            
            # Recompensa por completar meta
            self.user.xp += 50
            self.user.add_notification(
                'meta',
                '¡Meta completada!',
                f"Has completado tu meta de {self.tipo}",
                '🎯'
            )
        
        db.session.commit()


# Modelo de Notificaciones
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo = db.Column(db.String(50))  # logro, meta, recordatorio, sistema
    titulo = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    icono = db.Column(db.String(10))
    leida = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('user_notifications', lazy=True))
    
    def marcar_como_leida(self):
        self.leida = True
        db.session.commit()


# Modelo de Ejercicio (para caché)
class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    pregunta = db.Column(db.String(500), nullable=False)
    opciones = db.Column(db.Text, nullable=False)  # JSON string
    correcta = db.Column(db.Integer, nullable=False)
    explicacion = db.Column(db.String(500), nullable=False)
    dificultad = db.Column(db.String(20), default='intermedio')
    categoria = db.Column(db.String(50))
    veces_usado = db.Column(db.Integer, default=0)
    veces_correcto = db.Column(db.Integer, default=0)
    porcentaje_acierto = db.Column(db.Float, default=0.0)
    
    def get_opciones(self):
        return json.loads(self.opciones)
    
    def actualizar_estadisticas(self, correcto):
        """Actualiza las estadísticas del ejercicio"""
        self.veces_usado += 1
        if correcto:
            self.veces_correcto += 1
        self.porcentaje_acierto = (self.veces_correcto / self.veces_usado) * 100
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'pregunta': self.pregunta,
            'opciones': self.get_opciones(),
            'dificultad': self.dificultad,
            'categoria': self.categoria,
            'porcentaje_acierto': self.porcentaje_acierto
        }


# Modelo de Flashcard (para caché)
class FlashCard(db.Model):
    __tablename__ = 'flashcards'
    
    id = db.Column(db.Integer, primary_key=True)
    termino = db.Column(db.String(100), nullable=False)
    definicion = db.Column(db.Text, nullable=False)
    ejemplo = db.Column(db.String(500))
    categoria = db.Column(db.String(50))
    imagen = db.Column(db.String(10))
    dificultad = db.Column(db.String(20), default='intermedio')
    veces_estudiado = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'termino': self.termino,
            'definicion': self.definicion,
            'ejemplo': self.ejemplo,
            'categoria': self.categoria,
            'imagen': self.imagen,
            'dificultad': self.dificultad
        }


# Modelo de Comentarios en Oraciones Públicas
class SentenceComment(db.Model):
    __tablename__ = 'sentence_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    sentence_id = db.Column(db.Integer, db.ForeignKey('user_sentences.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comentario = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sentence = db.relationship('UserSentence', backref=db.backref('comments', lazy=True))
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'comentario': self.comentario,
            'usuario': self.user.username,
            'fecha': self.created_at.strftime('%d/%m/%Y %H:%M')
        }


# Modelo de Likes en Oraciones
class SentenceLike(db.Model):
    __tablename__ = 'sentence_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    sentence_id = db.Column(db.Integer, db.ForeignKey('user_sentences.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('sentence_id', 'user_id', name='unique_sentence_like'),)
    
    sentence = db.relationship('UserSentence', backref=db.backref('likes_rel', lazy=True))
    user = db.relationship('User', backref=db.backref('likes', lazy=True))
