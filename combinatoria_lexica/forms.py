from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, IntegerField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileSize
import re
from datetime import datetime

class LoginForm(FlaskForm):
    """Formulario de inicio de sesión con validación mejorada"""
    username = StringField('Usuario o Email', validators=[
        DataRequired(message='Este campo es obligatorio'),
        Length(min=3, max=80, message='Debe tener entre 3 y 80 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    remember = BooleanField('Recordarme')
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # Añadir clases Bootstrap a los campos
        self.username.render_kw = {'class': 'form-control', 'placeholder': 'Ingresa tu usuario o email'}
        self.password.render_kw = {'class': 'form-control', 'placeholder': 'Ingresa tu contraseña'}
        self.remember.render_kw = {'class': 'form-check-input'}

class RegisterForm(FlaskForm):
    """Formulario de registro con validaciones robustas"""
    username = StringField('Nombre de Usuario', validators=[
        DataRequired(message='El nombre de usuario es obligatorio'),
        Length(min=3, max=20, message='El usuario debe tener entre 3 y 20 caracteres')
    ])
    email = EmailField('Correo Electrónico', validators=[
        DataRequired(message='El email es obligatorio'),
        Email(message='Ingresa un email válido'),
        Length(max=120, message='El email no puede exceder 120 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=6, max=50, message='La contraseña debe tener entre 6 y 50 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Debes confirmar tu contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    accept_terms = BooleanField('Acepto los términos y condiciones', validators=[
        DataRequired(message='Debes aceptar los términos para registrarte')
    ])
    
    def validate_username(self, username):
        """Validación personalizada para nombre de usuario"""
        # Solo permitir letras, números y guiones bajos
        if not re.match('^[a-zA-Z0-9_]+$', username.data):
            raise ValidationError('El usuario solo puede contener letras, números y guiones bajos')
        
        # No permitir palabras ofensivas (ejemplo básico)
        palabras_prohibidas = ['admin', 'root', 'superuser']
        if username.data.lower() in palabras_prohibidas:
            raise ValidationError('Este nombre de usuario no está disponible')
    
    def validate_email(self, email):
        """Validación de dominio de email"""
        dominios_permitidos = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com', 'icloud.com']
        dominio = email.data.split('@')[-1].lower()
        
        # Comentar si no quieres restringir dominios
        # if dominio not in dominios_permitidos:
        #     raise ValidationError('Solo se permiten correos de dominios comunes')
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.username.render_kw = {
            'class': 'form-control', 
            'placeholder': 'Elige un nombre de usuario',
            'pattern': '[a-zA-Z0-9_]+',
            'title': 'Solo letras, números y guiones bajos'
        }
        self.email.render_kw = {
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com',
            'type': 'email'
        }
        self.password.render_kw = {
            'class': 'form-control',
            'placeholder': 'Crea una contraseña segura',
            'minlength': '6'
        }
        self.confirm_password.render_kw = {
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña'
        }
        self.accept_terms.render_kw = {'class': 'form-check-input'}

class ProfileForm(FlaskForm):
    """Formulario para editar perfil de usuario"""
    username = StringField('Nombre de Usuario', validators=[
        Optional(),
        Length(min=3, max=20, message='El usuario debe tener entre 3 y 20 caracteres')
    ])
    email = EmailField('Correo Electrónico', validators=[
        Optional(),
        Email(message='Ingresa un email válido')
    ])
    current_password = PasswordField('Contraseña Actual', validators=[
        Optional(),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    new_password = PasswordField('Nueva Contraseña', validators=[
        Optional(),
        Length(min=6, message='La nueva contraseña debe tener al menos 6 caracteres')
    ])
    confirm_new_password = PasswordField('Confirmar Nueva Contraseña', validators=[
        EqualTo('new_password', message='Las contraseñas no coinciden')
    ])
    theme_preference = SelectField('Tema', choices=[
        ('light', 'Claro'),
        ('dark', 'Oscuro'),
        ('auto', 'Automático')
    ], validators=[Optional()])
    
    font_size = SelectField('Tamaño de Fuente', choices=[
        ('small', 'Pequeño'),
        ('medium', 'Mediano'),
        ('large', 'Grande')
    ], validators=[Optional()])
    
    notifications_enabled = BooleanField('Activar notificaciones')
    sound_enabled = BooleanField('Activar sonidos')
    
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.username.render_kw = {'class': 'form-control'}
        self.email.render_kw = {'class': 'form-control', 'type': 'email'}
        self.current_password.render_kw = {'class': 'form-control'}
        self.new_password.render_kw = {'class': 'form-control'}
        self.confirm_new_password.render_kw = {'class': 'form-control'}
        self.theme_preference.render_kw = {'class': 'form-select'}
        self.font_size.render_kw = {'class': 'form-select'}
        self.notifications_enabled.render_kw = {'class': 'form-check-input'}
        self.sound_enabled.render_kw = {'class': 'form-check-input'}

class SentenceForm(FlaskForm):
    """Formulario para guardar oraciones"""
    sentence = TextAreaField('Tu Oración', validators=[
        DataRequired(message='La oración no puede estar vacía'),
        Length(min=10, max=500, message='La oración debe tener entre 10 y 500 caracteres')
    ])
    category = SelectField('Categoría', choices=[
        ('', 'Selecciona una categoría...'),
        ('cotidiano', 'Uso Cotidiano'),
        ('literario', 'Uso Literario'),
        ('academico', 'Uso Académico'),
        ('creativo', 'Uso Creativo')
    ], validators=[DataRequired(message='Selecciona una categoría')])
    
    is_public = BooleanField('Compartir con la comunidad')
    
    def validate_sentence(self, sentence):
        """Validar que la oración tenga sentido"""
        if len(sentence.data.split()) < 3:
            raise ValidationError('La oración debe tener al menos 3 palabras')
        
        # Verificar que no sea solo repetición de caracteres
        if all(c == sentence.data[0] for c in sentence.data.replace(' ', '')):
            raise ValidationError('La oración no puede ser solo caracteres repetidos')
    
    def __init__(self, *args, **kwargs):
        super(SentenceForm, self).__init__(*args, **kwargs)
        self.sentence.render_kw = {
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Ejemplo: El águila subió majestuosamente al cielo...'
        }
        self.category.render_kw = {'class': 'form-select'}
        self.is_public.render_kw = {'class': 'form-check-input'}

class ExerciseFilterForm(FlaskForm):
    """Formulario para filtrar ejercicios"""
    dificultad = SelectField('Dificultad', choices=[
        ('todos', 'Todas las dificultades'),
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
        ('experto', 'Experto')
    ], validators=[Optional()])
    
    categoria = SelectField('Categoría', choices=[
        ('todas', 'Todas las categorías'),
        ('verbos_movimiento', 'Verbos de Movimiento'),
        ('metaforas', 'Metáforas'),
        ('restricciones', 'Restricciones'),
        ('economia', 'Economía'),
        ('social', 'Social'),
        ('naturaleza', 'Naturaleza'),
        ('ceremonial', 'Ceremonial')
    ], validators=[Optional()])
    
    busqueda = StringField('Buscar', validators=[Optional(), Length(max=100)])
    
    def __init__(self, *args, **kwargs):
        super(ExerciseFilterForm, self).__init__(*args, **kwargs)
        self.dificultad.render_kw = {'class': 'form-select'}
        self.categoria.render_kw = {'class': 'form-select'}
        self.busqueda.render_kw = {
            'class': 'form-control',
            'placeholder': 'Buscar ejercicios...'
        }

class FlashcardReviewForm(FlaskForm):
    """Formulario para revisar flashcards"""
    flashcard_id = IntegerField('ID de Flashcard', validators=[DataRequired()])
    dificultad = SelectField('¿Qué tan difícil fue?', choices=[
        ('facil', 'Fácil - Lo sabía bien'),
        ('medio', 'Medio - Tuve que pensar'),
        ('dificil', 'Difícil - No lo recordaba')
    ], validators=[DataRequired()])
    
    tiempo_estudio = IntegerField('Tiempo de estudio (segundos)', 
                                 validators=[Optional(), NumberRange(min=1, max=300)])
    
    dominado = BooleanField('Marcar como dominado')
    
    def __init__(self, *args, **kwargs):
        super(FlashcardReviewForm, self).__init__(*args, **kwargs)
        self.flashcard_id.render_kw = {'type': 'hidden'}
        self.dificultad.render_kw = {'class': 'form-select'}
        self.tiempo_estudio.render_kw = {'class': 'form-control', 'type': 'number'}
        self.dominado.render_kw = {'class': 'form-check-input'}

class ContactForm(FlaskForm):
    """Formulario de contacto"""
    nombre = StringField('Nombre', validators=[
        DataRequired(message='Por favor ingresa tu nombre'),
        Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')
    ])
    email = EmailField('Email', validators=[
        DataRequired(message='El email es obligatorio'),
        Email(message='Ingresa un email válido')
    ])
    asunto = StringField('Asunto', validators=[
        DataRequired(message='El asunto es obligatorio'),
        Length(min=5, max=100, message='El asunto debe tener entre 5 y 100 caracteres')
    ])
    mensaje = TextAreaField('Mensaje', validators=[
        DataRequired(message='El mensaje no puede estar vacío'),
        Length(min=10, max=1000, message='El mensaje debe tener entre 10 y 1000 caracteres')
    ])
    
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.nombre.render_kw = {'class': 'form-control', 'placeholder': 'Tu nombre'}
        self.email.render_kw = {'class': 'form-control', 'placeholder': 'tu@email.com'}
        self.asunto.render_kw = {'class': 'form-control', 'placeholder': 'Asunto del mensaje'}
        self.mensaje.render_kw = {
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Escribe tu mensaje aquí...'
        }

class AvatarUploadForm(FlaskForm):
    """Formulario para subir avatar"""
    avatar = FileField('Imagen de Perfil', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Solo se permiten imágenes'),
        FileSize(max_size=5 * 1024 * 1024, message='La imagen no puede superar los 5MB')
    ])
    
    def __init__(self, *args, **kwargs):
        super(AvatarUploadForm, self).__init__(*args, **kwargs)
        self.avatar.render_kw = {
            'class': 'form-control',
            'accept': 'image/*'
        }

class GoalForm(FlaskForm):
    """Formulario para establecer metas personales"""
    tipo_meta = SelectField('Tipo de Meta', choices=[
        ('ejercicios_dia', 'Ejercicios por día'),
        ('racha', 'Días de racha'),
        ('xp_semana', 'XP por semana'),
        ('flashcards', 'Flashcards estudiadas')
    ], validators=[DataRequired()])
    
    cantidad = IntegerField('Cantidad', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000, message='La cantidad debe estar entre 1 y 1000')
    ])
    
    fecha_limite = StringField('Fecha Límite', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(GoalForm, self).__init__(*args, **kwargs)
        self.tipo_meta.render_kw = {'class': 'form-select'}
        self.cantidad.render_kw = {
            'class': 'form-control',
            'type': 'number',
            'min': '1',
            'max': '1000'
        }
        self.fecha_limite.render_kw = {
            'class': 'form-control',
            'type': 'date'
        }
