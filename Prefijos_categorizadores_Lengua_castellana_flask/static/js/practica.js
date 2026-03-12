/* ============================================
   SISTEMA DE PRÁCTICA - ECOSISTEMA MORFOLOGÍA
   ============================================ */

class SistemaPractica {
    constructor() {
        this.ejercicios = [];
        this.ejerciciosOriginales = [];
        this.indiceActual = 0;
        this.respuestas = [];
        this.puntos = 0;
        this.racha = 0;
        this.nivel = 1;
        this.modo = 'normal'; // 'normal', 'rapida', 'completa', 'desafio'
        this.estadisticas = {
            totalEjercicios: 0,
            correctas: 0,
            incorrectas: 0,
            tiempoTotal: 0,
            precision: 0,
            rachaMaxima: 0
        };
        this.tiempoInicio = null;
        this.tiempoEjercicio = null;
        this.categoriaActual = 'todos';
        this.dificultadActual = 0;
        this.estrellasObtenidas = 0;
        this.combos = {
            actual: 0,
            maximo: 0,
            multiplicador: 1
        };
        
        this.inicializar();
    }
    
    async inicializar() {
        try {
            await this.cargarEjercicios();
            this.cargarProgreso();
            this.crearInterfaz();
            this.configurarEventos();
            this.actualizarEstadisticas();
            this.mostrarEjercicio();
        } catch (error) {
            console.error('Error inicializando práctica:', error);
            window.notificaciones?.error('Error al cargar los ejercicios');
        }
    }
    
    async cargarEjercicios() {
        try {
            const response = await fetch('/static/data/ejercicios.json');
            const data = await response.json();
            
            this.ejerciciosOriginales = data.ejercicios.map(ej => ({
                ...ej,
                veces_practicado: 0,
                veces_acertado: 0,
                ultimo_intento: null,
                tiempo_promedio: 0,
                dificultad_percibida: ej.dificultad
            }));
            
            this.ejercicios = [...this.ejerciciosOriginales];
            this.estadisticas.totalEjercicios = this.ejercicios.length;
        } catch (error) {
            console.error('Error cargando ejercicios:', error);
            throw error;
        }
    }
    
    cargarProgreso() {
        const progreso = window.storage?.get('practica_progreso');
        if (progreso) {
            this.puntos = progreso.puntos || 0;
            this.racha = progreso.racha || 0;
            this.nivel = progreso.nivel || 1;
            this.estadisticas = progreso.estadisticas || this.estadisticas;
            this.combos = progreso.combos || this.combos;
            
            // Restaurar estado de ejercicios
            if (progreso.ejercicios) {
                this.ejercicios.forEach(ej => {
                    const guardado = progreso.ejercicios.find(e => e.id === ej.id);
                    if (guardado) {
                        Object.assign(ej, guardado);
                    }
                });
            }
        }
    }
    
    guardarProgreso() {
        window.storage?.set('practica_progreso', {
            puntos: this.puntos,
            racha: this.racha,
            nivel: this.nivel,
            estadisticas: this.estadisticas,
            combos: this.combos,
            ejercicios: this.ejercicios.map(ej => ({
                id: ej.id,
                veces_practicado: ej.veces_practicado,
                veces_acertado: ej.veces_acertado,
                ultimo_intento: ej.ultimo_intento,
                tiempo_promedio: ej.tiempo_promedio
            }))
        });
    }
    
    crearInterfaz() {
        const container = document.getElementById('practica-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="practica-sistema">
                <!-- Barra de progreso y estadísticas -->
                <div class="stats-bar mb-4">
                    <div class="row g-3">
                        <div class="col-md-3">
                            <div class="stat-card text-center p-3 bg-primary bg-opacity-10 rounded">
                                <i class="bi bi-trophy-fill text-primary fs-4"></i>
                                <h5 class="mt-2 mb-0">${this.puntos}</h5>
                                <small class="text-muted">Puntos</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card text-center p-3 bg-success bg-opacity-10 rounded">
                                <i class="bi bi-fire text-success fs-4"></i>
                                <h5 class="mt-2 mb-0">${this.racha}</h5>
                                <small class="text-muted">Racha</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card text-center p-3 bg-warning bg-opacity-10 rounded">
                                <i class="bi bi-star-fill text-warning fs-4"></i>
                                <h5 class="mt-2 mb-0">${this.nivel}</h5>
                                <small class="text-muted">Nivel</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card text-center p-3 bg-info bg-opacity-10 rounded">
                                <i class="bi bi-graph-up text-info fs-4"></i>
                                <h5 class="mt-2 mb-0">${this.calcularPrecision()}%</h5>
                                <small class="text-muted">Precisión</small>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Barra de progreso del nivel -->
                    <div class="progress mt-3" style="height: 10px;">
                        <div class="progress-bar bg-success" 
                             id="progresoNivel" 
                             style="width: ${this.calcularProgresoNivel()}%">
                        </div>
                    </div>
                </div>
                
                <!-- Controles de filtro -->
                <div class="filtros-bar mb-4">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <select class="form-select" id="filtroCategoria">
                                <option value="todos">Todas las categorías</option>
                                <option value="cuantitativo">Cuantitativos</option>
                                <option value="negación">Negación</option>
                                <option value="posición">Posición</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <select class="form-select" id="filtroDificultad">
                                <option value="0">Todas las dificultades</option>
                                <option value="1">★ Básico</option>
                                <option value="2">★★ Intermedio</option>
                                <option value="3">★★★ Avanzado</option>
                                <option value="4">★★★★ Experto</option>
                                <option value="5">★★★★★ Maestro</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <select class="form-select" id="modoPractica">
                                <option value="normal">Modo Normal</option>
                                <option value="rapida">Práctica Rápida (10 ejercicios)</option>
                                <option value="completa">Práctica Completa (100 ejercicios)</option>
                                <option value="desafio">Modo Desafío</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Área del ejercicio actual -->
                <div class="ejercicio-card card mb-4">
                    <div class="card-body p-4">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <h5 class="mb-0">
                                <span class="badge bg-primary me-2">Ejercicio ${this.indiceActual + 1}</span>
                                <span class="badge bg-info">${this.ejercicios[this.indiceActual]?.tipo_prefijo || ''}</span>
                            </h5>
                            <div class="combo-indicator">
                                <span class="badge bg-warning text-dark">
                                    <i class="bi bi-lightning-charge-fill me-1"></i>
                                    Combo x${this.combos.multiplicador}
                                </span>
                            </div>
                        </div>
                        
                        <div id="ejercicio-contenido" class="text-center mb-4">
                            <!-- Se carga dinámicamente -->
                        </div>
                        
                        <div class="respuesta-area">
                            <div class="row justify-content-center">
                                <div class="col-md-8">
                                    <div class="input-group">
                                        <input type="text" class="form-control form-control-lg" 
                                               id="respuestaInput" 
                                               placeholder="Escribe la palabra completa..."
                                               autocomplete="off">
                                        <button class="btn btn-primary btn-lg" id="btnVerificar">
                                            <i class="bi bi-check-circle me-2"></i>Verificar
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div id="feedback" class="mt-3 text-center"></div>
                    </div>
                </div>
                
                <!-- Sistema de estrellas -->
                <div class="estrellas-container text-center mb-4">
                    <div class="estrellas" id="estrellas">
                        ${this.generarEstrellas()}
                    </div>
                    <p class="text-muted small mt-2">
                        <i class="bi bi-info-circle me-1"></i>
                        3 estrellas = 100% precisión en los últimos 10 ejercicios
                    </p>
                </div>
                
                <!-- Historial de respuestas -->
                <div class="historial-card card">
                    <div class="card-header bg-transparent">
                        <h6 class="mb-0">
                            <i class="bi bi-clock-history me-2"></i>
                            Últimas respuestas
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="historial-lista" id="historialLista">
                            ${this.generarHistorial()}
                        </div>
                    </div>
                </div>
                
                <!-- Botones de acción adicionales -->
                <div class="acciones-bar mt-4 text-center">
                    <button class="btn btn-outline-primary me-2" onclick="practica.mostrarPista()">
                        <i class="bi bi-lightbulb me-2"></i>Pista
                    </button>
                    <button class="btn btn-outline-success me-2" onclick="practica.saltarEjercicio()">
                        <i class="bi bi-skip-forward me-2"></i>Saltar
                    </button>
                    <button class="btn btn-outline-info" onclick="practica.mostrarEstadisticasDetalladas()">
                        <i class="bi bi-bar-chart me-2"></i>Estadísticas
                    </button>
                </div>
            </div>
        `;
    }
    
    configurarEventos() {
        document.getElementById('filtroCategoria')?.addEventListener('change', (e) => {
            this.filtrarCategoria(e.target.value);
        });
        
        document.getElementById('filtroDificultad')?.addEventListener('change', (e) => {
            this.filtrarDificultad(parseInt(e.target.value));
        });
        
        document.getElementById('modoPractica')?.addEventListener('change', (e) => {
            this.cambiarModo(e.target.value);
        });
        
        document.getElementById('btnVerificar')?.addEventListener('click', () => {
            this.verificarRespuesta();
        });
        
        document.getElementById('respuestaInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.verificarRespuesta();
            }
        });
        
        // Autocompletar inteligente
        document.getElementById('respuestaInput')?.addEventListener('input', (e) => {
            this.sugerirAutocompletado(e.target.value);
        });
    }
    
    mostrarEjercicio() {
        if (this.ejercicios.length === 0) {
            document.getElementById('ejercicio-contenido').innerHTML = `
                <div class="text-center p-5">
                    <i class="bi bi-emoji-smile display-1 text-success"></i>
                    <h3 class="mt-3">¡Completaste todos los ejercicios!</h3>
                    <p class="text-muted">¿Quieres reiniciar o probar otro modo?</p>
                    <button class="btn btn-primary mt-3" onclick="practica.reiniciar()">
                        <i class="bi bi-arrow-repeat me-2"></i>Practicar de nuevo
                    </button>
                </div>
            `;
            return;
        }
        
        const ejercicio = this.ejercicios[this.indiceActual];
        this.tiempoEjercicio = Date.now();
        
        const palabraOculta = this.ocultarLetras(ejercicio.palabra);
        
        document.getElementById('ejercicio-contenido').innerHTML = `
            <h2 class="display-1 mb-4">${palabraOculta}</h2>
            <p class="lead">${ejercicio.ejemplo.replace('{palabra}', '______')}</p>
            <div class="mt-3">
                <span class="badge bg-secondary me-2">Base: ${ejercicio.base}</span>
                <span class="badge bg-info">Dificultad: ${'★'.repeat(ejercicio.dificultad)}</span>
            </div>
        `;
        
        document.getElementById('respuestaInput').value = '';
        document.getElementById('respuestaInput').focus();
        document.getElementById('feedback').innerHTML = '';
    }
    
    ocultarLetras(palabra) {
        const porcentajeOcultar = 20 + (this.nivel * 5);
        const letras = palabra.split('');
        const indices = [];
        
        while (indices.length < Math.floor(letras.length * porcentajeOcultar / 100)) {
            const idx = Math.floor(Math.random() * letras.length);
            if (!indices.includes(idx) && letras[idx] !== ' ') {
                indices.push(idx);
            }
        }
        
        return letras.map((l, i) => indices.includes(i) ? '_' : l).join('');
    }
    
    async verificarRespuesta() {
        const respuesta = document.getElementById('respuestaInput').value.toLowerCase().trim();
        const ejercicio = this.ejercicios[this.indiceActual];
        
        if (!respuesta) {
            window.notificaciones?.advertencia('Escribe una respuesta');
            return;
        }
        
        const tiempoRespuesta = (Date.now() - this.tiempoEjercicio) / 1000;
        const correcto = respuesta === ejercicio.palabra.toLowerCase();
        
        // Actualizar estadísticas del ejercicio
        ejercicio.veces_practicado++;
        ejercicio.ultimo_intento = new Date();
        ejercicio.tiempo_promedio = (ejercicio.tiempo_promedio * (ejercicio.veces_practicado - 1) + tiempoRespuesta) / ejercicio.veces_practicado;
        
        if (correcto) {
            await this.manejarAcierto(ejercicio);
        } else {
            await this.manejarError(ejercicio, respuesta);
        }
        
        this.actualizarEstadisticas();
        this.guardarHistorial(ejercicio, correcto);
        this.guardarProgreso();
        
        setTimeout(() => {
            this.siguienteEjercicio();
        }, 1500);
    }
    
    async manejarAcierto(ejercicio) {
        ejercicio.veces_acertado++;
        
        // Calcular puntos base
        let puntosGanados = 10 * this.combos.multiplicador;
        
        // Bonificación por tiempo rápido
        if (this.tiempoEjercicio && (Date.now() - this.tiempoEjercicio) < 5000) {
            puntosGanados += 5;
        }
        
        // Bonificación por racha
        this.racha++;
        this.combos.actual++;
        
        if (this.combos.actual > this.combos.maximo) {
            this.combos.maximo = this.combos.actual;
        }
        
        // Actualizar multiplicador de combo
        if (this.combos.actual >= 5) this.combos.multiplicador = 2;
        if (this.combos.actual >= 10) this.combos.multiplicador = 3;
        if (this.combos.actual >= 20) this.combos.multiplicador = 5;
        
        this.puntos += puntosGanados;
        
        // Subir de nivel cada 100 puntos
        this.nivel = Math.floor(this.puntos / 100) + 1;
        
        this.estadisticas.correctas++;
        
        // Mostrar feedback
        document.getElementById('feedback').innerHTML = `
            <div class="alert alert-success">
                <i class="bi bi-check-circle-fill me-2"></i>
                ¡Correcto! +${puntosGanados} puntos
                ${this.combos.multiplicador > 1 ? `<br><small>Combo x${this.combos.multiplicador}!</small>` : ''}
            </div>
        `;
        
        // Animación de celebración
        this.celebrarAcierto();
    }
    
    async manejarError(ejercicio, respuesta) {
        this.racha = 0;
        this.combos.actual = 0;
        this.combos.multiplicador = 1;
        this.estadisticas.incorrectas++;
        
        document.getElementById('feedback').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-x-circle-fill me-2"></i>
                Incorrecto. La respuesta era: <strong>${ejercicio.palabra}</strong>
            </div>
        `;
    }
    
    celebrarAcierto() {
        const estrellas = document.querySelectorAll('.estrella');
        estrellas.forEach((estrella, i) => {
            setTimeout(() => {
                estrella.classList.add('estrella-animada');
                setTimeout(() => estrella.classList.remove('estrella-animada'), 500);
            }, i * 100);
        });
    }
    
    siguienteEjercicio() {
        if (this.modo === 'rapida' && this.indiceActual >= 9) {
            this.finalizarPractica();
            return;
        }
        
        if (this.modo === 'completa' && this.indiceActual >= 99) {
            this.finalizarPractica();
            return;
        }
        
        this.indiceActual = (this.indiceActual + 1) % this.ejercicios.length;
        this.mostrarEjercicio();
    }
    
    saltarEjercicio() {
        if (this.puntos >= 5) {
            this.puntos -= 5;
            this.siguienteEjercicio();
            window.notificaciones?.info('Ejercicio saltado (-5 puntos)');
        } else {
            window.notificaciones?.advertencia('No tienes suficientes puntos');
        }
    }
    
    mostrarPista() {
        if (this.puntos >= 3) {
            const ejercicio = this.ejercicios[this.indiceActual];
            this.puntos -= 3;
            
            const pista = ejercicio.pistas[Math.floor(Math.random() * ejercicio.pistas.length)];
            
            document.getElementById('feedback').innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-lightbulb-fill me-2"></i>
                    Pista: ${pista}
                </div>
            `;
            
            setTimeout(() => {
                document.getElementById('feedback').innerHTML = '';
            }, 3000);
        } else {
            window.notificaciones?.advertencia('Necesitas 3 puntos para una pista');
        }
    }
    
    sugerirAutocompletado(texto) {
        if (texto.length < 2) return;
        
        const ejercicio = this.ejercicios[this.indiceActual];
        const palabra = ejercicio.palabra.toLowerCase();
        
        if (palabra.startsWith(texto.toLowerCase()) && texto.length < palabra.length) {
            // Mostrar sugerencia
            const sugerencia = palabra.substring(texto.length);
            // Implementar visualización de sugerencia
        }
    }
    
    filtrarCategoria(categoria) {
        this.categoriaActual = categoria;
        this.aplicarFiltros();
    }
    
    filtrarDificultad(dificultad) {
        this.dificultadActual = dificultad;
        this.aplicarFiltros();
    }
    
    cambiarModo(modo) {
        this.modo = modo;
        
        if (modo === 'rapida') {
            this.ejercicios = this.ejerciciosOriginales.slice(0, 10);
        } else if (modo === 'completa') {
            this.ejercicios = [...this.ejerciciosOriginales];
        } else if (modo === 'desafio') {
            this.ejercicios = this.ejerciciosOriginales.filter(e => e.dificultad >= 3);
        } else {
            this.aplicarFiltros();
        }
        
        this.indiceActual = 0;
        this.mostrarEjercicio();
    }
    
    aplicarFiltros() {
        this.ejercicios = this.ejerciciosOriginales.filter(ej => {
            if (this.categoriaActual !== 'todos' && ej.tipo_prefijo !== this.categoriaActual) {
                return false;
            }
            if (this.dificultadActual !== 0 && ej.dificultad !== this.dificultadActual) {
                return false;
            }
            return true;
        });
        
        this.indiceActual = 0;
        this.mostrarEjercicio();
    }
    
    calcularPrecision() {
        const total = this.estadisticas.correctas + this.estadisticas.incorrectas;
        if (total === 0) return 0;
        return Math.round((this.estadisticas.correctas / total) * 100);
    }
    
    calcularProgresoNivel() {
        const puntosSiguienteNivel = this.nivel * 100;
        const puntosAnteriorNivel = (this.nivel - 1) * 100;
        const progreso = ((this.puntos - puntosAnteriorNivel) / (puntosSiguienteNivel - puntosAnteriorNivel)) * 100;
        return Math.min(100, Math.max(0, progreso));
    }
    
    generarEstrellas() {
        const precision = this.calcularPrecision();
        let estrellas = '';
        
        for (let i = 1; i <= 3; i++) {
            if (precision >= i * 33) {
                estrellas += '<i class="bi bi-star-fill text-warning estrella"></i>';
            } else {
                estrellas += '<i class="bi bi-star text-secondary estrella"></i>';
            }
        }
        
        return estrellas;
    }
    
    generarHistorial() {
        if (this.respuestas.length === 0) {
            return '<p class="text-muted text-center">No hay respuestas recientes</p>';
        }
        
        return this.respuestas.slice(-5).reverse().map(r => `
            <div class="historial-item d-flex align-items-center mb-2 p-2 bg-light rounded">
                <span class="me-2">${r.correcto ? '✅' : '❌'}</span>
                <span class="flex-grow-1">${r.palabra}</span>
                <small class="text-muted">${window.utils?.formatearFecha(r.fecha) || r.fecha}</small>
            </div>
        `).join('');
    }
    
    guardarHistorial(ejercicio, correcto) {
        this.respuestas.push({
            palabra: ejercicio.palabra,
            correcto: correcto,
            fecha: new Date().toISOString()
        });
        
        if (this.respuestas.length > 10) {
            this.respuestas.shift();
        }
        
        const historialLista = document.getElementById('historialLista');
        if (historialLista) {
            historialLista.innerHTML = this.generarHistorial();
        }
    }
    
    actualizarEstadisticas() {
        // Actualizar elementos de la interfaz
        document.querySelectorAll('.stat-card h5').forEach((el, index) => {
            const valores = [this.puntos, this.racha, this.nivel, this.calcularPrecision()];
            if (el) el.textContent = valores[index];
        });
        
        document.getElementById('progresoNivel').style.width = this.calcularProgresoNivel() + '%';
        document.getElementById('estrellas').innerHTML = this.generarEstrellas();
    }
    
    finalizarPractica() {
        const precision = this.calcularPrecision();
        const estrellasObtenidas = Math.floor(precision / 33) + 1;
        
        document.getElementById('ejercicio-contenido').innerHTML = `
            <div class="text-center p-5">
                <i class="bi bi-trophy-fill display-1 text-warning"></i>
                <h2 class="mt-4">¡Práctica Completada!</h2>
                <div class="mt-4">
                    <p><strong>Ejercicios:</strong> ${this.estadisticas.correctas + this.estadisticas.incorrectas}</p>
                    <p><strong>Correctas:</strong> ${this.estadisticas.correctas}</p>
                    <p><strong>Precisión:</strong> ${precision}%</p>
                    <p><strong>Estrellas:</strong> ${'⭐'.repeat(estrellasObtenidas)}</p>
                    <p><strong>Puntos totales:</strong> ${this.puntos}</p>
                    <p><strong>Racha máxima:</strong> ${this.combos.maximo}</p>
                </div>
                <div class="mt-4">
                    <button class="btn btn-primary me-2" onclick="practica.reiniciar()">
                        <i class="bi bi-arrow-repeat me-2"></i>Practicar de nuevo
                    </button>
                    <button class="btn btn-success" onclick="window.location.href='/dashboard'">
                        <i class="bi bi-house-door me-2"></i>Ir al Dashboard
                    </button>
                </div>
            </div>
        `;
        
        // Guardar logros desbloqueados
        this.verificarLogros();
    }
    
    verificarLogros() {
        const logros = [];
        
        if (this.estadisticas.correctas >= 100) {
            logros.push('maestro_prefijos');
        }
        if (this.combos.maximo >= 20) {
            logros.push('imparable');
        }
        if (this.calcularPrecision() >= 90) {
            logros.push('preciso');
        }
        
        if (logros.length > 0) {
            window.notificaciones?.exito(`¡Logros desbloqueados: ${logros.length}!`);
        }
    }
    
    mostrarEstadisticasDetalladas() {
        const ejerciciosPorCategoria = {};
        this.ejerciciosOriginales.forEach(ej => {
            if (!ejerciciosPorCategoria[ej.tipo_prefijo]) {
                ejerciciosPorCategoria[ej.tipo_prefijo] = {
                    total: 0,
                    acertados: 0
                };
            }
            ejerciciosPorCategoria[ej.tipo_prefijo].total++;
            if (ej.veces_acertado > 0) {
                ejerciciosPorCategoria[ej.tipo_prefijo].acertados++;
            }
        });
        
        const statsHTML = `
            <div class="modal fade" id="modalEstadisticas" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">
                                <i class="bi bi-bar-chart-fill me-2"></i>
                                Estadísticas Detalladas
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <h6>Progreso General</h6>
                            <div class="row g-3 mb-4">
                                <div class="col-md-6">
                                    <div class="bg-light p-3 rounded">
                                        <p class="mb-1">Total ejercicios: ${this.estadisticas.totalEjercicios}</p>
                                        <p class="mb-1">Completados: ${this.estadisticas.correctas + this.estadisticas.incorrectas}</p>
                                        <p class="mb-1">Restantes: ${this.estadisticas.totalEjercicios - (this.estadisticas.correctas + this.estadisticas.incorrectas)}</p>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="bg-light p-3 rounded">
                                        <p class="mb-1">Tiempo total: ${Math.round(this.estadisticas.tiempoTotal)}s</p>
                                        <p class="mb-1">Tiempo promedio: ${(this.estadisticas.tiempoTotal / (this.estadisticas.correctas + this.estadisticas.incorrectas)).toFixed(1)}s</p>
                                    </div>
                                </div>
                            </div>
                            
                            <h6>Rendimiento por Categoría</h6>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Categoría</th>
                                            <th>Total</th>
                                            <th>Acertados</th>
                                            <th>Precisión</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${Object.entries(ejerciciosPorCategoria).map(([cat, datos]) => `
                                            <tr>
                                                <td>${cat}</td>
                                                <td>${datos.total}</td>
                                                <td>${datos.acertados}</td>
                                                <td>${Math.round((datos.acertados / datos.total) * 100)}%</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                            
                            <h6 class="mt-4">Logros</h6>
                            <div class="d-flex flex-wrap gap-2">
                                ${this.combos.maximo >= 20 ? '<span class="badge bg-warning text-dark p-2">🔥 Imparable</span>' : ''}
                                ${this.calcularPrecision() >= 90 ? '<span class="badge bg-success p-2">🎯 Preciso</span>' : ''}
                                ${this.estadisticas.correctas >= 100 ? '<span class="badge bg-primary p-2">👑 Maestro</span>' : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', statsHTML);
        const modal = new bootstrap.Modal(document.getElementById('modalEstadisticas'));
        modal.show();
        
        document.getElementById('modalEstadisticas').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
    
    reiniciar() {
        if (confirm('¿Estás seguro de reiniciar todo tu progreso?')) {
            this.puntos = 0;
            this.racha = 0;
            this.nivel = 1;
            this.combos = { actual: 0, maximo: 0, multiplicador: 1 };
            this.estadisticas = {
                totalEjercicios: this.ejerciciosOriginales.length,
                correctas: 0,
                incorrectas: 0,
                tiempoTotal: 0,
                precision: 0,
                rachaMaxima: 0
            };
            this.respuestas = [];
            
            this.ejercicios.forEach(ej => {
                ej.veces_practicado = 0;
                ej.veces_acertado = 0;
                ej.ultimo_intento = null;
                ej.tiempo_promedio = 0;
            });
            
            this.guardarProgreso();
            this.indiceActual = 0;
            this.mostrarEjercicio();
            this.actualizarEstadisticas();
            
            window.notificaciones?.info('Progreso reiniciado');
        }
    }
}

// Inicializar sistema de práctica
let practica;
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('practica-container')) {
        practica = new SistemaPractica();
        window.practica = practica;
    }
});

// Exportar para uso global
window.SistemaPractica = SistemaPractica;
