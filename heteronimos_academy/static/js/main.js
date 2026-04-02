/* ============================================
   HETERÓNIMOS ACADEMY - FUNCIONES PRINCIPALES
   ============================================ */

// Variables globales
let usuarioActual = null;
let puntuacionTotal = 0;
let nivelActual = 1;

// Mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = 'success') {
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alerta.style.zIndex = '9999';
    alerta.style.minWidth = '300px';
    alerta.style.borderRadius = '15px';
    alerta.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
    alerta.innerHTML = `
        <i class="fas ${tipo === 'success' ? 'fa-check-circle' : tipo === 'danger' ? 'fa-exclamation-circle' : 'fa-info-circle'} me-2"></i>
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alerta);
    
    setTimeout(() => {
        alerta.style.opacity = '0';
        alerta.style.transition = 'opacity 0.3s ease';
        setTimeout(() => alerta.remove(), 300);
    }, 3000);
}

// Cargar progreso global
function cargarProgresoGlobal() {
    fetch('/api/estadisticas/completas')
        .then(res => res.json())
        .then(data => {
            if (data && !data.error && data.usuario) {
                const progresoElement = document.getElementById('progresoGlobal');
                if (progresoElement) {
                    progresoElement.innerHTML = `
                        <span class="badge bg-primary me-2 rounded-pill">Nivel ${data.usuario.nivel}</span>
                        <span class="badge bg-success rounded-pill">${data.usuario.puntos_totales} pts</span>
                    `;
                }
                puntuacionTotal = data.usuario.puntos_totales;
                nivelActual = data.usuario.nivel;
            }
        })
        .catch(() => {});
}

// Animación de entrada
function animarElementos() {
    const elements = document.querySelectorAll('.card-modern, .stat-card');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        setTimeout(() => {
            el.style.transition = 'all 0.5s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Inicializar tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltips.length > 0 && typeof bootstrap !== 'undefined') {
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
    }
}

// Guardar preferencias
function guardarPreferencias(key, value) {
    localStorage.setItem(`heteronimos_${key}`, JSON.stringify(value));
}

// Obtener preferencias
function obtenerPreferencias(key) {
    const data = localStorage.getItem(`heteronimos_${key}`);
    return data ? JSON.parse(data) : null;
}

// Formatear fecha
function formatearFecha(fecha) {
    return new Date(fecha).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Debounce para búsquedas
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Validar email
function validarEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Generar ID único
function generarId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Exportar datos
function exportarDatos(data, nombreArchivo = 'datos_heteronimos.json') {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nombreArchivo;
    a.click();
    URL.revokeObjectURL(url);
}

// Actualizar puntuación
function actualizarPuntuacion(puntos) {
    puntuacionTotal += puntos;
    const puntosElement = document.getElementById('puntosTotales');
    if (puntosElement) {
        puntosElement.textContent = puntuacionTotal;
    }
    
    // Actualizar nivel
    const nuevoNivel = Math.floor(puntuacionTotal / 100) + 1;
    if (nuevoNivel > nivelActual) {
        nivelActual = nuevoNivel;
        mostrarNotificacion(`🎉 ¡Felicidades! Has subido al nivel ${nivelActual}`, 'success');
    }
}

// Registrar usuario
function registrarUsuario(nombre, email) {
    return fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre: nombre, email: email })
    }).then(res => res.json());
}

// Obtener heterónimo aleatorio
function obtenerHeteronimoAleatorio() {
    return fetch('/api/heteronimos/random').then(res => res.json());
}

// Verificar respuesta de completación
function verificarCompletacion(ejercicioId, masculino, femenino) {
    return fetch('/api/ejercicio/completacion/verificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ejercicio_id: ejercicioId,
            masculino: masculino,
            femenino: femenino
        })
    }).then(res => res.json());
}

// Verificar respuesta de quiz
function verificarQuiz(quizId, respuesta) {
    return fetch('/api/ejercicio/quiz/verificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            quiz_id: quizId,
            respuesta: respuesta
        })
    }).then(res => res.json());
}

// Obtener flashcard aleatoria
function obtenerFlashcardAleatorio() {
    return fetch('/api/flashcard/random').then(res => res.json());
}

// Guardar ejemplo personalizado
function guardarEjemploPersonalizado(masculino, femenino, oracion) {
    return fetch('/api/ejemplo/guardar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            masculino: masculino,
            femenino: femenino,
            oracion: oracion
        })
    }).then(res => res.json());
}

// Cargar ejemplos del usuario
function cargarEjemplosUsuario() {
    return fetch('/api/ejemplos/usuario').then(res => res.json());
}

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', () => {
    console.log('🏫 Heterónimos Academy - Plataforma Educativa');
    console.log('🚀 Aplicación lista para usar');
    
    animarElementos();
    initTooltips();
    cargarProgresoGlobal();
    
    // Añadir clase de animación al body
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});

// Exportar funciones globales
window.mostrarNotificacion = mostrarNotificacion;
window.cargarProgresoGlobal = cargarProgresoGlobal;
window.guardarPreferencias = guardarPreferencias;
window.obtenerPreferencias = obtenerPreferencias;
window.validarEmail = validarEmail;
window.exportarDatos = exportarDatos;
window.actualizarPuntuacion = actualizarPuntuacion;
window.registrarUsuario = registrarUsuario;
window.obtenerHeteronimoAleatorio = obtenerHeteronimoAleatorio;
window.verificarCompletacion = verificarCompletacion;
window.verificarQuiz = verificarQuiz;
window.obtenerFlashcardAleatorio = obtenerFlashcardAleatorio;
window.guardarEjemploPersonalizado = guardarEjemploPersonalizado;
window.cargarEjemplosUsuario = cargarEjemplosUsuario;
window.formatearFecha = formatearFecha;
window.generarId = generarId;
