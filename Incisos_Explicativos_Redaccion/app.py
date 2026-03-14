from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
import os
from datetime import datetime
import random
from functools import wraps
from config import config
from models import Usuario, SistemaMedallas

app = Flask(__name__)
app.config.from_object(config['development'])

# Inicializar sistema de medallas
sistema_medallas = SistemaMedallas(app.config)

# Asegurar que los directorios existen
os.makedirs('data', exist_ok=True)

# Funciones de utilidad
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def cargar_usuarios():
    try:
        with open(app.config['USUARIOS_FILE'], 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Usuario.from_dict(u) for u in data]
    except FileNotFoundError:
        return []

def guardar_usuarios(usuarios):
    with open(app.config['USUARIOS_FILE'], 'w', encoding='utf-8') as f:
        json.dump([u.to_dict() for u in usuarios], f, ensure_ascii=False, indent=2)

def cargar_ejemplos():
    try:
        with open(app.config['DATA_FILE'], 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_ejemplos(ejemplos):
    with open(app.config['DATA_FILE'], 'w', encoding='utf-8') as f:
        json.dump(ejemplos, f, ensure_ascii=False, indent=2)

def cargar_ejercicios_completos():
    try:
        with open(app.config['EJERCICIOS_FILE'], 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return generar_100_ejercicios()

def generar_100_ejercicios():
    """Genera 100 ejercicios por categorías"""
    categorias = ['Comas', 'Paréntesis', 'Rayas', 'Geográficos', 'Siglas']
    ejercicios = []
    
    bases = {
        'Comas': [
            "El presidente {} anunció nuevas medidas",
            "La ciudad {} es famosa por su arquitectura",
            "El profesor {} explicó la lección",
            "El libro {} fue un bestseller",
            "La película {} ganó varios premios"
        ],
        'Paréntesis': [
            "El COVID-19 {} cambió el mundo",
            "La ONU {} fue fundada en 1945",
            "El telescopio Hubble {} revolucionó la astronomía",
            "La empresa {} desarrolló nueva tecnología",
            "El tratado {} puso fin a la guerra"
        ],
        'Rayas': [
            "El resultado {} sorprendió a todos",
            "La decisión {} fue controversial",
            "El discurso {} conmovió a la audiencia",
            "El descubrimiento {} cambió la ciencia",
            "La noticia {} impactó al mundo"
        ],
        'Geográficos': [
            "París {} es conocida como la Ciudad Luz",
            "El Amazonas {} es el río más caudaloso",
            "Los Andes {} atraviesan Sudamérica",
            "El Sahara {} es el desierto más grande",
            "Australia {} es un país continente"
        ],
        'Siglas': [
            "La NASA {} lanzó una nueva misión",
            "La FIFA {} organiza el mundial",
            "La OMS {} declaró la emergencia",
            "La UNESCO {} protege el patrimonio",
            "La OTAN {} celebró una cumbre"
        ]
    }
    
    incisos = {
        'Comas': [
            "líder del proyecto", "capital de Francia", "experto en la materia",
            "publicado en 2020", "dirigida por un famoso director"
        ],
        'Paréntesis': [
            "descubierto en 2019", "Organización de las Naciones Unidas",
            "lanzado en 1990", "fundada en 2010", "firmado en 1945"
        ],
        'Rayas': [
            "inesperado por todos", "tomada tras largas deliberaciones",
            "pronunciado con pasión", "realizado por accidente",
            "difundida globalmente"
        ],
        'Geográficos': [
            "capital de Francia", "el más caudaloso del mundo",
            "la cordillera más larga", "el desierto más extenso",
            "el país más pequeño"
        ],
        'Siglas': [
            "National Aeronautics and Space Administration",
            "Fédération Internationale de Football Association",
            "Organización Mundial de la Salud",
            "Organización de las Naciones Unidas para la Educación",
            "Organización del Tratado del Atlántico Norte"
        ]
    }
    
    for i in range(100):
        categoria = random.choice(categorias)
        ejercicio = {
            'id': i + 1,
            'base': random.choice(bases[categoria]),
            'inciso': random.choice(incisos[categoria]),
            'categoria': categoria,
            'puntuacion': categoria.lower() if categoria in ['Comas', 'Paréntesis', 'Rayas'] else 
                         random.choice(['comas', 'paréntesis', 'rayas']),
            'dificultad': random.choice(['fácil', 'media', 'difícil']),
            'pistas': [
                f"Usa {categoria.lower() if categoria in ['Comas', 'Paréntesis', 'Rayas'] else 'puntuación adecuada'}",
                f"El inciso es: '{incisos[categoria][i % 5]}'"
            ]
        }
        ejercicios.append(ejercicio)
    
    # Guardar ejercicios
    with open(app.config['EJERCICIOS_FILE'], 'w', encoding='utf-8') as f:
        json.dump(ejercicios, f, ensure_ascii=False, indent=2)
    
    return ejercicios

def cargar_flashcards():
    try:
        with open(app.config['FLASHCARDS_FILE'], 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return generar_50_flashcards()

def generar_50_flashcards():
    """Genera 50 flashcards explicativas"""
    flashcards = []
    
    conceptos = [
        {
            'titulo': 'Inciso Explicativo',
            'definicion': 'Elemento sintáctico que añade información adicional entre comas, paréntesis o rayas',
            'ejemplo': 'Londres, capital del Reino Unido, tiene 9 millones de habitantes',
            'categoria': 'Conceptos básicos'
        },
        {
            'titulo': 'Comas Explicativas',
            'definicion': 'Se usan para introducir información relacionada o aclaratoria',
            'ejemplo': 'El director, Sr. Rodríguez, anunció cambios importantes',
            'categoria': 'Comas'
        },
        {
            'titulo': 'Paréntesis',
            'definicion': 'Se utilizan para datos técnicos o información secundaria',
            'ejemplo': 'El COVID-19 (descubierto en 2019) cambió el mundo',
            'categoria': 'Paréntesis'
        },
        {
            'titulo': 'Rayas',
            'definicion': 'Se emplean para dar énfasis o introducir interrupciones',
            'ejemplo': 'El resultado —inesperado por todos— sorprendió a los expertos',
            'categoria': 'Rayas'
        },
        {
            'titulo': 'Contexto Geográfico',
            'definicion': 'Incisos que proporcionan información sobre ubicaciones',
            'ejemplo': 'París, capital de Francia, es conocida como la Ciudad Luz',
            'categoria': 'Geográficos'
        },
        {
            'titulo': 'Siglas',
            'definicion': 'Abreviaturas que se explican con paréntesis',
            'ejemplo': 'La NASA (National Aeronautics and Space Administration) lanzó una misión',
            'categoria': 'Siglas'
        }
    ]
    
    # Generar 50 flashcards variando los ejemplos
    for i in range(50):
        concepto = random.choice(conceptos)
        flashcard = concepto.copy()
        flashcard['id'] = i + 1
        
        # Variar ejemplos según categoría
        if flashcard['categoria'] == 'Comas':
            ejemplos = [
                f"El presidente, {random.choice(['electo', 'saliente', 'actual'])}, hablará mañana",
                f"La ciudad, {random.choice(['fundada en 1500', 'capital regional', 'turística'])}, crece rápidamente"
            ]
            flashcard['ejemplo'] = random.choice(ejemplos)
        
        flashcards.append(flashcard)
    
    # Guardar flashcards
    with open(app.config['FLASHCARDS_FILE'], 'w', encoding='utf-8') as f:
        json.dump(flashcards, f, ensure_ascii=False, indent=2)
    
    return flashcards

# Rutas de autenticación
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        
        usuarios = cargar_usuarios()
        
        # Verificar si el email ya existe
        if any(u.email == email for u in usuarios):
            flash('El email ya está registrado', 'danger')
            return redirect(url_for('registro'))
        
        # Crear nuevo usuario
        nuevo_id = len(usuarios) + 1
        usuario = Usuario(id=nuevo_id, nombre=nombre, email=email)
        usuario.set_password(password)
        
        usuarios.append(usuario)
        guardar_usuarios(usuarios)
        
        session['usuario_id'] = usuario.id
        session['usuario_nombre'] = usuario.nombre
        
        flash('Registro exitoso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        usuarios = cargar_usuarios()
        usuario = next((u for u in usuarios if u.email == email), None)
        
        if usuario and usuario.check_password(password):
            session['usuario_id'] = usuario.id
            session['usuario_nombre'] = usuario.nombre
            flash(f'Bienvenido, {usuario.nombre}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('index'))

# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    usuarios = cargar_usuarios()
    usuario = next((u for u in usuarios if u.id == session['usuario_id']), None)
    return render_template('dashboard.html', usuario=usuario)

@app.route('/teoria')
def teoria():
    return render_template('teoria.html')

@app.route('/practica')
@login_required
def practica():
    ejercicios = cargar_ejercicios_completos()
    return render_template('practica.html', ejercicios=ejercicios)

@app.route('/flashcards')
@login_required
def flashcards():
    flashcards_list = cargar_flashcards()
    return render_template('flashcards.html', flashcards=flashcards_list)

@app.route('/crear')
@login_required
def crear():
    ejemplos = cargar_ejemplos()
    return render_template('crear.html', ejemplos=ejemplos, max_ejemplos=app.config['MAX_EJEMPLOS'])

@app.route('/estadisticas')
@login_required
def estadisticas():
    usuarios = cargar_usuarios()
    usuario = next((u for u in usuarios if u.id == session['usuario_id']), None)
    return render_template('estadisticas.html', usuario=usuario, medallas_config=app.config['MEDALLAS'])

# API endpoints
@app.route('/api/ejercicio/aleatorio', methods=['GET'])
@login_required
def api_ejercicio_aleatorio():
    ejercicios = cargar_ejercicios_completos()
    categoria = request.args.get('categoria')
    dificultad = request.args.get('dificultad')
    
    ejercicios_filtrados = ejercicios
    if categoria:
        ejercicios_filtrados = [e for e in ejercicios_filtrados if e['categoria'] == categoria]
    if dificultad:
        ejercicios_filtrados = [e for e in ejercicios_filtrados if e['dificultad'] == dificultad]
    
    if not ejercicios_filtrados:
        return jsonify({'error': 'No hay ejercicios disponibles'}), 404
    
    ejercicio = random.choice(ejercicios_filtrados)
    return jsonify(ejercicio)

@app.route('/api/verificar', methods=['POST'])
@login_required
def api_verificar():
    data = request.json
    respuesta = data['respuesta']
    ejercicio = data['ejercicio']
    
    # Verificar según el tipo de puntuación
    es_correcto = False
    import re
    
    if ejercicio['puntuacion'] == 'comas':
        patron = f",\\s*{re.escape(ejercicio['inciso'])}\\s*,"
        es_correcto = bool(re.search(patron, respuesta))
    elif ejercicio['puntuacion'] == 'paréntesis':
        patron = f"\\(\\s*{re.escape(ejercicio['inciso'])}\\s*\\)"
        es_correcto = bool(re.search(patron, respuesta))
    elif ejercicio['puntuacion'] == 'rayas':
        patron = f"—\\s*{re.escape(ejercicio['inciso'])}\\s*—"
        es_correcto = bool(re.search(patron, respuesta))
    
    # Actualizar estadísticas del usuario
    usuarios = cargar_usuarios()
    usuario = next((u for u in usuarios if u.id == session['usuario_id']), None)
    
    if usuario:
        nuevos_logros = sistema_medallas.registrar_ejercicio(
            usuario, es_correcto, ejercicio['categoria']
        )
        guardar_usuarios(usuarios)
    
    return jsonify({
        'correcto': es_correcto,
        'mensaje': '¡Correcto!' if es_correcto else 'Incorrecto. Revisa los signos de puntuación.',
        'puntos_ganados': app.config['PUNTOS']['ejercicio_completado'] + 
                         (app.config['PUNTOS']['respuesta_correcta'] if es_correcto else 0),
        'rachas': usuario.estadisticas['rachas'] if usuario else None,
        'nuevos_logros': nuevos_logros if usuario else []
    })

@app.route('/api/flashcard/completada', methods=['POST'])
@login_required
def api_flashcard_completada():
    usuarios = cargar_usuarios()
    usuario = next((u for u in usuarios if u.id == session['usuario_id']), None)
    
    if usuario:
        sistema_medallas.registrar_flashcard(usuario)
        guardar_usuarios(usuarios)
        
        return jsonify({
            'mensaje': 'Flashcard completada',
            'puntos': usuario.estadisticas['puntos'],
            'estrellas': usuario.estadisticas['estrellas']
        })
    
    return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/api/estadisticas', methods=['GET'])
@login_required
def api_get_estadisticas():
    usuarios = cargar_usuarios()
    usuario = next((u for u in usuarios if u.id == session['usuario_id']), None)
    
    if usuario:
        return jsonify(usuario.estadisticas)
    
    return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/api/ranking', methods=['GET'])
@login_required
def api_ranking():
    usuarios = cargar_usuarios()
    
    # Ordenar por puntos
    ranking = sorted(usuarios, key=lambda u: u.estadisticas['puntos'], reverse=True)
    
    ranking_data = []
    for i, usuario in enumerate(ranking[:10], 1):
        ranking_data.append({
            'posicion': i,
            'nombre': usuario.nombre,
            'puntos': usuario.estadisticas['puntos'],
            'medallas': len(usuario.estadisticas['medallas']),
            'estrellas': usuario.estadisticas['estrellas']
        })
    
    return jsonify(ranking_data)

if __name__ == '__main__':
    app.run(debug=True)
