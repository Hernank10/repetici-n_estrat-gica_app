#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
init_data.py - Script para inicializar la base de datos de ejercicios y flashcards
Ejecutar con: python init_data.py
"""

import json
import os
import random
from datetime import datetime

# Configuración de archivos
DATA_DIR = 'data'
EJERCICIOS_FILE = os.path.join(DATA_DIR, 'ejercicios_completos.json')
FLASHCARDS_FILE = os.path.join(DATA_DIR, 'flashcards.json')
EJEMPLOS_FILE = os.path.join(DATA_DIR, 'ejemplos.json')
USUARIOS_FILE = os.path.join(DATA_DIR, 'usuarios.json')

def asegurar_directorio():
    """Asegura que el directorio data existe"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📁 Directorio '{DATA_DIR}' creado")
    else:
        print(f"📁 Directorio '{DATA_DIR}' ya existe")

def generar_100_ejercicios():
    """Genera 100 ejercicios distribuidos por categorías"""
    
    categorias = ['Comas', 'Paréntesis', 'Rayas', 'Geográficos', 'Siglas']
    dificultades = ['fácil', 'media', 'difícil']
    
    # Bases de oraciones por categoría
    bases = {
        'Comas': [
            "El presidente {} anunció nuevas medidas económicas.",
            "La ciudad {} es famosa por su arquitectura colonial.",
            "El profesor {} explicó la lección con claridad.",
            "El libro {} fue un bestseller internacional.",
            "La película {} ganó varios premios Oscar.",
            "El director {} presentó su nueva obra.",
            "La empresa {} lanzó un producto innovador.",
            "El equipo {} ganó el campeonato nacional.",
            "La obra {} fue escrita en el siglo XIX.",
            "El científico {} descubrió una nueva especie."
        ],
        'Paréntesis': [
            "El COVID-19 {} cambió radicalmente el mundo.",
            "La ONU {} fue fundada después de la Segunda Guerra Mundial.",
            "El telescopio Hubble {} revolucionó la astronomía.",
            "La empresa Tesla {} lidera la industria de vehículos eléctricos.",
            "El tratado de Versalles {} puso fin a la Primera Guerra Mundial.",
            "La OMS {} declaró la emergencia sanitaria global.",
            "El proyecto Manhattan {} desarrolló la primera bomba atómica.",
            "La NASA {} logró llevar al hombre a la luna.",
            "El museo del Louvre {} alberga la Mona Lisa.",
            "La FIFA {} organiza el mundial de fútbol cada cuatro años."
        ],
        'Rayas': {
            "El resultado {} sorprendió a todos los analistas.",
            "La decisión {} fue controversial en la opinión pública.",
            "El discurso {} conmovió a toda la audiencia.",
            "El descubrimiento {} cambió el rumbo de la ciencia.",
            "La noticia {} impactó al mundo entero.",
            "El experimento {} demostró la teoría de Einstein.",
            "La declaración {} generó un debate nacional.",
            "El hallazgo {} fue publicado en Nature.",
            "La propuesta {} recibió apoyo unánime.",
            "El accidente {} evitó una tragedia mayor."
        ],
        'Geográficos': {
            "París {} es conocida como la Ciudad Luz.",
            "El Amazonas {} es el río más caudaloso del mundo.",
            "Los Andes {} son la cordillera más larga de Sudamérica.",
            "El Sahara {} es el desierto cálido más grande.",
            "Australia {} es el país más pequeño de Oceanía.",
            "El Himalaya {} alberga las montañas más altas.",
            "Venecia {} es famosa por sus canales.",
            "La Patagonia {} ofrece paisajes espectaculares.",
            "El Nilo {} es el río más largo de África.",
            "Machu Picchu {} es una maravilla del mundo moderno."
        ],
        'Siglas': {
            "La NASA {} lanzó una nueva misión a Marte.",
            "La FIFA {} anunció cambios en las reglas del fútbol.",
            "La OMS {} recomienda vacunarse anualmente.",
            "La UNESCO {} declaró patrimonio de la humanidad.",
            "La OTAN {} celebró una cumbre extraordinaria.",
            "El FMI {} aprobó un nuevo préstamo.",
            "La ONU {} convocó a una asamblea general.",
            "La OEA {} medió en el conflicto diplomático.",
            "El CERN {} anunció un descubrimiento importante.",
            "La OMC {} reguló las disputas comerciales."
        }
    }
    
    # Incisos por categoría
    incisos = {
        'Comas': [
            "electo democráticamente", "capital de Francia", "experto en la materia",
            "publicado en 2020", "dirigida por un famoso director", "reconocido mundialmente",
            "fundada en 1990", "campeón defensor", "escrita por Cervantes", "premio Nobel"
        ],
        'Paréntesis': [
            "descubierto en 2019", "Organización de las Naciones Unidas",
            "lanzado en 1990", "fundada por Elon Musk", "firmado en 1919",
            "Organización Mundial de la Salud", "1942-1946", "National Aeronautics and Space Administration",
            "inaugurado en 1793", "Fédération Internationale de Football Association"
        ],
        'Rayas': [
            "inesperado por todos", "tomada tras largas deliberaciones",
            "pronunciado con pasión", "realizado por accidente",
            "difundida globalmente", "controvertido pero necesario",
            "inédito hasta ahora", "revelador para la comunidad científica",
            "aprobada por unanimidad", "evitado por segundos"
        ],
        'Geográficos': [
            "capital de Francia", "el más caudaloso del mundo",
            "la cordillera más larga", "el desierto más extenso",
            "el país más pequeño", "la cadena montañosa más alta",
            "la ciudad de los canales", "región austral de Argentina",
            "el río más largo", "ciudad inca en los Andes"
        ],
        'Siglas': [
            "National Aeronautics and Space Administration",
            "Fédération Internationale de Football Association",
            "Organización Mundial de la Salud",
            "Organización de las Naciones Unidas para la Educación",
            "Organización del Tratado del Atlántico Norte",
            "Fondo Monetario Internacional",
            "Organización de las Naciones Unidas",
            "Organización de Estados Americanos",
            "Conseil Européen pour la Recherche Nucléaire",
            "Organización Mundial del Comercio"
        ]
    }
    
    ejercicios = []
    
    for i in range(100):
        categoria = random.choice(categorias)
        dificultad = random.choice(dificultades)
        
        # Seleccionar base e inciso según categoría
        if categoria == 'Rayas':
            base_list = bases['Rayas']
            inciso_list = incisos['Rayas']
        elif categoria == 'Geográficos':
            base_list = bases['Geográficos']
            inciso_list = incisos['Geográficos']
        elif categoria == 'Siglas':
            base_list = bases['Siglas']
            inciso_list = incisos['Siglas']
        else:
            base_list = bases[categoria]
            inciso_list = incisos[categoria]
        
        base = random.choice(base_list)
        inciso = random.choice(inciso_list)
        
        # Determinar puntuación según categoría
        if categoria in ['Comas', 'Rayas', 'Paréntesis']:
            puntuacion = categoria.lower()
        else:
            puntuacion = random.choice(['comas', 'paréntesis', 'rayas'])
        
        ejercicio = {
            'id': i + 1,
            'base': base,
            'inciso': inciso,
            'categoria': categoria,
            'puntuacion': puntuacion,
            'dificultad': dificultad,
            'pistas': [
                f"Usa {puntuacion} para separar el inciso",
                f"El inciso es: '{inciso[:30]}...'",
                f"Categoría: {categoria}"
            ],
            'fecha_creacion': datetime.now().isoformat()
        }
        ejercicios.append(ejercicio)
    
    return ejercicios

def generar_50_flashcards():
    """Genera 50 flashcards explicativas sobre incisos"""
    
    conceptos_base = [
        {
            'titulo': 'Inciso Explicativo',
            'definicion': 'Elemento sintáctico que añade información adicional entre comas, paréntesis o rayas sin alterar la estructura principal de la oración.',
            'ejemplo': 'Londres, capital del Reino Unido, tiene 9 millones de habitantes',
            'categoria': 'Conceptos básicos'
        },
        {
            'titulo': 'Comas Explicativas',
            'definicion': 'Se usan para introducir información relacionada o aclaratoria que complementa el significado de la oración.',
            'ejemplo': 'El director, Sr. Rodríguez, anunció cambios importantes en la empresa',
            'categoria': 'Comas'
        },
        {
            'titulo': 'Paréntesis',
            'definicion': 'Se utilizan para datos técnicos, fechas, siglas o información secundaria que no interrumpe el flujo principal.',
            'ejemplo': 'El COVID-19 (descubierto en 2019) cambió radicalmente nuestras vidas',
            'categoria': 'Paréntesis'
        },
        {
            'titulo': 'Rayas',
            'definicion': 'Se emplean para dar énfasis, introducir interrupciones o citas textuales dentro de la oración.',
            'ejemplo': 'El resultado —totalmente inesperado— sorprendió a todos los analistas',
            'categoria': 'Rayas'
        },
        {
            'titulo': 'Contexto Geográfico',
            'definicion': 'Incisos que proporcionan información sobre ubicaciones, características geográficas o datos de lugares.',
            'ejemplo': 'París, capital de Francia y ciudad del amor, es conocida como la Ciudad Luz',
            'categoria': 'Geográficos'
        },
        {
            'titulo': 'Siglas y Acrónimos',
            'definicion': 'Se utilizan paréntesis para explicar el significado completo de siglas o acrónimos.',
            'ejemplo': 'La NASA (National Aeronautics and Space Administration) lanzó una misión histórica',
            'categoria': 'Siglas'
        }
    ]
    
    # Variaciones de ejemplos por categoría
    ejemplos_variados = {
        'Comas': [
            "El presidente, electo por mayoría absoluta, tomará posesión mañana",
            "La ciudad, fundada en 1538 por los españoles, conserva su arquitectura colonial",
            "El profesor, experto en lingüística, publicó un nuevo libro",
            "El medicamento, aprobado por la FDA, estará disponible en farmacias",
            "La novela, escrita en el siglo XIX, sigue siendo relevante hoy"
        ],
        'Paréntesis': [
            "El proyecto Manhattan (1942-1946) desarrolló las primeras armas nucleares",
            "La OMS (Organización Mundial de la Salud) declaró el fin de la pandemia",
            "El telescopio James Webb (lanzado en 2021) reveló imágenes impresionantes",
            "La empresa Apple (fundada en 1976) revolucionó la tecnología",
            "El tratado de Maastricht (firmado en 1992) creó la Unión Europea"
        ],
        'Rayas': [
            "El descubrimiento —totalmente accidental— cambió el rumbo de la ciencia",
            "La decisión —tomada por unanimidad— fue bien recibida",
            "El discurso —pronunciado con gran emoción— conmovió a todos",
            "El experimento —repetido cien veces— demostró la teoría",
            "La noticia —confirmada por fuentes oficiales— impactó al mundo"
        ],
        'Geográficos': [
            "El Amazonas, el río más caudaloso del mundo, atraviesa Sudamérica",
            "Los Andes, la cordillera más larga, se extienden por siete países",
            "Venecia, la ciudad de los canales, está construida sobre 118 islas",
            "El Sahara, el desierto cálido más grande, cubre 9 millones de km²",
            "Machu Picchu, la ciudad perdida de los incas, es una maravilla mundial"
        ],
        'Siglas': [
            "La FIFA (Fédération Internationale de Football Association) organiza el mundial",
            "La UNESCO (Organización de las Naciones Unidas para la Educación) protege el patrimonio",
            "El FMI (Fondo Monetario Internacional) aprobó un rescate financiero",
            "La OTAN (Organización del Tratado del Atlántico Norte) celebra su 75 aniversario",
            "El CERN (Conseil Européen pour la Recherche Nucléaire) descubrió el bosón de Higgs"
        ]
    }
    
    flashcards = []
    
    # Generar 50 flashcards
    for i in range(50):
        # Seleccionar concepto base
        concepto = random.choice(conceptos_base)
        
        # Crear flashcard
        flashcard = {
            'id': i + 1,
            'titulo': concepto['titulo'],
            'definicion': concepto['definicion'],
            'categoria': concepto['categoria'],
            'nivel': random.choice(['básico', 'intermedio', 'avanzado']),
            'fecha_creacion': datetime.now().isoformat()
        }
        
        # Asignar ejemplo según categoría
        if concepto['categoria'] in ejemplos_variados:
            flashcard['ejemplo'] = random.choice(ejemplos_variados[concepto['categoria']])
        else:
            flashcard['ejemplo'] = concepto['ejemplo']
        
        # Añadir datos adicionales para variedad
        if i % 5 == 0:
            flashcard['nota_adicional'] = "💡 Recuerda: los incisos siempre van entre signos de puntuación"
        elif i % 5 == 1:
            flashcard['nota_adicional'] = "📝 Si eliminas el inciso, la oración debe mantener sentido"
        elif i % 5 == 2:
            flashcard['nota_adicional'] = "⚠️ Máximo 2 incisos por oración para mantener claridad"
        elif i % 5 == 3:
            flashcard['nota_adicional'] = "🎯 Practica con ejercicios interactivos en la sección Práctica"
        else:
            flashcard['nota_adicional'] = "🏆 Cada flashcard completada te da 5 puntos"
        
        flashcards.append(flashcard)
    
    return flashcards

def crear_archivo_ejemplos_vacios():
    """Crea un archivo vacío para ejemplos de usuarios"""
    if not os.path.exists(EJEMPLOS_FILE):
        with open(EJEMPLOS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"✅ Archivo '{EJEMPLOS_FILE}' creado")
    else:
        print(f"📁 Archivo '{EJEMPLOS_FILE}' ya existe")

def crear_archivo_usuarios_vacio():
    """Crea un archivo vacío para usuarios"""
    if not os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"✅ Archivo '{USUARIOS_FILE}' creado")
    else:
        print(f"📁 Archivo '{USUARIOS_FILE}' ya existe")

def guardar_ejercicios(ejercicios):
    """Guarda los ejercicios en archivo JSON"""
    with open(EJERCICIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ejercicios, f, ensure_ascii=False, indent=2)
    print(f"✅ {len(ejercicios)} ejercicios guardados en '{EJERCICIOS_FILE}'")

def guardar_flashcards(flashcards):
    """Guarda las flashcards en archivo JSON"""
    with open(FLASHCARDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(flashcards, f, ensure_ascii=False, indent=2)
    print(f"✅ {len(flashcards)} flashcards guardadas en '{FLASHCARDS_FILE}'")

def mostrar_resumen(ejercicios, flashcards):
    """Muestra un resumen de los datos generados"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE INICIALIZACIÓN")
    print("="*60)
    
    # Resumen de ejercicios
    print(f"\n📝 EJERCICIOS ({len(ejercicios)} total):")
    categorias = {}
    dificultades = {}
    for ej in ejercicios:
        cat = ej['categoria']
        dif = ej['dificultad']
        categorias[cat] = categorias.get(cat, 0) + 1
        dificultades[dif] = dificultades.get(dif, 0) + 1
    
    for cat, count in categorias.items():
        print(f"   • {cat}: {count} ejercicios")
    
    print("\n   Por dificultad:")
    for dif, count in dificultades.items():
        print(f"     - {dif}: {count}")
    
    # Resumen de flashcards
    print(f"\n🃏 FLASHCARDS ({len(flashcards)} total):")
    flash_cats = {}
    for fc in flashcards:
        cat = fc['categoria']
        flash_cats[cat] = flash_cats.get(cat, 0) + 1
    
    for cat, count in flash_cats.items():
        print(f"   • {cat}: {count} flashcards")
    
    print("\n" + "="*60)
    print("✅ Inicialización completada exitosamente!")
    print("🚀 Ejecuta 'python run.py' para iniciar la aplicación")
    print("="*60)

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔄 INICIALIZANDO BASE DE DATOS DE INCISOS EXPLICATIVOS")
    print("="*60)
    
    # Asegurar directorio data
    asegurar_directorio()
    
    # Generar ejercicios
    print("\n📝 Generando 100 ejercicios...")
    ejercicios = generar_100_ejercicios()
    guardar_ejercicios(ejercicios)
    
    # Generar flashcards
    print("\n🃏 Generando 50 flashcards...")
    flashcards = generar_50_flashcards()
    guardar_flashcards(flashcards)
    
    # Crear archivos vacíos
    print("\n📁 Creando archivos adicionales...")
    crear_archivo_ejemplos_vacios()
    crear_archivo_usuarios_vacio()
    
    # Mostrar resumen
    mostrar_resumen(ejercicios, flashcards)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {str(e)}")
        raise
