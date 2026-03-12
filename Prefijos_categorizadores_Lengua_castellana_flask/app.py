from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave-secreta-desarrollo-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecosistema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['SESSION_PROTECTION'] = 'strong'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
login_manager.login_message_category = 'info'

# Modelos de Base de Datos
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    nivel = db.Column(db.Integer, default=1)
    puntos = db.Column(db.Integer, default=0)
    racha = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text, default='')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ejemplos = db.relationship('Ejemplo', backref='autor', lazy=True)
    progresos = db.relationship('Progreso', backref='usuario', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Palabra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    palabra = db.Column(db.String(100), nullable=False)
    base = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    tipo_prefijo = db.Column(db.String(50))
    dificultad = db.Column(db.Integer, default=1)

class Ejemplo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    palabra_id = db.Column(db.Integer, db.ForeignKey('palabra.id'))
    oracion_simple = db.Column(db.Text, nullable=False)
    oracion_compuesta = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    validado = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer, default=0)

class Progreso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    palabra_id = db.Column(db.Integer, db.ForeignKey('palabra.id'))
    aciertos = db.Column(db.Integer, default=0)
    intentos = db.Column(db.Integer, default=0)
    ultima_practica = db.Column(db.DateTime, default=datetime.utcnow)

class Logro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    icono = db.Column(db.String(50))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))

# Datos iniciales
def init_db():
    db.create_all()
    
    if Palabra.query.count() == 0:
        palabras_iniciales = [
            {"palabra": "polisílabo", "base": "sílaba", "categoria": "adjetivo", "tipo_prefijo": "cuantitativo", "dificultad": 2},
            {"palabra": "multicolor", "base": "color", "categoria": "adjetivo", "tipo_prefijo": "cuantitativo", "dificultad": 1},
            {"palabra": "pluricelular", "base": "célula", "categoria": "adjetivo", "tipo_prefijo": "cuantitativo", "dificultad": 3},
            {"palabra": "monocromo", "base": "cromo", "categoria": "adjetivo", "tipo_prefijo": "cuantitativo", "dificultad": 2},
            {"palabra": "bicéfalo", "base": "cabeza", "categoria": "adjetivo", "tipo_prefijo": "cuantitativo", "dificultad": 2},
            {"palabra": "tricolor", "base": "color", "categoria": "adjetivo", "tipo_prefijo": "cuantitativo", "dificultad": 1},
            {"palabra": "antinatural", "base": "naturaleza", "categoria": "adjetivo", "tipo_prefijo": "negación", "dificultad": 2},
            {"palabra": "extraterrestre", "base": "terrestre", "categoria": "adjetivo", "tipo_prefijo": "posición", "dificultad": 3},
            {"palabra": "sobrenatural", "base": "naturaleza", "categoria": "adjetivo", "tipo_prefijo": "posición", "dificultad": 3},
            {"palabra": "subcutáneo", "base": "piel", "categoria": "adjetivo", "tipo_prefijo": "posición", "dificultad": 4},
        ]
        
        for p in palabras_iniciales:
            palabra = Palabra(**p)
            db.session.add(palabra)
        
        # Crear usuario demo
        demo = Usuario(username='demo', email='demo@ejemplo.com')
        demo.set_password('demo123')
        db.session.add(demo)
        
        db.session.commit()

# Funciones auxiliares
def calcular_progreso_categoria(usuario_id, tipo):
    total = Palabra.query.filter_by(tipo_prefijo=tipo).count()
    if total == 0:
        return 0
    progresos = Progreso.query.join(Palabra).filter(
        Progreso.usuario_id == usuario_id,
        Palabra.tipo_prefijo == tipo
    ).all()
    completados = sum(1 for p in progresos if p.aciertos > 0)
    return int((completados / total) * 100)

def calcular_logros(usuario_id):
    logros_usuario = Logro.query.filter_by(usuario_id=usuario_id).all()
    return [
        {
            'nombre': l.nombre,
            'descripcion': l.descripcion,
            'icono': l.icono,
            'fecha': l.fecha.strftime('%d/%m/%Y')
        } for l in logros_usuario
    ]

def obtener_ranking():
    return Usuario.query.order_by(Usuario.puntos.desc()).limit(10).all()

def verificar_logros(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    progresos = Progreso.query.filter_by(usuario_id=usuario_id).count()
    
    if progresos >= 10 and not Logro.query.filter_by(usuario_id=usuario_id, nombre='Aprendiz Inicial').first():
        logro = Logro(
            usuario_id=usuario_id,
            nombre='Aprendiz Inicial',
            descripcion='Completaste 10 ejercicios',
            icono='🌟'
        )
        db.session.add(logro)
    
    if usuario.racha >= 7 and not Logro.query.filter_by(usuario_id=usuario_id, nombre='En Racha').first():
        logro = Logro(
            usuario_id=usuario_id,
            nombre='En Racha',
            descripcion='7 respuestas correctas consecutivas',
            icono='🔥'
        )
        db.session.add(logro)
    
    db.session.commit()

# Rutas principales
@app.route('/')
def index():
    stats = {
        'usuarios': Usuario.query.count(),
        'ejemplos': Ejemplo.query.count(),
        'palabras': Palabra.query.count()
    }
    return render_template('index.html', stats=stats)

@app.route('/teoria')
def teoria():
    prefijos_por_tipo = {
        'cuantitativos': Palabra.query.filter_by(tipo_prefijo='cuantitativo').all(),
        'negacion': Palabra.query.filter_by(tipo_prefijo='negación').all(),
        'posicion': Palabra.query.filter_by(tipo_prefijo='posición').all()
    }
    return render_template('teoria.html', prefijos=prefijos_por_tipo)

@app.route('/practica')
@login_required
def practica():
    nivel_usuario = current_user.nivel
    palabras_disponibles = Palabra.query.filter(Palabra.dificultad <= nivel_usuario).all()
    return render_template('practica.html', palabras=palabras_disponibles)

@app.route('/practica-avanzada')
@login_required
def practica_avanzada():
    return render_template('practica_avanzada.html')

@app.route('/practica-completa')
@login_required
def practica_completa():
    return render_template('practica_completa.html')

@app.route('/flashcards')
@login_required
def flashcards():
    return render_template('flashcards.html')

@app.route('/dashboard')
@login_required
def dashboard():
    progreso = Progreso.query.filter_by(usuario_id=current_user.id).all()
    ejercicios_completados = len(progreso)
    
    stats = {
        'total_puntos': current_user.puntos,
        'ejercicios_completados': ejercicios_completados,
        'racha_actual': current_user.racha,
        'nivel': current_user.nivel,
        'cuantitativos': calcular_progreso_categoria(current_user.id, 'cuantitativo'),
        'negacion': calcular_progreso_categoria(current_user.id, 'negación'),
        'posicion': calcular_progreso_categoria(current_user.id, 'posición'),
        'logros': Logro.query.filter_by(usuario_id=current_user.id).count()
    }
    
    logros_recientes = Logro.query.filter_by(usuario_id=current_user.id).order_by(Logro.fecha.desc()).limit(3).all()
    actividad_reciente = []
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         logros_recientes=logros_recientes,
                         actividad_reciente=actividad_reciente,
                         proximos_logros=[])

@app.route('/logros')
@login_required
def logros():
    logros_usuario = calcular_logros(current_user.id)
    ranking = obtener_ranking()
    return render_template('logros.html', logros=logros_usuario, ranking=ranking)

@app.route('/creacion', methods=['GET', 'POST'])
@login_required
def creacion():
    if request.method == 'POST':
        palabra_id = request.form.get('palabra_id')
        oracion_simple = request.form.get('oracion_simple')
        oracion_compuesta = request.form.get('oracion_compuesta')
        
        if palabra_id and oracion_simple and oracion_compuesta:
            ejemplo = Ejemplo(
                usuario_id=current_user.id,
                palabra_id=palabra_id,
                oracion_simple=oracion_simple,
                oracion_compuesta=oracion_compuesta
            )
            
            db.session.add(ejemplo)
            db.session.commit()
            
            flash('Ejemplo guardado correctamente', 'success')
            return redirect(url_for('creacion', success=True))
    
    palabras = Palabra.query.all()
    ejemplos_usuario = Ejemplo.query.filter_by(usuario_id=current_user.id).order_by(Ejemplo.fecha.desc()).all()
    
    return render_template('creacion.html', palabras=palabras, ejemplos=ejemplos_usuario)

@app.route('/comunidad')
def comunidad():
    ejemplos_recientes = Ejemplo.query.filter_by(validado=True).order_by(Ejemplo.fecha.desc()).limit(20).all()
    top_usuarios = Usuario.query.order_by(Usuario.puntos.desc()).limit(10).all()
    
    stats = {
        'total_ejemplos': Ejemplo.query.count(),
        'usuarios_activos': Usuario.query.count(),
        'validados': Ejemplo.query.filter_by(validado=True).count(),
        'total_likes': db.session.query(db.func.sum(Ejemplo.likes)).scalar() or 0,
        'cuantitativos': Palabra.query.filter_by(tipo_prefijo='cuantitativo').count(),
        'negacion': Palabra.query.filter_by(tipo_prefijo='negación').count(),
        'posicion': Palabra.query.filter_by(tipo_prefijo='posición').count()
    }
    
    actividad_reciente = []
    
    return render_template('comunidad.html', 
                         ejemplos=ejemplos_recientes, 
                         top_usuarios=top_usuarios,
                         stats=stats,
                         actividad_reciente=actividad_reciente)

@app.route('/perfil')
@login_required
def perfil():
    stats = {
        'total_puntos': current_user.puntos,
        'ejercicios_completados': Progreso.query.filter_by(usuario_id=current_user.id).count(),
        'precision': 0,
        'logros': Logro.query.filter_by(usuario_id=current_user.id).count(),
        'cuantitativos': calcular_progreso_categoria(current_user.id, 'cuantitativo'),
        'negacion': calcular_progreso_categoria(current_user.id, 'negación'),
        'posicion': calcular_progreso_categoria(current_user.id, 'posición')
    }
    
    logros_recientes = Logro.query.filter_by(usuario_id=current_user.id).order_by(Logro.fecha.desc()).limit(5).all()
    actividad_reciente = []
    
    return render_template('perfil.html', 
                         stats=stats, 
                         logros_recientes=logros_recientes,
                         actividad_reciente=actividad_reciente)

@app.route('/api/palabra-aleatoria')
@login_required
def palabra_aleatoria():
    nivel = current_user.nivel
    palabras = Palabra.query.filter(Palabra.dificultad <= nivel).all()
    if palabras:
        palabra = random.choice(palabras)
        return jsonify({
            'id': palabra.id,
            'palabra': palabra.palabra,
            'base': palabra.base,
            'categoria': palabra.categoria
        })
    return jsonify({'error': 'No hay palabras disponibles'}), 404

@app.route('/api/verificar-respuesta', methods=['POST'])
@login_required
def verificar_respuesta():
    data = request.json
    palabra_id = data.get('palabra_id')
    respuesta = data.get('respuesta', '').lower().strip()
    
    palabra = Palabra.query.get(palabra_id)
    progreso = Progreso.query.filter_by(
        usuario_id=current_user.id,
        palabra_id=palabra_id
    ).first()
    
    if not progreso:
        progreso = Progreso(
            usuario_id=current_user.id,
            palabra_id=palabra_id
        )
        db.session.add(progreso)
    
    progreso.intentos += 1
    correcto = respuesta == palabra.palabra.lower()
    
    if correcto:
        progreso.aciertos += 1
        current_user.puntos += 10
        current_user.racha += 1
        
        if current_user.racha % 3 == 0 and current_user.nivel < 5:
            current_user.nivel += 1
    else:
        current_user.racha = 0
    
    progreso.ultima_practica = datetime.utcnow()
    db.session.commit()
    
    verificar_logros(current_user.id)
    
    return jsonify({
        'correcto': correcto,
        'palabra_correcta': palabra.palabra,
        'puntos': current_user.puntos,
        'nivel': current_user.nivel,
        'racha': current_user.racha
    })

@app.route('/api/guardar-progreso', methods=['POST'])
@login_required
def guardar_progreso():
    data = request.json
    current_user.puntos = data.get('puntos', current_user.puntos)
    current_user.racha = data.get('racha', current_user.racha)
    
    db.session.commit()
    verificar_logros(current_user.id)
    
    return jsonify({'status': 'ok'})

@app.route('/api/like-ejemplo/<int:ejemplo_id>', methods=['POST'])
@login_required
def like_ejemplo(ejemplo_id):
    ejemplo = Ejemplo.query.get_or_404(ejemplo_id)
    ejemplo.likes += 1
    db.session.commit()
    return jsonify({'likes': ejemplo.likes})

@app.route('/api/actualizar-perfil', methods=['POST'])
@login_required
def actualizar_perfil():
    data = request.json
    current_user.username = data.get('username', current_user.username)
    current_user.email = data.get('email', current_user.email)
    current_user.bio = data.get('bio', current_user.bio)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/cambiar-password', methods=['POST'])
@login_required
def cambiar_password():
    data = request.json
    if current_user.check_password(data['current']):
        current_user.set_password(data['new'])
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Contraseña actual incorrecta'})

# Autenticación
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('registro'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return redirect(url_for('registro'))
        
        usuario = Usuario(username=username, email=email)
        usuario.set_password(password)
        
        db.session.add(usuario)
        db.session.commit()
        
        login_user(usuario)
        flash('Registro exitoso. ¡Bienvenido!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and usuario.check_password(password):
            login_user(usuario, remember=True)
            next_page = request.args.get('next')
            flash(f'¡Bienvenido de nuevo, {usuario.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
        flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
