/* ============================================
   SISTEMA DE FLASHCARDS - ECOSISTEMA MORFOLOGÍA
   ============================================ */

class SistemaFlashcards {
    constructor() {
        this.flashcards = [];
        this.flashcardsOriginales = [];
        this.indiceActual = 0;
        this.categoriaActual = 'todos';
        this.dificultadActual = 'todas';
        this.modo = 'estudio'; // 'estudio', 'revision', 'examen'
        this.aprendidas = new Set();
        this.dificiles = new Set();
        this.estadisticas = {
            vistas: 0,
            aciertos: 0,
            fallos: 0,
            tiempoTotal: 0
        };
        this.tiempoInicio = null;
        this.historialRevision = [];
        this.filtrosActivos = {
            categorias: [],
            dificultades: [],
            etiquetas: []
        };
        
        this.inicializar();
    }
    
    async inicializar() {
        try {
            await this.cargarFlashcards();
            this.cargarProgreso();
            this.crearInterfaz();
            this.configurarEventos();
            this.actualizarEstadisticas();
            this.mostrarFlashcard();
        } catch (error) {
            console.error('Error inicializando flashcards:', error);
            window.notificaciones?.error('Error al cargar las flashcards');
        }
    }
    
    async cargarFlashcards() {
        try {
            const response = await fetch('/static/data/ejercicios.json');
            const data = await response.json();
            
            this.flashcardsOriginales = data.ejercicios.map(ej => ({
                id: ej.id,
                palabra: ej.palabra,
                base: ej.base,
                categoria: ej.tipo_prefijo,
                dificultad: ej.dificultad,
                pistas: ej.pistas || [],
                ejemplo: ej.ejemplo || '',
                oracion_correcta: ej.oracion_correcta || '',
                veces_vista: 0,
                veces_acertada: 0,
                ultima_revision: null,
                intervalo: 1, // días para próxima revisión
                factor_facilidad: 2.5, // algoritmo SM-2
                fecha_proxima_revision: new Date()
            }));
            
            this.flashcards = [...this.flashcardsOriginales];
        } catch (error) {
            console.error('Error cargando flashcards:', error);
            throw error;
        }
    }
    
    cargarProgreso() {
        const progreso = window.storage?.get('flashcards_progreso');
        if (progreso) {
            this.aprendidas = new Set(progreso.aprendidas || []);
            this.dificiles = new Set(progreso.dificiles || []);
            this.estadisticas = progreso.estadisticas || this.estadisticas;
            this.historialRevision = progreso.historialRevision || [];
            
            // Restaurar estado de cada flashcard
            if (progreso.flashcards) {
                this.flashcards.forEach(fc => {
                    const guardada = progreso.flashcards.find(f => f.id === fc.id);
                    if (guardada) {
                        Object.assign(fc, guardada);
                    }
                });
            }
        }
    }
    
    guardarProgreso() {
        window.storage?.set('flashcards_progreso', {
            aprendidas: Array.from(this.aprendidas),
            dificiles: Array.from(this.dificiles),
            estadisticas: this.estadisticas,
            historialRevision: this.historialRevision,
            flashcards: this.flashcards.map(fc => ({
                id: fc.id,
                veces_vista: fc.veces_vista,
                veces_acertada: fc.veces_acertada,
                ultima_revision: fc.ultima_revision,
                intervalo: fc.intervalo,
                factor_facilidad: fc.factor_facilidad
            }))
        });
    }
    
    crearInterfaz() {
        const container = document.getElementById('flashcard-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="flashcard-sistema">
                <!-- Barra de control superior -->
                <div class="control-bar mb-4">
                    <div class="row g-3">
                        <div class="col-md-3">
                            <select class="form-select" id="filtroCategoria">
                                <option value="todos">Todas las categorías</option>
                                <option value="cuantitativo">Cuantitativos</option>
                                <option value="negación">Negación</option>
                                <option value="posición">Posición</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <select class="form-select" id="filtroDificultad">
                                <option value="todas">Todas las dificultades</option>
                                <option value="1">★ Básico</option>
                                <option value="2">★★ Intermedio</option>
                                <option value="3">★★★ Avanzado</option>
                                <option value="4">★★★★ Experto</option>
                                <option value="5">★★★★★ Maestro</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <select class="form-select" id="modoEstudio">
                                <option value="estudio">Modo Estudio</option>
                                <option value="revision">Modo Revisión</option>
                                <option value="examen">Modo Examen</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <button class="btn btn-primary w-100" onclick="flashcards.aleatorio()">
                                <i class="bi bi-shuffle me-2"></i>Aleatorio
                            </button>
                        </div>
                    </div>
                    
                    <div class="row mt-3">
                        <div class="col-md-8">
                            <div class="progress" style="height: 10px;">
                                <div class="progress-bar bg-success" 
                                     id="progresoFlashcards" 
                                     style="width: ${(this.aprendidas.size / this.flashcards.length * 100) || 0}%">
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 text-end">
                            <span class="badge bg-primary" id="contadorFlashcards">
                                ${this.aprendidas.size}/${this.flashcards.length} aprendidas
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Tarjeta principal -->
                <div class="flashcard-container text-center mb-4">
                    <div class="flashcard" id="flashcard" onclick="flashcards.voltear()">
                        <div class="flashcard-inner">
                            <div class="flashcard-front">
                                <div id="frontContent"></div>
                            </div>
                            <div class="flashcard-back">
                                <div id="backContent"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Botones de control -->
                <div class="control-buttons text-center">
                    <div class="btn-group btn-group-lg" role="group">
                        <button class="btn btn-outline-danger" onclick="flashcards.dificil()">
                            <i class="bi bi-exclamation-triangle"></i> Difícil
                        </button>
                        <button class="btn btn-outline-warning" onclick="flashcards.repetir()">
                            <i class="bi bi-arrow-repeat"></i> Repetir
                        </button>
                        <button class="btn btn-outline-success" onclick="flashcards.facil()">
                            <i class="bi bi-check-circle"></i> Fácil
                        </button>
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-outline-secondary me-2" onclick="flashcards.anterior()">
                            <i class="bi bi-arrow-left"></i> Anterior
                        </button>
                        <button class="btn btn-outline-secondary" onclick="flashcards.siguiente()">
                            Siguiente <i class="bi bi-arrow-right"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Panel de estadísticas -->
                <div class="stats-panel mt-4">
                    <div class="row g-3">
                        <div class="col-md-3">
                            <div class="stat-card text-center">
                                <h5 class="text-muted mb-2">Vistas</h5>
                                <h3 id="totalVistas">${this.estadisticas.vistas}</h3>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card text-center">
                                <h5 class="text-muted mb-2">Aciertos</h5>
                                <h3 id="totalAciertos">${this.estadisticas.aciertos}</h3>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card text-center">
                                <h5 class="text-muted mb-2">Precisión</h5>
                                <h3 id="precisionFlashcards">
                                    ${this.calcularPrecision()}%
                                </h3>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card text-center">
                                <h5 class="text-muted mb-2">Tiempo promedio</h5>
                                <h3 id="tiempoPromedio">
                                    ${this.calcularTiempoPromedio()}s
                                </h3>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    configurarEventos() {
        document.getElementById('filtroCategoria')?.addEventListener('change', (e) => {
            this.filtrarCategoria(e.target.value);
        });
        
        document.getElementById('filtroDificultad')?.addEventListener('change', (e) => {
            this.filtrarDificultad(e.target.value);
        });
        
        document.getElementById('modoEstudio')?.addEventListener('change', (e) => {
            this.cambiarModo(e.target.value);
        });
    }
    
    mostrarFlashcard() {
        if (this.flashcards.length === 0) {
            document.getElementById('frontContent').innerHTML = `
                <h3>🎉 ¡Felicidades!</h3>
                <p>Has completado todas las flashcards de esta categoría</p>
                <button class="btn btn-light mt-3" onclick="flashcards.resetearFiltros()">
                    Ver todas
                </button>
            `;
            return;
        }
        
        const flashcard = this.flashcards[this.indiceActual % this.flashcards.length];
        this.tiempoInicio = Date.now();
        
        // Actualizar contador de vistas
        flashcard.veces_vista++;
        this.estadisticas.vistas++;
        
        // Mostrar contenido frontal
        document.getElementById('frontContent').innerHTML = `
            <h3 class="display-4 mb-4">${flashcard.palabra}</h3>
            <p class="opacity-75">Haz clic para ver los detalles</p>
            ${this.modo === 'examen' ? '<p class="small">Escribe la palabra completa...</p>' : ''}
        `;
        
        // Preparar contenido trasero
        const pistasHTML = flashcard.pistas.map(p => `<li>• ${p}</li>`).join('');
        
        document.getElementById('backContent').innerHTML = `
            <div class="text-start">
                <h4 class="mb-3">${flashcard.palabra}</h4>
                <p><strong>Base:</strong> ${flashcard.base}</p>
                <p><strong>Categoría:</strong> ${flashcard.categoria}</p>
                <p><strong>Dificultad:</strong> ${'★'.repeat(flashcard.dificultad)}</p>
                <div class="mt-3">
                    <strong>Pistas:</strong>
                    <ul class="list-unstyled mt-2">
                        ${pistasHTML}
                    </ul>
                </div>
                ${flashcard.ejemplo ? `
                    <div class="mt-3 p-3 bg-light rounded">
                        <strong>Ejemplo:</strong><br>
                        ${flashcard.ejemplo.replace('{palabra}', `<strong>${flashcard.palabra}</strong>`)}
                    </div>
                ` : ''}
            </div>
        `;
        
        // Actualizar indicadores de progreso
        this.actualizarIndicadores();
        this.guardarProgreso();
    }
    
    voltear() {
        const flashcard = document.getElementById('flashcard');
        flashcard.classList.toggle('flipped');
        
        if (flashcard.classList.contains('flipped')) {
            this.registrarTiempoVisualizacion();
        }
    }
    
    registrarTiempoVisualizacion() {
        if (this.tiempoInicio) {
            const tiempo = (Date.now() - this.tiempoInicio) / 1000;
            this.estadisticas.tiempoTotal += tiempo;
            this.tiempoInicio = null;
        }
    }
    
    siguiente() {
        this.registrarTiempoVisualizacion();
        this.indiceActual = (this.indiceActual + 1) % this.flashcards.length;
        document.getElementById('flashcard').classList.remove('flipped');
        this.mostrarFlashcard();
    }
    
    anterior() {
        this.registrarTiempoVisualizacion();
        this.indiceActual = (this.indiceActual - 1 + this.flashcards.length) % this.flashcards.length;
        document.getElementById('flashcard').classList.remove('flipped');
        this.mostrarFlashcard();
    }
    
    aleatorio() {
        this.registrarTiempoVisualizacion();
        this.indiceActual = Math.floor(Math.random() * this.flashcards.length);
        document.getElementById('flashcard').classList.remove('flipped');
        this.mostrarFlashcard();
    }
    
    async dificil() {
        const flashcard = this.flashcards[this.indiceActual];
        this.dificiles.add(flashcard.id);
        this.aprendidas.delete(flashcard.id);
        
        this.estadisticas.fallos++;
        flashcard.veces_acertada = (flashcard.veces_acertada || 0) - 1;
        
        await this.aplicarAlgoritmoSM2(flashcard, 1); // 1 = respuesta difícil
        this.registrarHistorial(flashcard, 'difícil');
        
        if (this.modo === 'examen') {
            this.siguiente();
        }
        
        window.notificaciones?.info('¡Sigue practicando!', 'warning');
        this.guardarProgreso();
    }
    
    async facil() {
        const flashcard = this.flashcards[this.indiceActual];
        this.aprendidas.add(flashcard.id);
        this.dificiles.delete(flashcard.id);
        
        this.estadisticas.aciertos++;
        flashcard.veces_acertada++;
        
        await this.aplicarAlgoritmoSM2(flashcard, 5); // 5 = respuesta fácil
        this.registrarHistorial(flashcard, 'fácil');
        
        if (this.modo === 'examen') {
            this.siguiente();
        }
        
        window.notificaciones?.exito('¡Bien hecho!');
        this.guardarProgreso();
    }
    
    repetir() {
        this.registrarTiempoVisualizacion();
        document.getElementById('flashcard').classList.remove('flipped');
        this.mostrarFlashcard();
    }
    
    async aplicarAlgoritmoSM2(flashcard, calidad) {
        // Algoritmo SM-2 para spaced repetition
        if (calidad >= 3) {
            if (flashcard.veces_acertada === 1) {
                flashcard.intervalo = 1;
            } else if (flashcard.veces_acertada === 2) {
                flashcard.intervalo = 6;
            } else {
                flashcard.intervalo = Math.round(flashcard.intervalo * flashcard.factor_facilidad);
            }
            flashcard.factor_facilidad = Math.max(
                1.3,
                flashcard.factor_facilidad + (0.1 - (5 - calidad) * (0.08 + (5 - calidad) * 0.02))
            );
        } else {
            flashcard.intervalo = 1;
            flashcard.veces_acertada = 0;
        }
        
        const hoy = new Date();
        flashcard.ultima_revision = hoy;
        flashcard.fecha_proxima_revision = new Date(hoy.getTime() + flashcard.intervalo * 24 * 60 * 60 * 1000);
    }
    
    registrarHistorial(flashcard, tipo) {
        this.historialRevision.push({
            id: flashcard.id,
            palabra: flashcard.palabra,
            tipo: tipo,
            fecha: new Date().toISOString()
        });
        
        // Mantener solo últimos 100 registros
        if (this.historialRevision.length > 100) {
            this.historialRevision.shift();
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
    
    aplicarFiltros() {
        this.flashcards = this.flashcardsOriginales.filter(fc => {
            if (this.categoriaActual !== 'todos' && fc.categoria !== this.categoriaActual) {
                return false;
            }
            if (this.dificultadActual !== 'todas' && 
                fc.dificultad.toString() !== this.dificultadActual) {
                return false;
            }
            return true;
        });
        
        this.indiceActual = 0;
        this.mostrarFlashcard();
        this.actualizarContador();
    }
    
    cambiarModo(modo) {
        this.modo = modo;
        
        if (modo === 'revision') {
            this.flashcards = this.flashcardsOriginales.filter(fc => {
                const proxima = new Date(fc.fecha_proxima_revision);
                return proxima <= new Date();
            });
        } else if (modo === 'examen') {
            this.flashcards = this.flashcardsOriginales.filter(fc => 
                !this.aprendidas.has(fc.id)
            );
        } else {
            this.aplicarFiltros();
        }
        
        this.indiceActual = 0;
        this.mostrarFlashcard();
    }
    
    resetearFiltros() {
        this.categoriaActual = 'todos';
        this.dificultadActual = 'todas';
        this.modo = 'estudio';
        this.flashcards = [...this.flashcardsOriginales];
        this.indiceActual = 0;
        
        document.getElementById('filtroCategoria').value = 'todos';
        document.getElementById('filtroDificultad').value = 'todas';
        document.getElementById('modoEstudio').value = 'estudio';
        
        this.mostrarFlashcard();
    }
    
    calcularPrecision() {
        if (this.estadisticas.aciertos + this.estadisticas.fallos === 0) return 0;
        return Math.round((this.estadisticas.aciertos / 
            (this.estadisticas.aciertos + this.estadisticas.fallos)) * 100);
    }
    
    calcularTiempoPromedio() {
        if (this.estadisticas.vistas === 0) return 0;
        return (this.estadisticas.tiempoTotal / this.estadisticas.vistas).toFixed(1);
    }
    
    actualizarIndicadores() {
        const progreso = (this.aprendidas.size / this.flashcardsOriginales.length) * 100;
        document.getElementById('progresoFlashcards').style.width = `${progreso}%`;
        document.getElementById('contadorFlashcards').innerHTML = 
            `${this.aprendidas.size}/${this.flashcardsOriginales.length} aprendidas`;
    }
    
    actualizarEstadisticas() {
        document.getElementById('totalVistas').textContent = this.estadisticas.vistas;
        document.getElementById('totalAciertos').textContent = this.estadisticas.aciertos;
        document.getElementById('precisionFlashcards').textContent = this.calcularPrecision() + '%';
        document.getElementById('tiempoPromedio').textContent = this.calcularTiempoPromedio() + 's';
    }
    
    actualizarContador() {
        document.getElementById('totalFlashcards').textContent = this.flashcards.length;
    }
    
    // Exportar estadísticas
    exportarEstadisticas() {
        const data = {
            estadisticas: this.estadisticas,
            aprendidas: Array.from(this.aprendidas),
            dificiles: Array.from(this.dificiles),
            historial: this.historialRevision,
            fecha: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `flashcards-estadisticas-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    // Importar estadísticas
    importarEstadisticas(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                this.estadisticas = data.estadisticas;
                this.aprendidas = new Set(data.aprendidas);
                this.dificiles = new Set(data.dificiles);
                this.historialRevision = data.historial || [];
                this.guardarProgreso();
                this.actualizarIndicadores();
                this.actualizarEstadisticas();
                window.notificaciones?.exito('Estadísticas importadas correctamente');
            } catch (error) {
                window.notificaciones?.error('Error al importar estadísticas');
            }
        };
        reader.readAsText(file);
    }
    
    // Reiniciar progreso
    reiniciar() {
        if (confirm('¿Estás seguro de reiniciar todo tu progreso?')) {
            this.aprendidas.clear();
            this.dificiles.clear();
            this.estadisticas = {
                vistas: 0,
                aciertos: 0,
                fallos: 0,
                tiempoTotal: 0
            };
            this.historialRevision = [];
            
            this.flashcards.forEach(fc => {
                fc.veces_vista = 0;
                fc.veces_acertada = 0;
                fc.ultima_revision = null;
                fc.intervalo = 1;
                fc.factor_facilidad = 2.5;
            });
            
            this.guardarProgreso();
            this.actualizarIndicadores();
            this.actualizarEstadisticas();
            this.mostrarFlashcard();
            
            window.notificaciones?.info('Progreso reiniciado');
        }
    }
}

// Inicializar sistema de flashcards
let flashcards;
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('flashcard-container')) {
        flashcards = new SistemaFlashcards();
        window.flashcards = flashcards;
    }
});

// Exportar para uso global
window.SistemaFlashcards = SistemaFlashcards;
