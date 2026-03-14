/* ============================================
   main.js - JavaScript principal para
   Aplicación de Incisos Explicativos
   Integración con Bootstrap 5
   ============================================ */

// ============================================
// SISTEMA DE NOTIFICACIONES MEJORADO
// ============================================
const Notificaciones = {
    /**
     * Muestra una notificación toast personalizada
     * @param {string} mensaje - Mensaje a mostrar
     * @param {string} tipo - success, error, warning, info
     * @param {number} duracion - Duración en ms
     */
    mostrar: function(mensaje, tipo = 'success', duracion = 4000) {
        // Configurar icono y color según tipo
        const config = {
            success: { icono: 'bi-check-circle-fill', bg: 'success', titulo: 'Éxito' },
            error: { icono: 'bi-exclamation-triangle-fill', bg: 'danger', titulo: 'Error' },
            warning: { icono: 'bi-exclamation-circle-fill', bg: 'warning', titulo: 'Advertencia' },
            info: { icono: 'bi-info-circle-fill', bg: 'info', titulo: 'Información' }
        };
        
        const cfg = config[tipo] || config.info;
        
        // Crear toast con HTML mejorado
        const toastId = 'toast-' + Date.now();
        const toast = $(`
            <div id="${toastId}" class="toast align-items-center text-white bg-${cfg.bg} border-0" 
                 role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="${duracion}">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi ${cfg.icono} me-2"></i>
                        <strong>${cfg.titulo}:</strong> ${mensaje}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                            data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `);
        
        // Añadir al contenedor
        $('#toast-container').append(toast);
        
        // Inicializar y mostrar toast con Bootstrap
        const bsToast = new bootstrap.Toast(toast[0], { 
            autohide: true, 
            delay: duracion,
            animation: true
        });
        
        bsToast.show();
        
        // Eliminar del DOM después de ocultarse
        toast.on('hidden.bs.toast', function() {
            $(this).remove();
        });
        
        // Animación de entrada
        toast.hide().fadeIn(300);
    },
    
    // Métodos shorthand
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
    },
    
    // Notificación con confeti (para logros)
    logro: function(mensaje) {
        this.mostrar('🎉 ' + mensaje, 'success', 6000);
        this.lanzarConfeti();
    },
    
    // Efecto de confeti para logros importantes
    lanzarConfeti: function() {
        if (typeof confetti !== 'undefined') {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }
    }
};

// ============================================
// SISTEMA DE LOGROS Y MEDALLAS
// ============================================
const Logros = {
    /**
     * Muestra un modal con el logro desbloqueado
     * @param {Array|string} logros - Lista de logros desbloqueados
     */
    mostrarDesbloqueo: function(logros) {
        if (!logros || logros.length === 0) return;
        
        // Convertir a array si es string
        const listaLogros = Array.isArray(logros) ? logros : [logros];
        
        listaLogros.forEach((logro, index) => {
            setTimeout(() => {
                const modalId = 'logroModal-' + Date.now() + '-' + index;
                const modal = $(`
                    <div class="modal fade" id="${modalId}" tabindex="-1" data-bs-backdrop="static">
                        <div class="modal-dialog modal-dialog-centered modal-lg">
                            <div class="modal-content bg-warning text-dark">
                                <div class="modal-header border-0">
                                    <h5 class="modal-title">
                                        <i class="bi bi-trophy-fill me-2"></i>
                                        ¡Nuevo Logro Desbloqueado!
                                    </h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body text-center py-4">
                                    <div class="display-1 mb-3">🏆</div>
                                    <h2 class="mb-3">${logro}</h2>
                                    <p class="lead">¡Felicidades! Has alcanzado un nuevo hito en tu aprendizaje.</p>
                                    <div class="mt-4">
                                        <span class="badge bg-success fs-6 p-3">
                                            <i class="bi bi-star-fill me-2"></i>
                                            +50 puntos extra
                                        </span>
                                    </div>
                                </div>
                                <div class="modal-footer border-0 justify-content-center">
                                    <button type="button" class="btn btn-primary" data-bs-dismiss="modal">
                                        <i class="bi bi-check-circle me-2"></i>
                                        ¡Genial!
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
                
                $('body').append(modal);
                
                // Inicializar y mostrar modal con Bootstrap
                const bsModal = new bootstrap.Modal(modal[0], {
                    keyboard: true,
                    focus: true,
                    backdrop: 'static'
                });
                
                bsModal.show();
                
                // Lanzar confeti
                Notificaciones.lanzarConfeti();
                
                // Eliminar del DOM después de cerrar
                modal.on('hidden.bs.modal', function() {
                    $(this).remove();
                });
                
                // Auto-cerrar después de 5 segundos
                setTimeout(() => {
                    if (bsModal) {
                        bsModal.hide();
                    }
                }, 5000);
                
            }, index * 800); // Delay entre modales
        });
    },
    
    /**
     * Actualiza la visualización de medallas en el dashboard
     * @param {Array} medallas - Lista de medallas del usuario
     */
    actualizarMedallas: function(medallas) {
        $('.medalla').each(function() {
            const medallaTipo = $(this).data('medalla');
            if (medallas && medallas.includes(medallaTipo)) {
                $(this).addClass('obtenida');
                $(this).attr('title', '¡Medalla obtenida!');
            } else {
                $(this).removeClass('obtenida');
            }
        });
    }
};

// ============================================
// SISTEMA DE PUNTOS Y ANIMACIONES
// ============================================
const Puntos = {
    /**
     * Anima la ganancia de puntos
     * @param {number} puntos - Cantidad de puntos ganados
     * @param {string} elemento - Selector del elemento contenedor
     */
    animar: function(puntos, elemento = 'body') {
        const span = $(`<span class="puntos-animacion">+${puntos} pts</span>`);
        $(elemento).append(span);
        
        // Posición aleatoria cerca del elemento
        const offset = $(elemento).offset();
        if (offset) {
            span.css({
                position: 'absolute',
                left: offset.left + Math.random() * 100,
                top: offset.top - 20,
                color: '#28a745',
                fontWeight: 'bold',
                fontSize: '24px',
                textShadow: '2px 2px 4px rgba(0,0,0,0.2)',
                zIndex: 1000,
                animation: 'floatUp 1.5s ease forwards'
            });
        }
        
        setTimeout(() => span.remove(), 1500);
    },
    
    /**
     * Actualiza el contador de puntos en la UI
     * @param {number} nuevosPuntos - Total de puntos actualizado
     */
    actualizarContador: function(nuevosPuntos) {
        $('.puntos-usuario').each(function() {
            const actual = parseInt($(this).text()) || 0;
            this.contadorAnimado(actual, nuevosPuntos, 1000);
        });
    }
};

// ============================================
// GESTIÓN DEL ESTADO DEL USUARIO
// ============================================
const UserState = {
    datos: null,
    cache: null,
    
    /**
     * Carga los datos del usuario desde el servidor
     * @returns {Promise} Promesa con los datos del usuario
     */
    cargar: async function() {
        try {
            const response = await $.get('/api/estadisticas');
            this.datos = response;
            this.cache = response;
            this.actualizarUI();
            return response;
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
            return null;
        }
    },
    
    /**
     * Actualiza todos los elementos de la UI con los datos del usuario
     */
    actualizarUI: function() {
        if (!this.datos) return;
        
        // Actualizar puntos y estrellas
        $('.puntos-usuario').text(this.datos.puntos || 0);
        
        // Actualizar estrellas
        $('.estrellas-usuario').each(function() {
            const estrellas = this.datos?.estrellas || 0;
            $(this).html('⭐'.repeat(estrellas));
        });
        
        // Actualizar rachas
        if (this.datos.rachas) {
            $('.rachas-usuario').text(this.datos.rachas.actual || 0);
            $('.racha-maxima').text(this.datos.rachas.maxima || 0);
        }
        
        // Actualizar medallas
        if (this.datos.medallas) {
            Logros.actualizarMedallas(this.datos.medallas);
        }
        
        // Actualizar progreso por categoría
        if (this.datos.por_categoria) {
            this.actualizarProgresoCategorias();
        }
    },
    
    /**
     * Actualiza las barras de progreso por categoría
     */
    actualizarProgresoCategorias: function() {
        const categorias = this.datos.por_categoria;
        
        Object.keys(categorias).forEach(cat => {
            const datos = categorias[cat];
            const porcentaje = datos.intentos > 0 
                ? Math.round((datos.correctos / datos.intentos) * 100) 
                : 0;
            
            $(`#progreso-${cat}`).css('width', porcentaje + '%').text(porcentaje + '%');
            $(`#texto-${cat}`).text(`${datos.correctos}/${datos.intentos} (${porcentaje}%)`);
        });
    },
    
    /**
     * Actualiza los datos del usuario después de una acción
     * @param {Object} nuevosDatos - Datos actualizados
     */
    actualizar: function(nuevosDatos) {
        this.datos = { ...this.datos, ...nuevosDatos };
        this.actualizarUI();
    }
};

// ============================================
// UTILIDADES GENERALES
// ============================================
const Utils = {
    /**
     * Valida una dirección de email
     * @param {string} email - Email a validar
     * @returns {boolean} true si es válido
     */
    validarEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    /**
     * Formatea una fecha
     * @param {string|Date} fecha - Fecha a formatear
     * @returns {string} Fecha formateada
     */
    formatearFecha: function(fecha) {
        const d = new Date(fecha);
        return d.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    /**
     * Trunca un texto a una longitud máxima
     * @param {string} texto - Texto a truncar
     * @param {number} longitud - Longitud máxima
     * @returns {string} Texto truncado
     */
    truncarTexto: function(texto, longitud = 50) {
        if (texto.length <= longitud) return texto;
        return texto.substring(0, longitud) + '...';
    },
    
    /**
     * Genera un ID único
     * @returns {string} ID único
     */
    generarId: function() {
        return Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    },
    
    /**
     * Debounce para funciones de búsqueda
     * @param {Function} func - Función a ejecutar
     * @param {number} wait - Tiempo de espera
     * @returns {Function} Función con debounce
     */
    debounce: function(func, wait = 300) {
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
// GESTIÓN DE FORMULARIOS CON AJAX
// ============================================
const FormHandler = {
    /**
     * Inicializa todos los formularios con data-ajax
     */
    init: function() {
        $('form[data-ajax]').off('submit').on('submit', this.handleSubmit);
    },
    
    /**
     * Maneja el envío de formularios vía AJAX
     * @param {Event} e - Evento de submit
     */
    handleSubmit: async function(e) {
        e.preventDefault();
        
        const form = $(this);
        const url = form.attr('action');
        const method = form.attr('method') || 'POST';
        const submitBtn = form.find('[type="submit"]');
        const originalText = submitBtn.html();
        
        // Deshabilitar botón y mostrar loading
        submitBtn.prop('disabled', true)
                 .html('<span class="spinner-border spinner-border-sm me-2"></span>Procesando...');
        
        try {
            const response = await $.ajax({
                url: url,
                method: method,
                data: form.serialize(),
                dataType: 'json'
            });
            
            if (response.success) {
                Notificaciones.exito(response.mensaje || 'Operación exitosa');
                
                // Resetear formulario
                form[0].reset();
                
                // Redireccionar si es necesario
                if (response.redirect) {
                    setTimeout(() => {
                        window.location.href = response.redirect;
                    }, 1500);
                }
                
                // Actualizar estado del usuario
                if (response.estadisticas) {
                    UserState.actualizar(response.estadisticas);
                }
                
                // Mostrar nuevos logros
                if (response.nuevos_logros) {
                    Logros.mostrarDesbloqueo(response.nuevos_logros);
                }
                
                // Animar puntos ganados
                if (response.puntos_ganados) {
                    Puntos.animar(response.puntos_ganados, form);
                }
                
            } else {
                Notificaciones.error(response.mensaje || 'Error en la operación');
            }
            
        } catch (error) {
            console.error('Error AJAX:', error);
            Notificaciones.error('Error de conexión. Intenta nuevamente.');
            
        } finally {
            // Restaurar botón
            submitBtn.prop('disabled', false).html(originalText);
        }
    }
};

// ============================================
// ANIMACIONES Y EFECTOS
// ============================================
const Animaciones = {
    /**
     * Inicializa todas las animaciones
     */
    init: function() {
        this.initHoverEffects();
        this.initScrollAnimations();
        this.initCounterAnimations();
        this.initTooltips();
        this.initPopovers();
    },
    
    /**
     * Inicializa efectos hover en tarjetas
     */
    initHoverEffects: function() {
        $('.card').hover(
            function() { 
                $(this).addClass('shadow-lg').css('transform', 'translateY(-5px)'); 
            },
            function() { 
                $(this).removeClass('shadow-lg').css('transform', 'translateY(0)'); 
            }
        );
        
        // Efecto pulse en botones al hacer click
        $('.btn').on('click', function() {
            $(this).addClass('pulse');
            setTimeout(() => $(this).removeClass('pulse'), 300);
        });
    },
    
    /**
     * Inicializa animaciones al hacer scroll
     */
    initScrollAnimations: function() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    $(entry.target).addClass('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        $('.fade-in-on-scroll').each(function() {
            observer.observe(this);
        });
    },
    
    /**
     * Inicializa animaciones de contadores
     */
    initCounterAnimations: function() {
        $('.counter').each(function() {
            const $this = $(this);
            const target = parseInt($this.text());
            
            $this.prop('Counter', 0).animate({
                Counter: target
            }, {
                duration: 2000,
                easing: 'swing',
                step: function(now) {
                    $this.text(Math.ceil(now));
                }
            });
        });
    },
    
    /**
     * Inicializa tooltips de Bootstrap
     */
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                animation: true,
                delay: { show: 500, hide: 100 }
            });
        });
    },
    
    /**
     * Inicializa popovers de Bootstrap
     */
    initPopovers: function() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl, {
                animation: true,
                trigger: 'hover'
            });
        });
    }
};

// ============================================
// GESTIÓN DE TEMA (CLARO/OSCURO)
// ============================================
const ThemeManager = {
    temaActual: localStorage.getItem('theme') || 'light',
    
    init: function() {
        this.aplicarTema(this.temaActual);
        this.initThemeToggle();
    },
    
    aplicarTema: function(tema) {
        if (tema === 'dark') {
            $('body').addClass('dark-theme');
            $('#theme-icon').removeClass('bi-moon-fill').addClass('bi-sun-fill');
        } else {
            $('body').removeClass('dark-theme');
            $('#theme-icon').removeClass('bi-sun-fill').addClass('bi-moon-fill');
        }
        
        localStorage.setItem('theme', tema);
        this.temaActual = tema;
    },
    
    toggleTema: function() {
        const nuevoTema = this.temaActual === 'light' ? 'dark' : 'light';
        this.aplicarTema(nuevoTema);
        Notificaciones.info(`Tema ${nuevoTema === 'light' ? 'claro' : 'oscuro'} activado`);
    },
    
    initThemeToggle: function() {
        $('#theme-toggle').off('click').on('click', () => this.toggleTema());
    }
};

// ============================================
// INICIALIZACIÓN PRINCIPAL
// ============================================
$(document).ready(function() {
    console.log('🚀 Aplicación de Incisos Explicativos iniciada');
    
    // 1. Crear contenedor para toasts si no existe
    if ($('#toast-container').length === 0) {
        $('body').append(`
            <div id="toast-container" class="position-fixed bottom-0 end-0 p-3" 
                 style="z-index: 9999; max-width: 400px;"></div>
        `);
    }
    
    // 2. Crear botón de cambio de tema si no existe
    if ($('#theme-toggle').length === 0 && !$('.navbar').length === 0) {
        $('.navbar .navbar-nav').append(`
            <li class="nav-item">
                <a class="nav-link" href="#" id="theme-toggle" title="Cambiar tema">
                    <i class="bi ${ThemeManager.temaActual === 'light' ? 'bi-moon-fill' : 'bi-sun-fill'}" id="theme-icon"></i>
                </a>
            </li>
        `);
    }
    
    // 3. Inicializar módulos
    FormHandler.init();
    Animaciones.init();
    ThemeManager.init();
    
    // 4. Cargar estado del usuario
    UserState.cargar().then(() => {
        console.log('✅ Datos de usuario cargados');
    });
    
    // 5. Detectar cambios en la conexión
    window.addEventListener('online', () => {
        Notificaciones.exito('¡Conexión restaurada!');
    });
    
    window.addEventListener('offline', () => {
        Notificaciones.error('Sin conexión. Algunas funciones pueden no estar disponibles.');
    });
    
    // 6. Prevenir envío de formularios vacíos
    $('form').on('submit', function(e) {
        const requiredFields = $(this).find('[required]');
        let isValid = true;
        
        requiredFields.each(function() {
            if (!$(this).val()) {
                isValid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            Notificaciones.error('Por favor, completa todos los campos requeridos');
        }
    });
    
    // 7. Auto-guardado en formularios largos (opcional)
    let autoSaveTimer;
    $('form input, form textarea').on('input', Utils.debounce(function() {
        const formData = $(this).closest('form').serialize();
        localStorage.setItem('formAutoSave', formData);
        Notificaciones.info('Borrador guardado automáticamente', 2000);
    }, 1000));
    
    // 8. Precarga de imágenes para mejorar rendimiento
    const imagenes = [
        'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="%234e73df"/></svg>'
    ];
    
    imagenes.forEach(src => {
        const img = new Image();
        img.src = src;
    });
    
    console.log('✅ Inicialización completada');
});

// ============================================
// POLYFILLS PARA COMPATIBILIDAD
// ============================================

// Intersection Observer polyfill para navegadores antiguos
if (window.IntersectionObserver === undefined) {
    window.IntersectionObserver = class {
        constructor(callback) {
            this.callback = callback;
        }
        observe(element) {
            // Simular que todos los elementos son visibles
            this.callback([{ isIntersecting: true, target: element }]);
        }
        unobserve() {}
    };
}

// ============================================
// EXTENSIONES DE JQUERY
// ============================================

// Plugin jQuery para animación de contadores
$.fn.contadorAnimado = function(from, to, duration) {
    return this.each(function() {
        let current = from;
        const increment = (to - from) / (duration / 20);
        const $this = $(this);
        
        const timer = setInterval(() => {
            current += increment;
            $this.text(Math.round(current));
            
            if ((increment > 0 && current >= to) || (increment < 0 && current <= to)) {
                $this.text(to);
                clearInterval(timer);
            }
        }, 20);
    });
};

// Plugin jQuery para fadeIn con dirección
$.fn.fadeInDirection = function(direction = 'up', duration = 400) {
    const directions = {
        up: { start: { opacity: 0, transform: 'translateY(20px)' } },
        down: { start: { opacity: 0, transform: 'translateY(-20px)' } },
        left: { start: { opacity: 0, transform: 'translateX(20px)' } },
        right: { start: { opacity: 0, transform: 'translateX(-20px)' } }
    };
    
    const anim = directions[direction] || directions.up;
    
    return this.each(function() {
        $(this).css(anim.start)
               .animate({ opacity: 1, transform: 'translate(0)' }, duration);
    });
};

// ============================================
// MANEJADORES DE ERRORES GLOBALES
// ============================================

window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('Error global:', { msg, url, lineNo, columnNo, error });
    
    // Enviar error al servidor en producción (opcional)
    if (window.location.hostname !== 'localhost') {
        $.post('/api/log-error', {
            mensaje: msg,
            url: url,
            linea: lineNo,
            columna: columnNo,
            stack: error?.stack
        });
    }
    
    return false;
};

// Manejar promesas no capturadas
window.addEventListener('unhandledrejection', function(event) {
    console.error('Promesa no manejada:', event.reason);
    Notificaciones.error('Ocurrió un error inesperado');
});

// ============================================
// EXPORTAR MÓDULOS PARA USO GLOBAL
// ============================================
window.App = {
    Notificaciones,
    Logros,
    Puntos,
    UserState,
    Utils,
    FormHandler,
    Animaciones,
    ThemeManager
};

// Alias para facilitar el acceso
window.$app = window.App;
