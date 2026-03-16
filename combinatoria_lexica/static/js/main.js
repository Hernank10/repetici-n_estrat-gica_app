// ============================================
// ARCHIVO PRINCIPAL DE JAVASCRIPT
// Combinatoria Léxica - Funciones Globales
// ============================================

// ============================================
// VARIABLES GLOBALES
// ============================================
const API_BASE_URL = '';
const USER_ID = document.querySelector('meta[name="user-id"]')?.content || null;
const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.content || '';

// ============================================
// INICIALIZACIÓN
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Aplicación iniciada');
    
    inicializarTema();
    inicializarTooltips();
    inicializarPopovers();
    inicializarNotificaciones();
    inicializarFormularios();
    inicializarAnimaciones();
    
    // Cargar datos del usuario si está autenticado
    if (USER_ID) {
        cargarDatosUsuario();
    }
});

// ============================================
// SISTEMA DE TEMAS
// ============================================
function inicializarTema() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    
    if (themeToggle) {
        // Cargar tema guardado
        const savedTheme = localStorage.getItem('theme') || 'light';
        aplicarTema(savedTheme);
        
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            aplicarTema(newTheme);
            
            // Guardar preferencia
            localStorage.setItem('theme', newTheme);
            
            // Enviar al servidor si el usuario está autenticado
            if (USER_ID) {
                fetch('/api/user/theme', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': CSRF_TOKEN
                    },
                    body: JSON.stringify({ theme: newTheme })
                }).catch(error => console.error('Error guardando tema:', error));
            }
        });
    }
    
    // Botones de tema en dropdown
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const theme = this.dataset.theme;
            aplicarTema(theme);
            localStorage.setItem('theme', theme);
            
            if (USER_ID) {
                fetch('/api/user/theme', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': CSRF_TOKEN
                    },
                    body: JSON.stringify({ theme: theme })
                }).catch(error => console.error('Error guardando tema:', error));
            }
        });
    });
}

function aplicarTema(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-bs-theme', theme);
    
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = theme === 'light' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    }
    
    // Disparar evento para componentes que necesiten reaccionar al cambio de tema
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: theme } }));
}

// ============================================
// COMPONENTES DE BOOTSTRAP
// ============================================
function inicializarTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function inicializarPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function inicializarNotificaciones() {
    // Cargar notificaciones cada 30 segundos si el usuario está autenticado
    if (USER_ID) {
        cargarNotificaciones();
        setInterval(cargarNotificaciones, 30000);
    }
}

function cargarNotificaciones() {
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            actualizarBadgeNotificaciones(data.length);
            actualizarListaNotificaciones(data);
        })
        .catch(error => console.error('Error cargando notificaciones:', error));
}

function actualizarBadgeNotificaciones(count) {
    const badge = document.getElementById('notificationBadge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 9 ? '9+' : count;
            badge.classList.remove('d-none');
        } else {
            badge.classList.add('d-none');
        }
    }
}

function actualizarListaNotificaciones(notificaciones) {
    const container = document.getElementById('notificationsList');
    if (!container) return;
    
    if (notificaciones.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-3">
                <i class="bi bi-bell-slash fs-1 d-block mb-2"></i>
                <small>No hay notificaciones</small>
            </div>
        `;
        return;
    }
    
    container.innerHTML = notificaciones.map(notif => `
        <div class="dropdown-item notification-item ${notif.leida ? '' : 'fw-bold'}" data-id="${notif.id}">
            <div class="d-flex align-items-center">
                <span class="notification-icon me-2">${notif.icono || '📌'}</span>
                <div class="flex-grow-1">
                    <div class="small fw-semibold">${notif.titulo}</div>
                    <div class="small text-muted">${notif.mensaje}</div>
                    <small class="text-muted">${notif.created_at}</small>
                </div>
                ${notif.leida ? '' : '<span class="badge bg-primary">Nueva</span>'}
            </div>
        </div>
    `).join('');
    
    // Marcar como leídas al hacer clic
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            const id = this.dataset.id;
            marcarNotificacionLeida(id);
        });
    });
}

function marcarNotificacionLeida(id) {
    fetch(`/api/notifications/${id}/read`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': CSRF_TOKEN
        }
    })
    .then(() => {
        cargarNotificaciones();
    })
    .catch(error => console.error('Error marcando notificación:', error));
}

// ============================================
// FORMULARIOS
// ============================================
function inicializarFormularios() {
    // Validación de Bootstrap
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Mostrar/ocultar contraseña
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.querySelector('i').classList.toggle('bi-eye');
            this.querySelector('i').classList.toggle('bi-eye-slash');
        });
    });
}

// ============================================
// ANIMACIONES
// ============================================
function inicializarAnimaciones() {
    // Observador de intersección para animaciones al hacer scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

function crearConfeti() {
    const duration = 3000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };
    
    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }
    
    const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now();
        
        if (timeLeft <= 0) {
            return clearInterval(interval);
        }
        
        const particleCount = 50 * (timeLeft / duration);
        confetti(Object.assign({}, defaults, { 
            particleCount, 
            origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
        }));
        confetti(Object.assign({}, defaults, { 
            particleCount, 
            origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
        }));
    }, 250);
}

// ============================================
// UTILIDADES
// ============================================
function cargarDatosUsuario() {
    fetch('/api/user/stats')
        .then(response => response.json())
        .then(data => {
            window.userStats = data;
            actualizarBarraXP(data);
        })
        .catch(error => console.error('Error cargando datos del usuario:', error));
}

function actualizarBarraXP(data) {
    const xpBar = document.getElementById('xpProgressBar');
    const xpDisplay = document.getElementById('xpDisplay');
    
    if (xpBar && xpDisplay) {
        xpBar.style.width = data.progreso_nivel + '%';
        xpDisplay.textContent = data.xp + ' XP';
    }
}

function mostrarToast(mensaje, tipo = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${tipo} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${mensaje}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.getElementById('toastContainer').appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function mostrarLoading(selector) {
    const elemento = document.querySelector(selector);
    if (elemento) {
        elemento.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            </div>
        `;
    }
}

function formatearFecha(fecha) {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatearTiempo(segundos) {
    const horas = Math.floor(segundos / 3600);
    const minutos = Math.floor((segundos % 3600) / 60);
    const segs = segundos % 60;
    
    if (horas > 0) {
        return `${horas}h ${minutos}m`;
    } else if (minutos > 0) {
        return `${minutos}m ${segs}s`;
    } else {
        return `${segs}s`;
    }
}

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

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================
// COOKIES Y ALMACENAMIENTO
// ============================================
function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

function getCookie(name) {
    const cookieName = name + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(cookieName) == 0) {
            return c.substring(cookieName.length, c.length);
        }
    }
    return "";
}

function deleteCookie(name) {
    document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

function guardarDatosLocal(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
        console.error('Error guardando en localStorage:', e);
    }
}

function obtenerDatosLocal(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (e) {
        console.error('Error leyendo de localStorage:', e);
        return null;
    }
}

// ============================================
// EVENTOS GLOBALES
// ============================================
window.addEventListener('online', function() {
    mostrarToast('¡Conexión restablecida!', 'success');
});

window.addEventListener('offline', function() {
    mostrarToast('Sin conexión a internet', 'warning');
});

window.addEventListener('error', function(event) {
    console.error('Error global:', event.error);
});

// ============================================
// EXPORTAR FUNCIONES PARA USO GLOBAL
// ============================================
window.CombinatoriaLexica = {
    mostrarToast,
    crearConfeti,
    formatearFecha,
    formatearTiempo,
    debounce,
    throttle,
    setCookie,
    getCookie,
    deleteCookie,
    guardarDatosLocal,
    obtenerDatosLocal
};

console.log('✅ main.js cargado correctamente');
