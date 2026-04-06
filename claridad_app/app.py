from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
import json
import os
import sqlite3
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clave_secreta_claridad_tecnica_2024'
app.config['UPLOAD_FOLDER'] = 'static/downloads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ==================== CONFIGURACIÓN ====================
DB_FILE = 'data/usuarios.db'
EJERCICIOS_FILE = 'data/ejercicios.json'
FLASHCARDS_FILE = 'data/flashcards.json'
CONFIG_FILE = 'data/config.json'

os.makedirs('data', exist_ok=True)
os.makedirs('static/downloads', exist_ok=True)
os.makedirs('templates/admin', exist_ok=True)

# ==================== FUNCIONES DE BASE DE DATOS ====================

def get_db():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializar la base de datos"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        avatar TEXT DEFAULT 'default.png',
        biografia TEXT,
        es_admin INTEGER DEFAULT 0,
        activo INTEGER DEFAULT 1
    )''')
    
    # Tabla de progreso de ejercicios
    cursor.execute('''CREATE TABLE IF NOT EXISTS progreso_ejercicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        ejercicio_id INTEGER NOT NULL,
        completado INTEGER DEFAULT 0,
        intentos INTEGER DEFAULT 0,
        ultimo_intento TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
        UNIQUE(usuario_id, ejercicio_id)
    )''')
    
    # Tabla de progreso de flashcards
    cursor.execute('''CREATE TABLE IF NOT EXISTS progreso_flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        flashcard_id INTEGER NOT NULL,
        dominado INTEGER DEFAULT 0,
        nivel_dominio INTEGER DEFAULT 1,
        ultimo_review TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
        UNIQUE(usuario_id, flashcard_id)
    )''')
    
    # Tabla de estadísticas
    cursor.execute('''CREATE TABLE IF NOT EXISTS estadisticas (
        usuario_id INTEGER PRIMARY KEY,
        puntaje_total INTEGER DEFAULT 0,
        ejercicios_completados INTEGER DEFAULT 0,
        flashcards_dominadas INTEGER DEFAULT 0,
        racha_actual INTEGER DEFAULT 0,
        mejor_racha INTEGER DEFAULT 0,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )''')
    
    # Tabla de actividades
    cursor.execute('''CREATE TABLE IF NOT EXISTS actividades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )''')
    
    # Tabla de inscripciones al taller
    cursor.execute('''CREATE TABLE IF NOT EXISTS inscripciones_taller (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        taller_nombre TEXT NOT NULL,
        fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        asistio INTEGER DEFAULT 0,
        puntaje_obtenido INTEGER DEFAULT 0,
        certificado_entregado INTEGER DEFAULT 0,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )''')
    
    conn.commit()
    
    # Verificar si existe admin
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE es_admin = 1")
    if cursor.fetchone()[0] == 0:
        admin_password = generate_password_hash('admin123')
        cursor.execute('''INSERT INTO usuarios (nombre, email, password, es_admin, biografia) 
                          VALUES (?, ?, ?, ?, ?)''',
                       ('Administrador', 'admin@claridad.com', admin_password, 1, 'Administrador del sistema'))
        conn.commit()
        print("✅ Usuario admin creado: admin@claridad.com / admin123")
    
    conn.close()

# ==================== FUNCIONES DE CARGA DE DATOS ====================

def cargar_ejercicios():
    """Cargar ejercicios desde JSON"""
    if os.path.exists(EJERCICIOS_FILE):
        with open(EJERCICIOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def cargar_flashcards():
    """Cargar flashcards desde JSON"""
    if os.path.exists(FLASHCARDS_FILE):
        with open(FLASHCARDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def cargar_config():
    """Cargar configuración desde JSON"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": "1.0",
        "modo_mantenimiento": False,
        "puntaje_ejercicio": 10,
        "puntaje_flashcard": 5
    }

# ==================== FUNCIONES DE USUARIO ====================

def registrar_actividad(usuario_id, tipo, descripcion):
    """Registrar actividad del usuario"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO actividades (usuario_id, tipo, descripcion) VALUES (?, ?, ?)",
                   (usuario_id, tipo, descripcion))
    conn.commit()
    conn.close()

def obtener_progreso(usuario_id):
    """Obtener progreso del usuario"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT ejercicio_id FROM progreso_ejercicios WHERE usuario_id=? AND completado=1", (usuario_id,))
    ejercicios_completados = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT flashcard_id FROM progreso_flashcards WHERE usuario_id=? AND dominado=1", (usuario_id,))
    flashcards_dominadas = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT puntaje_total, ejercicios_completados, flashcards_dominadas, racha_actual, mejor_racha FROM estadisticas WHERE usuario_id=?", (usuario_id,))
    stats = cursor.fetchone()
    
    conn.close()
    
    if stats:
        return {
            'ejercicios_completados': ejercicios_completados,
            'flashcards_dominadas': flashcards_dominadas,
            'puntaje_total': stats[0],
            'ejercicios_total': stats[1],
            'flashcards_total': stats[2],
            'racha_actual': stats[3],
            'mejor_racha': stats[4]
        }
    return {
        'ejercicios_completados': [],
        'flashcards_dominadas': [],
        'puntaje_total': 0,
        'ejercicios_total': 0,
        'flashcards_total': 0,
        'racha_actual': 0,
        'mejor_racha': 0
    }

def registrar_acierto(usuario_id, ejercicio_id, tipo='ejercicio'):
    """Registrar respuesta correcta"""
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now()
    
    if tipo == 'ejercicio':
        cursor.execute('''INSERT OR REPLACE INTO progreso_ejercicios 
                         (usuario_id, ejercicio_id, completado, intentos, ultimo_intento)
                         VALUES (?, ?, 1, COALESCE((SELECT intentos+1 FROM progreso_ejercicios 
                                                    WHERE usuario_id=? AND ejercicio_id=?), 1), ?)''',
                      (usuario_id, ejercicio_id, usuario_id, ejercicio_id, now))
        registrar_actividad(usuario_id, 'ejercicio', f"Completó ejercicio {ejercicio_id}")
    else:
        cursor.execute('''INSERT OR REPLACE INTO progreso_flashcards 
                         (usuario_id, flashcard_id, dominado, ultimo_review)
                         VALUES (?, ?, 1, ?)''',
                      (usuario_id, ejercicio_id, now))
        registrar_actividad(usuario_id, 'flashcard', f"Dominó flashcard {ejercicio_id}")
    
    conn.commit()
    conn.close()
    actualizar_estadisticas(usuario_id)

def actualizar_estadisticas(usuario_id):
    """Actualizar estadísticas del usuario"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM progreso_ejercicios WHERE usuario_id=? AND completado=1", (usuario_id,))
    ejercicios = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM progreso_flashcards WHERE usuario_id=? AND dominado=1", (usuario_id,))
    flashcards = cursor.fetchone()[0]
    
    puntaje = ejercicios * 10 + flashcards * 5
    
    cursor.execute('''INSERT OR REPLACE INTO estadisticas 
                     (usuario_id, puntaje_total, ejercicios_completados, flashcards_dominadas)
                     VALUES (?, ?, ?, ?)''',
                  (usuario_id, puntaje, ejercicios, flashcards))
    
    conn.commit()
    conn.close()

# ==================== DECORADORES ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor inicia sesión', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor inicia sesión', 'warning')
            return redirect(url_for('login'))
        if not session.get('es_admin'):
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== RUTAS PRINCIPALES ====================

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    usuario_id = session['usuario_id']
    progreso = obtener_progreso(usuario_id)
    ejercicios = cargar_ejercicios()
    flashcards = cargar_flashcards()
    
    return render_template('dashboard.html',
                          progreso=progreso,
                          total_ejercicios=len(ejercicios),
                          total_flashcards=len(flashcards))

@app.route('/teoria')
@login_required
def teoria():
    return render_template('teoria.html')

# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, email, password, es_admin FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario and check_password_hash(usuario['password'], password):
            session['usuario_id'] = usuario['id']
            session['usuario_nombre'] = usuario['nombre']
            session['es_admin'] = usuario['es_admin']
            registrar_actividad(usuario['id'], 'login', 'Inició sesión')
            flash(f'¡Bienvenido, {usuario["nombre"]}!', 'success')
            if usuario['es_admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmar = request.form.get('confirmar')
        
        if password != confirmar:
            flash('Las contraseñas no coinciden', 'danger')
        elif len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            conn = get_db()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)",
                              (nombre, email, hashed_password))
                conn.commit()
                flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('El email ya está registrado', 'danger')
            finally:
                conn.close()
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    if 'usuario_id' in session:
        registrar_actividad(session['usuario_id'], 'logout', 'Cerró sesión')
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))

# ==================== RUTAS DE EJERCICIOS ====================

@app.route('/ejercicios')
@login_required
def ejercicios():
    ejercicios_lista = cargar_ejercicios()
    usuario_id = session['usuario_id']
    progreso = obtener_progreso(usuario_id)
    return render_template('ejercicios.html', 
                          ejercicios=ejercicios_lista,
                          completados=progreso['ejercicios_completados'],
                          total=len(ejercicios_lista))

@app.route('/api/ejercicios')
@login_required
def api_get_ejercicios():
    ejercicios = cargar_ejercicios()
    return jsonify(ejercicios)

@app.route('/api/ejercicios_pendientes')
@login_required
def api_ejercicios_pendientes():
    usuario_id = session['usuario_id']
    progreso = obtener_progreso(usuario_id)
    completados = progreso['ejercicios_completados']
    ejercicios = cargar_ejercicios()
    pendientes = [e for e in ejercicios if e['id'] not in completados]
    return jsonify([e['id'] for e in pendientes])

@app.route('/api/ejercicio/<int:ejercicio_id>')
@login_required
def api_get_ejercicio(ejercicio_id):
    ejercicios = cargar_ejercicios()
    ejercicio = next((e for e in ejercicios if e['id'] == ejercicio_id), None)
    if ejercicio:
        return jsonify(ejercicio)
    return jsonify({'error': 'Ejercicio no encontrado'}), 404

@app.route('/api/verificar_ejercicio', methods=['POST'])
@login_required
def api_verificar_ejercicio():
    data = request.json
    ejercicio_id = data.get('ejercicio_id')
    respuesta = data.get('respuesta', '').strip().lower()
    
    ejercicios = cargar_ejercicios()
    ejercicio = next((e for e in ejercicios if e['id'] == ejercicio_id), None)
    
    if not ejercicio:
        return jsonify({'error': 'Ejercicio no encontrado'}), 404
    
    usuario_id = session['usuario_id']
    
    if ejercicio['tipo'] == 'correccion':
        correcto = respuesta == ejercicio['correcto'].lower()
    else:
        correcto = respuesta == ejercicio['respuesta'].lower()
    
    if correcto:
        registrar_acierto(usuario_id, ejercicio_id, 'ejercicio')
        mensaje = "¡Correcto! +10 puntos"
    else:
        mensaje = f"Incorrecto. Respuesta correcta: {ejercicio.get('correcto', ejercicio.get('respuesta', ''))}"
    
    progreso = obtener_progreso(usuario_id)
    
    return jsonify({
        'correcto': correcto,
        'mensaje': mensaje,
        'puntaje': progreso['puntaje_total'],
        'completados': len(progreso['ejercicios_completados'])
    })

# ==================== RUTAS DE FLASHCARDS ====================

@app.route('/flashcards')
@login_required
def flashcards():
    flashcards_lista = cargar_flashcards()
    usuario_id = session['usuario_id']
    progreso = obtener_progreso(usuario_id)
    return render_template('flashcards.html', 
                          flashcards=flashcards_lista,
                          dominadas=progreso['flashcards_dominadas'])

@app.route('/api/flashcards')
@login_required
def api_get_flashcards():
    flashcards = cargar_flashcards()
    return jsonify(flashcards)

@app.route('/api/flashcards_pendientes')
@login_required
def api_flashcards_pendientes():
    usuario_id = session['usuario_id']
    progreso = obtener_progreso(usuario_id)
    dominadas = progreso['flashcards_dominadas']
    flashcards = cargar_flashcards()
    pendientes = [f for f in flashcards if f['id'] not in dominadas]
    return jsonify([f['id'] for f in pendientes])

@app.route('/api/flashcard/<int:flashcard_id>')
@login_required
def api_get_flashcard(flashcard_id):
    flashcards = cargar_flashcards()
    flashcard = next((f for f in flashcards if f['id'] == flashcard_id), None)
    if flashcard:
        return jsonify(flashcard)
    return jsonify({'error': 'Flashcard no encontrado'}), 404

@app.route('/api/marcar_flashcard', methods=['POST'])
@login_required
def api_marcar_flashcard():
    data = request.json
    flashcard_id = data.get('flashcard_id')
    dominado = data.get('dominado', False)
    
    usuario_id = session['usuario_id']
    
    if dominado:
        registrar_acierto(usuario_id, flashcard_id, 'flashcard')
    
    progreso = obtener_progreso(usuario_id)
    
    return jsonify({
        'success': True,
        'puntaje': progreso['puntaje_total'],
        'dominadas': len(progreso['flashcards_dominadas'])
    })

# ==================== RUTAS DE PROGRESO ====================

@app.route('/progreso')
@login_required
def progreso():
    usuario_id = session['usuario_id']
    progreso = obtener_progreso(usuario_id)
    ejercicios = cargar_ejercicios()
    flashcards = cargar_flashcards()
    
    return render_template('progreso.html',
                          progreso=progreso,
                          total_ejercicios=len(ejercicios),
                          total_flashcards=len(flashcards))

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    usuario_id = session['usuario_id']
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        biografia = request.form.get('biografia')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET nombre = ?, biografia = ? WHERE id = ?", (nombre, biografia, usuario_id))
        conn.commit()
        conn.close()
        
        session['usuario_nombre'] = nombre
        registrar_actividad(usuario_id, 'perfil', 'Actualizó su perfil')
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('perfil'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email, fecha_registro, biografia FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()
    conn.close()
    
    return render_template('perfil.html', usuario=usuario)

# ==================== RUTAS DE ADMINISTRACIÓN ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE es_admin = 0")
    total_usuarios = cursor.fetchone()[0]
    conn.close()
    
    ejercicios = cargar_ejercicios()
    flashcards = cargar_flashcards()
    
    return render_template('admin/dashboard.html',
                          total_usuarios=total_usuarios,
                          total_ejercicios=len(ejercicios),
                          total_flashcards=len(flashcards))

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email, fecha_registro, es_admin FROM usuarios ORDER BY id")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/eliminar/<int:usuario_id>', methods=['POST'])
@admin_required
def admin_eliminar_usuario(usuario_id):
    if usuario_id == session['usuario_id']:
        flash('No puedes eliminarte a ti mismo', 'danger')
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ? AND es_admin = 0", (usuario_id,))
        conn.commit()
        conn.close()
        flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('admin_usuarios'))

# ==================== INICIALIZACIÓN ====================

if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("🎯 CLARIDAD TÉCNICA - Aplicación educativa")
    print("📍 Accede en: http://localhost:5000")
    print("📧 Admin: admin@claridad.com")
    print("🔑 Contraseña: admin123")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
