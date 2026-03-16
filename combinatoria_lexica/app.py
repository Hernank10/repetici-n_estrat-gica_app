from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap5
from datetime import datetime, timedelta
import json
import os
import random
from config import Config
from models import db, User, Achievement, UserAchievement, UserSentence, UserExercise, UserFlashCard, DailyStat
from forms import (LoginForm, RegisterForm, ProfileForm, SentenceForm, 
                  ExerciseFilterForm, FlashcardReviewForm, ContactForm, 
                  AvatarUploadForm, GoalForm)
from utils import (calcular_nivel, calcular_xp, verificar_logros, 
                  generar_recomendaciones, formatear_tiempo, 
                  obtener_color_por_nivel, obtener_icono_por_categoria,
                  validar_oracion, calcular_tendencia, obtener_mensaje_motivacional)
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
csrf = CSRFProtect(app)
bootstrap = Bootstrap5(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Cargar datos JSON
with open('data/ejercicios.json', 'r', encoding='utf-8') as f:
    EJERCICIOS_DATA = json.load(f)

with open('data/flashcards.json', 'r', encoding='utf-8') as f:
    FLASHCARDS_DATA = json.load(f)

with open('data/niveles.json', 'r', encoding='utf-8') as f:
    NIVELES_DATA = json.load(f)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor para variables globales en templates
@app.context_processor
def utility_processor():
    return {
        'now': datetime.utcnow(),
        'formatear_tiempo': formatear_tiempo,
        'obtener_color_nivel': obtener_color_por_nivel,
        'obtener_icono_categoria': obtener_icono_por_categoria
    }

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            user = User.query.filter_by(email=form.username.data).first()
        
        # Nota: En producción deberías usar hash de contraseñas
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember.data)
            user.last_active = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            flash(f'¡Bienvenido de nuevo, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('El nombre de usuario ya existe', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('El email ya está registrado', 'danger')
            return render_template('register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data  # Nota: En producción usar hash
        )
        db.session.add(user)
        db.session.commit()
        
        flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))

# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Actualizar último acceso
    current_user.last_active = datetime.utcnow()
    db.session.commit()
    
    recomendaciones = generar_recomendaciones(current_user)
    mensaje_motivacional = obtener_mensaje_motivacional(
        current_user.racha_actual, 
        current_user.nivel_actual
    )
    
    return render_template('dashboard.html', 
                         recomendaciones=recomendaciones,
                         mensaje_motivacional=mensaje_motivacional)

@app.route('/flashcards')
@login_required
def flashcards():
    return render_template('flashcards.html')

@app.route('/ejercicios')
@login_required
def ejercicios():
    form = ExerciseFilterForm()
    return render_template('ejercicios.html', form=form)

@app.route('/niveles')
@login_required
def niveles():
    return render_template('niveles.html')

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    form = ProfileForm(obj=current_user)
    avatar_form = AvatarUploadForm()
    
    if form.validate_on_submit():
        if form.username.data and form.username.data != current_user.username:
            if User.query.filter_by(username=form.username.data).first():
                flash('El nombre de usuario ya está en uso', 'danger')
            else:
                current_user.username = form.username.data
        
        if form.email.data and form.email.data != current_user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash('El email ya está registrado', 'danger')
            else:
                current_user.email = form.email.data
        
        if form.new_password.data:
            if form.current_password.data == current_user.password:
                current_user.password = form.new_password.data
                flash('Contraseña actualizada correctamente', 'success')
            else:
                flash('La contraseña actual es incorrecta', 'danger')
        
        current_user.theme_preference = form.theme_preference.data
        current_user.font_size = form.font_size.data
        current_user.notifications_enabled = form.notifications_enabled.data
        current_user.sound_enabled = form.sound_enabled.data
        
        db.session.commit()
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('perfil'))
    
    return render_template('perfil.html', form=form, avatar_form=avatar_form)

@app.route('/practica', methods=['GET', 'POST'])
@login_required
def practica():
    form = SentenceForm()
    
    if form.validate_on_submit():
        valida, mensaje = validar_oracion(form.sentence.data)
        if valida:
            sentence = UserSentence(
                user_id=current_user.id,
                sentence=form.sentence.data,
                verb='otro',  # Se detectará automáticamente
                category=form.category.data,
                is_public=form.is_public.data
            )
            
            # Detectar verbo principal
            verbs = ['subir', 'bajar', 'caer', 'izar', 'arriar', 'levantar', 
                    'alzar', 'descender', 'ascender', 'elevar']
            for verb in verbs:
                if verb in form.sentence.data.lower():
                    sentence.verb = verb
                    break
            
            db.session.add(sentence)
            current_user.oraciones_guardadas += 1
            current_user.xp += Config.XP_CONFIG['oracion_guardada']
            db.session.commit()
            
            # Verificar logros
            verificar_logros(current_user)
            
            flash('¡Oración guardada correctamente!', 'success')
            return redirect(url_for('practica'))
        else:
            flash(mensaje, 'warning')
    
    # Obtener oraciones del usuario
    sentences = UserSentence.query.filter_by(user_id=current_user.id)\
        .order_by(UserSentence.created_at.desc()).limit(10).all()
    
    return render_template('practica.html', form=form, sentences=sentences)

# API Endpoints para ejercicios
@app.route('/api/ejercicios/random', methods=['GET'])
@login_required
def get_random_ejercicio():
    nivel = request.args.get('nivel', 'todos')
    categoria = request.args.get('categoria', 'todas')
    
    ejercicios = EJERCICIOS_DATA['ejercicios']
    
    if nivel != 'todos':
        ejercicios = [e for e in ejercicios if e['dificultad'] == nivel]
    
    if categoria != 'todas':
        ejercicios = [e for e in ejercicios if e.get('categoria') == categoria]
    
    if ejercicios:
        ejercicio = random.choice(ejercicios)
        return jsonify(ejercicio)
    
    return jsonify({'error': 'No hay ejercicios disponibles'}), 404

@app.route('/api/ejercicios/check', methods=['POST'])
@login_required
def check_ejercicio():
    data = request.get_json()
    ejercicio_id = data.get('ejercicio_id')
    respuesta = data.get('respuesta')
    tiempo = data.get('tiempo', 0)
    
    ejercicio = next((e for e in EJERCICIOS_DATA['ejercicios'] if e['id'] == ejercicio_id), None)
    
    if not ejercicio:
        return jsonify({'error': 'Ejercicio no encontrado'}), 404
    
    es_correcto = (respuesta == ejercicio['correcta'])
    
    # Calcular XP basado en dificultad y tiempo
    xp_ganado = calcular_xp(ejercicio['dificultad'], tiempo, es_correcto)
    
    # Registrar el intento
    record = UserExercise(
        user_id=current_user.id,
        exercise_id=ejercicio_id,
        was_correct=es_correcto,
        tiempo=tiempo,
        xp_ganado=xp_ganado if es_correcto else 0,
        dificultad=ejercicio['dificultad']
    )
    db.session.add(record)
    
    # Actualizar estadísticas del usuario
    if es_correcto:
        current_user.xp += xp_ganado
        current_user.ejercicios_completados += 1
        current_user.ejercicios_correctos += 1
        current_user.racha_actual += 1
        
        if current_user.racha_actual > current_user.racha_maxima:
            current_user.racha_maxima = current_user.racha_actual
        
        # Actualizar nivel si corresponde
        nivel_info = calcular_nivel(current_user.xp)
        current_user.nivel_actual = nivel_info['nombre']
    else:
        current_user.racha_actual = 0
    
    current_user.tiempo_total += tiempo
    db.session.commit()
    
    # Actualizar estadísticas diarias
    current_user.update_daily_stat(ejercicios=1, xp=xp_ganado if es_correcto else 0)
    
    # Verificar nuevos logros
    nuevos_logros = verificar_logros(current_user)
    
    return jsonify({
        'correcto': es_correcto,
        'xp_ganado': xp_ganado if es_correcto else 0,
        'explicacion': ejercicio['explicacion'],
        'nuevos_logros': nuevos_logros,
        'racha': current_user.racha_actual
    })

# API Endpoints para flashcards
@app.route('/api/flashcards/random', methods=['GET'])
@login_required
def get_random_flashcard():
    categoria = request.args.get('categoria', 'todas')
    
    flashcards = FLASHCARDS_DATA['flashcards']
    
    if categoria != 'todas':
        flashcards = [f for f in flashcards if f['categoria'] == categoria]
    
    # Priorizar flashcards no estudiadas o menos estudiadas
    if flashcards:
        flashcard = random.choice(flashcards)
        
        # Registrar estudio
        existing = UserFlashCard.query.filter_by(
            user_id=current_user.id,
            flashcard_id=flashcard['id']
        ).first()
        
        if existing:
            existing.veces_estudiado += 1
            existing.fecha_estudio = datetime.utcnow()
        else:
            user_flashcard = UserFlashCard(
                user_id=current_user.id,
                flashcard_id=flashcard['id'],
                veces_estudiado=1
            )
            db.session.add(user_flashcard)
            current_user.flashcards_estudiadas += 1
        
        db.session.commit()
        
        return jsonify(flashcard)
    
    return jsonify({'mensaje': 'No hay flashcards disponibles'}), 404

@app.route('/api/flashcards/review', methods=['POST'])
@login_required
def review_flashcard():
    form = FlashcardReviewForm()
    
    if form.validate_on_submit():
        user_flashcard = UserFlashCard.query.filter_by(
            user_id=current_user.id,
            flashcard_id=form.flashcard_id.data
        ).first()
        
        if user_flashcard:
            user_flashcard.dificultad = form.dificultad.data
            user_flashcard.dominado = form.dominado.data
            
            if form.dominado.data:
                current_user.flashcards_dominadas += 1
                current_user.xp += Config.XP_CONFIG['flashcard_estudiada']
            
            db.session.commit()
            
            return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid data'}), 400

@app.route('/api/flashcards/estadisticas', methods=['GET'])
@login_required
def get_flashcard_stats():
    total = len(FLASHCARDS_DATA['flashcards'])
    estudiadas = current_user.flashcards_estudiadas
    dominadas = current_user.flashcards_dominadas
    
    # Estadísticas por categoría
    categorias = {}
    for flashcard in FLASHCARDS_DATA['flashcards']:
        cat = flashcard['categoria']
        if cat not in categorias:
            categorias[cat] = {'total': 0, 'estudiadas': 0}
        categorias[cat]['total'] += 1
    
    estudiadas_por_cat = db.session.query(
        UserFlashCard.flashcard_id,
        db.func.count(UserFlashCard.id)
    ).filter_by(user_id=current_user.id).group_by(UserFlashCard.flashcard_id).all()
    
    for flashcard_id, count in estudiadas_por_cat:
        flashcard = next((f for f in FLASHCARDS_DATA['flashcards'] if f['id'] == flashcard_id), None)
        if flashcard:
            categorias[flashcard['categoria']]['estudiadas'] += 1
    
    return jsonify({
        'total': total,
        'estudiadas': estudiadas,
        'dominadas': dominadas,
        'porcentaje': int((estudiadas / total) * 100) if total > 0 else 0,
        'categorias': categorias
    })

# API Endpoints para usuario
@app.route('/api/user/stats', methods=['GET'])
@login_required
def get_user_stats():
    nivel_info = current_user.get_nivel_info()
    stats = current_user.get_stats()
    progreso_diario = current_user.get_daily_progress(7)
    tendencia = calcular_tendencia(progreso_diario)
    
    # Obtener medallas
    achievements = Achievement.query.all()
    user_achievements = current_user.get_achievements_ids()
    
    return jsonify({
        'username': current_user.username,
        'xp': current_user.xp,
        'nivel': nivel_info,
        'progreso_nivel': nivel_info['progreso'],
        'ejercicios_completados': current_user.ejercicios_completados,
        'ejercicios_correctos': current_user.ejercicios_correctos,
        'accuracy': stats['accuracy'],
        'racha_actual': current_user.racha_actual,
        'racha_maxima': current_user.racha_maxima,
        'tiempo_total': current_user.tiempo_total,
        'flashcards_estudiadas': current_user.flashcards_estudiadas,
        'flashcards_dominadas': current_user.flashcards_dominadas,
        'oraciones_guardadas': current_user.oraciones_guardadas,
        'logros_totales': current_user.logros_totales,
        'tendencia': tendencia,
        'progreso_diario': progreso_diario,
        'medallas': [{
            'id': a.id,
            'nombre': a.nombre,
            'icono': a.icono,
            'color': a.color_bootstrap,
            'descripcion': a.descripcion,
            'desbloqueada': a.id in user_achievements,
            'xp_recompensa': a.xp_recompensa
        } for a in achievements]
    })

@app.route('/api/user/theme', methods=['POST'])
@login_required
def update_theme():
    data = request.get_json()
    theme = data.get('theme')
    if theme in ['light', 'dark', 'auto']:
        current_user.theme_preference = theme
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid theme'}), 400

@app.route('/api/sentences/list', methods=['GET'])
@login_required
def get_sentences():
    sentences = UserSentence.query.filter_by(user_id=current_user.id)\
        .order_by(UserSentence.created_at.desc()).limit(50).all()
    
    return jsonify([s.to_dict() for s in sentences])

@app.route('/api/sentences/delete/<int:sentence_id>', methods=['DELETE'])
@login_required
def delete_sentence(sentence_id):
    sentence = UserSentence.query.filter_by(
        id=sentence_id,
        user_id=current_user.id
    ).first()
    
    if sentence:
        db.session.delete(sentence)
        current_user.oraciones_guardadas -= 1
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Sentence not found'}), 404

# Exportar reporte PDF
@app.route('/export/pdf', methods=['GET'])
@login_required
def export_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#3498db')
    )
    story.append(Paragraph('Reporte de Progreso - Combinatoria Léxica', title_style))
    story.append(Spacer(1, 20))
    
    # Información del usuario
    story.append(Paragraph(f'Usuario: {current_user.username}', styles['Heading2']))
    story.append(Paragraph(f'Fecha: {datetime.now().strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Estadísticas
    nivel_info = current_user.get_nivel_info()
    stats = current_user.get_stats()
    
    data = [
        ['Métrica', 'Valor'],
        ['Nivel Actual', nivel_info['titulo']],
        ['XP Total', str(current_user.xp)],
        ['Progreso Nivel', f"{nivel_info['progreso']}%"],
        ['Ejercicios Completados', str(current_user.ejercicios_completados)],
        ['Precisión', f"{stats['accuracy']}%"],
        ['Racha Máxima', str(current_user.racha_maxima)],
        ['Flashcards Estudiadas', str(current_user.flashcards_estudiadas)],
        ['Oraciones Guardadas', str(current_user.oraciones_guardadas)],
        ['Logros Desbloqueados', str(current_user.logros_totales)],
        ['Tiempo Total', formatear_tiempo(current_user.tiempo_total)]
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Logros
    story.append(Paragraph('Logros Desbloqueados:', styles['Heading2']))
    user_achievements = current_user.get_achievements_ids()
    achievements = Achievement.query.all()
    
    if user_achievements:
        for achievement in achievements:
            if achievement.id in user_achievements:
                story.append(Paragraph(f'✓ {achievement.icono} {achievement.nombre}: {achievement.descripcion}', styles['Normal']))
    else:
        story.append(Paragraph('Aún no has desbloqueado logros.', styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Últimas oraciones
    story.append(Paragraph('Últimas Oraciones Guardadas:', styles['Heading2']))
    sentences = UserSentence.query.filter_by(user_id=current_user.id)\
        .order_by(UserSentence.created_at.desc()).limit(10).all()
    
    if sentences:
        for sentence in sentences:
            story.append(Paragraph(f'• {sentence.sentence}', styles['Normal']))
    else:
        story.append(Paragraph('No has guardado oraciones aún.', styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'reporte_{current_user.username}_{datetime.now().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

# Manejo de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Inicializar base de datos
def init_db():
    with app.app_context():
        db.create_all()
        
        # Crear logros si no existen
        logros = [
            Achievement(id='novato', nombre='Novato', icono='🌱', 
                       color_bootstrap='success', descripcion='Completa 5 ejercicios', xp_recompensa=50),
            Achievement(id='aprendiz', nombre='Aprendiz', icono='🌿', 
                       color_bootstrap='info', descripcion='Completa 20 ejercicios', xp_recompensa=100),
            Achievement(id='experto', nombre='Experto', icono='🏆', 
                       color_bootstrap='warning', descripcion='Completa 50 ejercicios', xp_recompensa=200),
            Achievement(id='racha5', nombre='Racha de 5', icono='🔥', 
                       color_bootstrap='danger', descripcion='5 respuestas correctas consecutivas', xp_recompensa=75),
            Achievement(id='racha10', nombre='Racha de 10', icono='⚡', 
                       color_bootstrap='danger', descripcion='10 respuestas correctas consecutivas', xp_recompensa=150),
            Achievement(id='precision', nombre='Preciso', icono='🎯', 
                       color_bootstrap='primary', descripcion='100% de aciertos en 10 ejercicios', xp_recompensa=100),
            Achievement(id='escritor', nombre='Escritor', icono='✍️', 
                       color_bootstrap='secondary', descripcion='Guarda 10 oraciones', xp_recompensa=75),
            Achievement(id='rapidez', nombre='Velocista', icono='⚡', 
                       color_bootstrap='warning', descripcion='Responde 10 ejercicios en menos de 30 segundos', xp_recompensa=100),
            Achievement(id='dedicacion', nombre='Dedicado', icono='📚', 
                       color_bootstrap='primary', descripcion='Completa 100 ejercicios', xp_recompensa=300),
            Achievement(id='creatividad', nombre='Creativo', icono='🎨', 
                       color_bootstrap='info', descripcion='Guarda 20 oraciones originales', xp_recompensa=150),
            Achievement(id='estudioso', nombre='Estudioso', icono='📇', 
                       color_bootstrap='success', descripcion='Estudia 50 flashcards', xp_recompensa=100)
        ]
        
        for logro in logros:
            if not Achievement.query.get(logro.id):
                db.session.add(logro)
        
        db.session.commit()
        print("Base de datos inicializada correctamente")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
