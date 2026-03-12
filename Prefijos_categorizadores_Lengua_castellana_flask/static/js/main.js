/* ============================================
   ECOSISTEMA MORFOLOGÍA - MAIN.JS
   ============================================ */

// ============================================
// INICIALIZACIÓN GLOBAL
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Ecosistema Morfología iniciado');
    
    inicializarTooltips();
    inicializarNotificaciones();
    inicializarAnimaciones();
    inicializarFormularios();
    inicializarEventosGlobales();
    cargarPreferenciasUsuario();
    verificarNotificaciones();
});

// ============================================
// CONFIGURACIÓN INICIAL
// ============================================
function inicializarTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            animation: true,
            delay: { show: 500, hide: 100 }
        });
    });
}

function inicializarNotificaciones() {
    window.notificaciones = {
        mostrar: function(mensaje, tipo = 'info', duracion = 5000) {
            const colores = {
                success: '#84fab0',
                error: '#fc8181',
                warning: '#f6d365',
                info: '#6B73FF'
            };
            
            const iconos = {
                success: 'bi-check-circle-fill',
                error: 'bi-exclamation-circle-fill',
                warning: 'bi-exclamation-triangle-fill',
                info: 'bi-info-circle-fill'
            };
            
            const notificacion = document.createElement('div');
            notificacion.className = `notificacion notificacion-${tipo} fade-in`;
            notificacion.innerHTML = `
                <i class="bi ${iconos[tipo]} me-2"></i>
                <span>${mensaje}</span>
                <button class="btn-close ms-3" onclick="this.parentElement.remove()"></button>
            `;
            
            notificacion.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${colores[tipo]};
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                z-index: 9999;
                display: flex;
                align-items: center;
                max-width: 400px;
                animation: slideInRight 0.3s ease;
            `;
            
            document.body.appendChild(notificacion);
            
            setTimeout(() => {
                notificacion.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => notificacion.remove(), 300);
            }, duracion);
        },
        
        exito: function(mensaje) {
            this.mostrar(mensaje, 'success');
        },
        
        error: function(mensaje) {
            this.mostrar(mensaje, 'error');
        },
        
        advertencia: function(mensaje) {
            this.mostrar(mensaje, 'warning');
        },
        
        info: function(mensaje) {
            this.mostrar(mensaje, 'info');
        }
    };
}

function inicializarAnimaciones() {
    // Observador de intersección para animaciones al hacer scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

function inicializarFormularios() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (this.classList.contains('ajax-form')) {
                e.preventDefault();
                enviarFormularioAjax(this);
            }
        });
    });
}

function inicializarEventosGlobales() {
    // Tecla Escape para cerrar modales
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(modal => {
                bootstrap.Modal.getInstance(modal).hide();
            });
        }
    });
    
    // Clic fuera de dropdowns para cerrarlos
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

function cargarPreferenciasUsuario() {
    const tema = localStorage.getItem('tema') || 'claro';
    document.body.classList.add(`tema-${tema}`);
}

function verificarNotificaciones() {
    // Verificar notificaciones pendientes cada 30 segundos
    setInterval(() => {
        if (currentUser?.id) {
            fetch('/api/notificaciones-pendientes')
                .then(response => response.json())
                .then(data => {
                    if (data.notificaciones && data.notificaciones.length > 0) {
                        data.notificaciones.forEach(notif => {
                            window.notificaciones.mostrar(notif.mensaje, notif.tipo);
                        });
                    }
                });
        }
    }, 30000);
}

// ============================================
// FUNCIONES DE UTILIDAD
// ============================================
window.utils = {
    // Formatear fechas
    formatearFecha: function(fecha) {
        const d = new Date(fecha);
        const hoy = new Date();
        const ayer = new Date(hoy);
        ayer.setDate(ayer.getDate() - 1);
        
        if (d.toDateString() === hoy.toDateString()) {
            return 'Hoy ' + d.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
        } else if (d.toDateString() === ayer.toDateString()) {
            return 'Ayer ' + d.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
        } else {
            return d.toLocaleDateString('es-ES', { 
                day: '2-digit', 
                month: '2-digit', 
                year: 'numeric' 
            });
        }
    },
    
    // Validar email
    validarEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Sanitizar texto
    sanitizar: function(texto) {
        const div = document.createElement('div');
        div.textContent = texto;
        return div.innerHTML;
    },
    
    // Generar ID único
    generarId: function() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },
    
    // Formatear número con separadores de miles
    formatearNumero: function(num) {
        return new Intl.NumberFormat('es-ES').format(num);
    },
    
    // Truncar texto
    truncar: function(texto, longitud = 100) {
        if (texto.length <= longitud) return texto;
        return texto.substr(0, longitud) + '...';
    },
    
    // Obtener parámetros de URL
    getUrlParams: function() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        for (const [key, value] of params) {
            result[key] = value;
        }
        return result;
    },
    
    // Debounce para búsquedas
    debounce: function(func, wait) {
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
};

// ============================================
// FUNCIONES DE API
// ============================================
window.api = {
    baseUrl: '',
    
    async get(endpoint) {
        try {
            const response = await fetch(this.baseUrl + endpoint, {
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    },
    
    async post(endpoint, data) {
        try {
            const response = await fetch(this.baseUrl + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    },
    
    async put(endpoint, data) {
        try {
            const response = await fetch(this.baseUrl + endpoint, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API PUT Error:', error);
            throw error;
        }
    },
    
    async delete(endpoint) {
        try {
            const response = await fetch(this.baseUrl + endpoint, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API DELETE Error:', error);
            throw error;
        }
    }
};

// ============================================
// FUNCIONES DE ALMACENAMIENTO LOCAL
// ============================================
window.storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Error guardando en localStorage:', e);
            return false;
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error leyendo de localStorage:', e);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('Error eliminando de localStorage:', e);
            return false;
        }
    },
    
    clear: function() {
        try {
            localStorage.clear();
            return true;
        } catch (e) {
            console.error('Error limpiando localStorage:', e);
            return false;
        }
    },
    
    // Guardar preferencias del usuario
    guardarPreferencias: function(prefs) {
        const actuales = this.get('preferencias', {});
        this.set('preferencias', { ...actuales, ...prefs });
    },
    
    // Obtener preferencias del usuario
    obtenerPreferencias: function() {
        return this.get('preferencias', {});
    }
};

// ============================================
// MANEJO DE TEORÍA INTERACTIVA
// ============================================
window.teoria = {
    expandirSeccion: function(id) {
        const seccion = document.getElementById(id);
        if (seccion) {
            seccion.classList.toggle('expandida');
        }
    },
    
    mostrarEjemplo: function(id) {
        const ejemplo = document.getElementById(`ejemplo-${id}`);
        if (ejemplo) {
            ejemplo.classList.add('mostrar');
        }
    },
    
    filtrarPorTipo: function(tipo) {
        document.querySelectorAll('.teoria-card').forEach(card => {
            if (tipo === 'todos' || card.dataset.tipo === tipo) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
};

// ============================================
// MANEJO DE ERRORES
// ============================================
window.addEventListener('error', function(e) {
    console.error('Error global:', e.error);
    if (window.notificaciones) {
        window.notificaciones.error('Ha ocurrido un error. Por favor, recarga la página.');
    }
});

// ============================================
// FUNCIONES PARA PWA (PROGRESSIVE WEB APP)
// ============================================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').then(registration => {
            console.log('ServiceWorker registrado:', registration.scope);
        }).catch(error => {
            console.log('Error registrando ServiceWorker:', error);
        });
    });
}

// ============================================
// MODO OFFLINE
// ============================================
window.addEventListener('online', function() {
    document.body.classList.remove('offline');
    window.notificaciones?.exito('¡Conexión restablecida!');
    sincronizarDatosOffline();
});

window.addEventListener('offline', function() {
    document.body.classList.add('offline');
    window.notificaciones?.advertencia('Modo offline activado');
});

function sincronizarDatosOffline() {
    const datosOffline = storage.get('offlineQueue', []);
    if (datosOffline.length > 0) {
        datosOffline.forEach(async dato => {
            try {
                await api.post(dato.endpoint, dato.data);
            } catch (e) {
                console.error('Error sincronizando:', e);
            }
        });
        storage.remove('offlineQueue');
    }
}

// ============================================
// ANALÍTICAS Y SEGUIMIENTO
// ============================================
window.analytics = {
    trackEvent: function(categoria, accion, etiqueta = null) {
        if (typeof gtag !== 'undefined') {
            gtag('event', accion, {
                'event_category': categoria,
                'event_label': etiqueta
            });
        }
        
        // Guardar para análisis interno
        const eventos = storage.get('analytics', []);
        eventos.push({
            categoria,
            accion,
            etiqueta,
            timestamp: new Date().toISOString()
        });
        storage.set('analytics', eventos.slice(-100)); // Mantener últimos 100
    },
    
    trackPageView: function(pagina) {
        this.trackEvent('navegacion', 'page_view', pagina);
    }
};

// ============================================
// EXPORTAR FUNCIONES PARA USO GLOBAL
// ============================================
window.$utils = window.utils;
window.$api = window.api;
window.$storage = window.storage;
window.$notificaciones = window.notificaciones;
window.$analytics = window.analytics;

// ============================================
// INICIALIZACIÓN DE PREFERENCIAS DE ACCESIBILIDAD
// ============================================
function inicializarAccesibilidad() {
    const preferencias = storage.obtenerPreferencias();
    
    if (preferencias.altoContraste) {
        document.body.classList.add('alto-contraste');
    }
    
    if (preferencias.fuenteGrande) {
        document.body.classList.add('fuente-grande');
    }
    
    if (preferencias.reducirAnimaciones) {
        document.body.classList.add('reducir-animaciones');
    }
}

// ============================================
// ATALAJOS DE TECLADO
// ============================================
document.addEventListener('keydown', function(e) {
    // Ctrl + / para mostrar ayuda
    if (e.ctrlKey && e.key === '/') {
        e.preventDefault();
        mostrarAyudaTeclado();
    }
    
    // Ctrl + S para guardar (en formularios)
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const formulario = document.querySelector('form:not([data-no-save])');
        if (formulario) {
            formulario.dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape para cerrar todo
    if (e.key === 'Escape') {
        cerrarTodosLosModales();
    }
});

function mostrarAyudaTeclado() {
    const ayuda = `
        <div class="atajos-teclado">
            <h5>Atajos de teclado</h5>
            <ul>
                <li><kbd>Ctrl</kbd> + <kbd>/</kbd> - Mostrar ayuda</li>
                <li><kbd>Ctrl</kbd> + <kbd>S</kbd> - Guardar formulario</li>
                <li><kbd>Esc</kbd> - Cerrar ventanas</li>
                <li><kbd>?</kbd> - Mostrar ayuda contextual</li>
            </ul>
        </div>
    `;
    
    window.notificaciones.info(ayuda, 10000);
}

function cerrarTodosLosModales() {
    document.querySelectorAll('.modal.show').forEach(modal => {
        bootstrap.Modal.getInstance(modal).hide();
    });
    
    document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        menu.classList.remove('show');
    });
}

// ============================================
// SISTEMA DE BÚSQUEDA GLOBAL
// ============================================
window.busquedaGlobal = {
    init: function() {
        const input = document.getElementById('busquedaGlobal');
        if (!input) return;
        
        input.addEventListener('input', utils.debounce(() => {
            this.buscar(input.value);
        }, 500));
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.buscar(input.value);
            }
        });
    },
    
    buscar: async function(termino) {
        if (termino.length < 3) return;
        
        try {
            const resultados = await api.get(`/api/buscar?q=${encodeURIComponent(termino)}`);
            this.mostrarResultados(resultados);
        } catch (error) {
            console.error('Error en búsqueda:', error);
        }
    },
    
    mostrarResultados: function(resultados) {
        // Implementar según necesidades
        console.log('Resultados:', resultados);
    }
};

// Inicializar búsqueda global si existe
setTimeout(() => busquedaGlobal.init(), 1000);
