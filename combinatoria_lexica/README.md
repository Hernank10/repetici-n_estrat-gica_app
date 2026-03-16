# 📚 Combinatoria Léxica - Tutor Interactivo

Aplicación web educativa para aprender y practicar la combinatoria léxica en español.

## ✨ Características

- 🎯 **100 ejercicios interactivos** con 4 niveles de dificultad
- 🃏 **50 flashcards** explicativas con sistema de repaso espaciado
- 📊 **Sistema de progresión** con 5 niveles y medallas
- 🏆 **Logros y recompensas** para motivar el aprendizaje
- 📈 **Dashboard personal** con estadísticas detalladas
- 🌓 **Tema claro/oscuro** ajustable
- 📱 **Diseño responsive** para móviles y tablets
- 📤 **Exportación de progreso** a PDF

## 🚀 Tecnologías utilizadas

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Frontend:** Bootstrap 5, Chart.js, Font Awesome
- **Base de datos:** SQLite
- **Autenticación:** Flask-WTF, email-validator

## 📦 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/Hernank10/combinatoria-lexica.git
cd combinatoria-lexica
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
 Estructura del proyecto
text
combinatoria_lexica/
├── app.py                 # Aplicación principal
├── config.py              # Configuración
├── models.py              # Modelos de base de datos
├── forms.py               # Formularios WTForms
├── utils.py               # Utilidades
├── data/                  # Datos JSON
│   ├── ejercicios.json    # 100 ejercicios
│   ├── flashcards.json    # 50 flashcards
│   └── niveles.json       # Sistema de niveles
├── static/                # Archivos estáticos
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/             # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── flashcards.html
│   ├── ejercicios.html
│   ├── niveles.html
│   ├── perfil.html
│   └── practica.html
└── requirements.txt       # Dependencias
🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor:

Fork el proyecto

Crea una rama (git checkout -b feature/AmazingFeature)

Commit tus cambios (git commit -m 'Add AmazingFeature')

Push a la rama (git push origin feature/AmazingFeature)

Abre un Pull Request

📚 Referencias
Bosque, I. (2004). REDES. Diccionario combinatorio del español contemporáneo. SM.

Bosque, I. (2006). Diccionario práctico de combinaciones léxicas. SM
