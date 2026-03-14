# 🎓 Academia Digital

Plataforma educativa interactiva con juegos de aprendizaje, perfiles de usuario, logros y sistema social.

## 🚀 Características

- **Múltiples juegos educativos**: Aventura y Ortografía
- **Sistema de perfiles**: Cada usuario tiene su perfil, inventario y estadísticas
- **Logros y recompensas**: Sistema completo de logros desbloqueables
- **Red social interna**: Amigos, mensajes y notificaciones
- **Ranking en tiempo real**: Competencia sana entre estudiantes
- **Internacionalización**: Soporte para 16 idiomas
- **Panel administrativo**: Gestión completa de la plataforma

## 🛠️ Tecnologías

- **Backend**: Django 4.2.7
- **Frontend**: Bootstrap 5, JavaScript
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Internacionalización**: Django i18n
- **API**: Django REST Framework

## 📋 Requisitos

- Python 3.10+
- pip
- virtualenv (recomendado)

## 🔧 Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/academia-digital.git
cd academia-digital

# Crear entorno virtual
python -m venv venv source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Migrar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
🌐 Idiomas soportados
Español (es), English (en), Français (fr), Português (pt)

Deutsch (de), Italiano (it), 中文 (zh-hans, zh-hant)

日本語 (ja), 한국어 (ko), العربية (ar), עברית (he)

Русский (ru), Català (ca), Galego (gl), Euskara (eu)

📁 Estructura del proyecto
text
academia_digital/
├── core/           # App principal (perfiles, autenticación, social)
├── juegos/         # App de juegos (aventura, ortografía)
├── ejercicios/     # App de ejercicios
├── academia_digital/ # Configuración del proyecto
├── locale/         # Archivos de traducción
├── static/         # Archivos estáticos
├── media/          # Archivos subidos
└── templates/      # Plantillas HTML
📄 Licencia
MIT License
EOF

text
