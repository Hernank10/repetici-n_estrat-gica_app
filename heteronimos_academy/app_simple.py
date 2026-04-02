from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
import random

app = Flask(__name__)
app.secret_key = 'heteronimos_key'

# Cargar datos JSON
def cargar_json(archivo):
    with open(f'data/{archivo}', 'r', encoding='utf-8') as f:
        return json.load(f)

HETERONIMOS = cargar_json('heteronimos.json')['heteronimos']
EJERCICIOS_COMPLETACION = cargar_json('ejercicios_completacion.json')['ejercicios']
EJERCICIOS_QUIZ = cargar_json('ejercicios_quiz.json')['quiz']
FLASHCARDS = cargar_json('flashcards.json')['flashcards']

# Almacenamiento en memoria (sin base de datos)
usuarios = {}
progreso_usuarios = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teoria')
def teoria():
    return render_template('teoria.html', heteronimos=HETERONIMOS)

@app.route('/teoria/semantica')
def teoria_semantica():
    teoria_data = cargar_json('teoria_semantica.json')
    return render_template('teoria_semantica.html', teoria=teoria_data['teoria'])

@app.route('/flashcards')
def flashcards():
    return render_template('flashcards.html', flashcards=FLASHCARDS)

@app.route('/practica')
def practica():
    return render_template('practica.html')

@app.route('/ejercicios')
def ejercicios():
    return render_template('ejercicios.html')

@app.route('/progreso')
def progreso():
    return render_template('progreso.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    user_id = len(usuarios) + 1
    usuarios[user_id] = {
        'nombre': data['nombre'],
        'email': data['email'],
        'puntos': 0,
        'nivel': 1
    }
    session['usuario_id'] = user_id
    return jsonify({"success": True})

@app.route('/api/heteronimos/random', methods=['GET'])
def heteronimo_random():
    return jsonify(random.choice(HETERONIMOS))

@app.route('/api/ejercicio/completacion/random', methods=['GET'])
def ejercicio_random():
    ejercicio = random.choice(EJERCICIOS_COMPLETACION)
    return jsonify({
        "id": ejercicio['id'],
        "texto": ejercicio['texto'],
        "categoria": ejercicio['categoria'],
        "dificultad": ejercicio['dificultad']
    })

@app.route('/api/ejercicio/completacion/verificar', methods=['POST'])
def verificar_completacion():
    data = request.json
    ejercicio = next((e for e in EJERCICIOS_COMPLETACION if e['id'] == data['ejercicio_id']), None)
    
    if not ejercicio:
        return jsonify({"correcto": False})
    
    correcto = (data['masculino'].lower() == ejercicio['respuesta_m'] and 
                data['femenino'].lower() == ejercicio['respuesta_f'])
    
    puntos = 10 if correcto else 0
    
    return jsonify({
        "correcto": correcto,
        "respuesta_correcta_m": ejercicio['respuesta_m'],
        "respuesta_correcta_f": ejercicio['respuesta_f'],
        "puntos_ganados": puntos
    })

@app.route('/api/ejercicio/quiz/random', methods=['GET'])
def quiz_random():
    quiz = random.choice(EJERCICIOS_QUIZ)
    return jsonify({
        "id": quiz['id'],
        "pregunta": quiz['pregunta'],
        "opciones": quiz['opciones'],
        "categoria": quiz['categoria'],
        "dificultad": quiz['dificultad']
    })

@app.route('/api/ejercicio/quiz/verificar', methods=['POST'])
def verificar_quiz():
    data = request.json
    quiz = next((q for q in EJERCICIOS_QUIZ if q['id'] == data['quiz_id']), None)
    
    if not quiz:
        return jsonify({"correcto": False})
    
    correcto = data['respuesta'].lower() == quiz['respuesta'].lower()
    puntos = 10 if correcto else 0
    
    return jsonify({
        "correcto": correcto,
        "respuesta_correcta": quiz['respuesta'],
        "puntos_ganados": puntos
    })

@app.route('/api/flashcard/random', methods=['GET'])
def flashcard_random():
    return jsonify(random.choice(FLASHCARDS))

@app.route('/api/flashcard/verificar', methods=['POST'])
def verificar_flashcard():
    return jsonify({"correcto": True})

@app.route('/api/estadisticas/flashcards', methods=['GET'])
def estadisticas_flashcards():
    return jsonify({"total": len(FLASHCARDS), "estudiadas": 5, "porcentaje": 10})

@app.route('/api/estadisticas/completas', methods=['GET'])
def estadisticas_completas():
    return jsonify({
        "usuario": {
            "nombre": "Estudiante",
            "puntos_totales": 150,
            "nivel": 2,
            "nombre_nivel": "Aprendiz",
            "racha_actual": 3,
            "mejor_racha": 5
        },
        "categorias": [
            {"nombre": "Parentesco", "icono": "fa-users", "puntos": 30, "completada": False},
            {"nombre": "Animales", "icono": "fa-paw", "puntos": 45, "completada": False},
            {"nombre": "Títulos", "icono": "fa-crown", "puntos": 20, "completada": False},
            {"nombre": "Profesiones", "icono": "fa-briefcase", "puntos": 35, "completada": False}
        ]
    })

@app.route('/api/ejemplo/guardar', methods=['POST'])
def guardar_ejemplo():
    return jsonify({"success": True})

@app.route('/api/ejemplos/usuario', methods=['GET'])
def obtener_ejemplos():
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
