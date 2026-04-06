# 🎯 Claridad Técnica

> *"No importa repetir si se repite lo que importa"* — **Ángel Zapata**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask 2.3+](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📚 Descripción

**Claridad Técnica** es una plataforma educativa diseñada para enseñar el principio de **repetición estratégica** en la comunicación técnica. Ayuda a redactores, ingenieros, programadores y profesionales técnicos a eliminar ambigüedades mediante ejercicios interactivos y flashcards.

### 🎯 ¿Por qué es importante?

En entornos técnicos, la comunicación ambigua puede generar:
- ❌ Accidentes laborales
- ❌ Errores en procedimientos médicos
- ❌ Malinterpretación de manuales
- ❌ Bugs en software por documentación confusa

**Claridad Técnica** resuelve este problema enseñando a **repetir términos técnicos** en lugar de usar sinónimos innecesarios.

## ✨ Características

| Característica | Descripción |
|----------------|-------------|
| ✅ **100+ Ejercicios** | Corrección de textos y completar espacios |
| ✅ **60+ Flashcards** | Tarjetas de estudio para reforzar conceptos |
| ✅ **Sistema de Puntaje** | 10 pts por ejercicio, 5 pts por flashcard |
| ✅ **Rachas y Logros** | Motivación mediante gamificación |
| ✅ **Panel de Administración** | Gestión completa de usuarios y contenido |
| ✅ **API RESTful** | Integración con aplicaciones externas |
| ✅ **Diseño Responsive** | Funciona en móvil, tablet y escritorio |
| ✅ **Base de Datos SQLite** | Ligera y sin configuración compleja |

## 🚀 Instalación Rápida

### Requisitos previos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

### Pasos de instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/claridad-tecnica.git
cd claridad-tecnica

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Inicializar base de datos
python -c "from app import init_db; init_db()"

# 5. Ejecutar la aplicación
python app.py

Acceso a la aplicación
Rol	Email	Contraseña
Administrador	admin@claridad.com	admin123
Usuario	(registrarse)	(elegir)
Abre tu navegador en: http://localhost:5000

📁 Estructura del Proyecto
text
claridad-tecnica/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias del proyecto
├── README.md              # Este archivo
├── .gitignore             # Archivos ignorados por Git
│
├── data/                  # Datos de la aplicación
│   ├── ejercicios.json    # 100+ ejercicios
│   ├── flashcards.json    # 60+ flashcards
│   ├── config.json        # Configuración
│   └── usuarios.db        # Base de datos SQLite
│
├── static/                # Archivos estáticos
│   ├── css/
│   │   └── style.css      # Estilos CSS
│   ├── js/
│   │   └── main.js        # JavaScript
│   └── downloads/         # Archivos descargables
│
└── templates/             # Plantillas HTML
    ├── base.html          # Plantilla base
    ├── index.html         # Página de inicio
    ├── login.html         # Inicio de sesión
    ├── registro.html      # Registro de usuarios
    ├── dashboard.html     # Panel de usuario
    ├── teoria.html        # Contenido teórico
    ├── ejercicios.html    # Ejercicios interactivos
    ├── flashcards.html    # Flashcards
    ├── progreso.html      # Progreso del usuario
    ├── perfil.html        # Perfil de usuario
    ├── demostracion/      # Demostraciones de código
    └── admin/             # Panel de administración
🛠️ Tecnologías Utilizadas
Capa	Tecnología	Versión
Backend	Python + Flask	3.9+ / 2.3+
Base de Datos	SQLite	3.x
Frontend	Bootstrap 5	5.3.0
JavaScript	Vanilla JS	ES6+
Autenticación	Werkzeug	2.3+
API	RESTful	JSON
📖 Uso de la Aplicación
Para Usuarios
Regístrate como nuevo usuario

Estudia la teoría sobre repetición estratégica

Completa ejercicios para ganar puntos

Repasa con flashcards para reforzar conceptos

Sigue tu progreso en el dashboard

Para Administradores
Inicia sesión con admin@claridad.com / admin123

Accede al Panel de Administración

Gestiona usuarios, ejercicios y flashcards

Genera nuevo contenido automáticamente

Revisa estadísticas del sistema

🔧 Configuración Avanzada
Cambiar el puerto del servidor
python
# En app.py, modificar la última línea:
app.run(debug=True, host='0.0.0.0', port=5001)
Modo producción
python
# Desactivar debug mode
app.run(debug=False, host='0.0.0.0', port=5000)
Personalizar colores
Edita static/css/style.css y modifica las variables CSS:

css
:root {
    --primary-color: #2c3e50;  /* Cambia por tu color */
    --secondary-color: #3498db;
}
📊 API Endpoints
Endpoint	Método	Descripción
/api/ejercicios	GET	Obtener todos los ejercicios
/api/ejercicios_pendientes	GET	Ejercicios no completados
/api/verificar_ejercicio	POST	Verificar respuesta
/api/flashcards	GET	Obtener flashcards
/api/flashcards_pendientes	GET	Flashcards no dominadas
/api/marcar_flashcard	POST	Marcar flashcard como dominada
/api/progreso	GET	Obtener progreso del usuario
🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor:

Fork el proyecto

Crea tu rama (git checkout -b feature/AmazingFeature)

Commit tus cambios (git commit -m 'Add some AmazingFeature')

Push a la rama (git push origin feature/AmazingFeature)

Abre un Pull Request

📝 Licencia
Distribuido bajo la licencia MIT. Ver LICENSE para más información.

📧 Contacto
Email: equipo@claridadtecnica.com

GitHub: github.com/tu-usuario/claridad-tecnica

Demo: [próximamente]

🙏 Agradecimientos
A Ángel Zapata por su inspiradora frase

A la comunidad de Flask y Bootstrap

A todos los contribuidores y usuarios

📊 Estadísticas del Proyecto
Métrica	Valor
Líneas de código	~2,500
Ejercicios	100+
Flashcards	60+
Templates HTML	15+
Endpoints API	12
🚀 ¡Comienza a usar Claridad Técnica hoy mismo!
bash
python app.py
# Abre http://localhost:5000
Hecho con ❤️ para mejorar la comunicación técnica en el mundo

Última actualización: Abril 2024

text

---


