/* ============================================
   PROGRESO - LÓGICA ESPECÍFICA
   ============================================ */

function cargarEstadisticas() {
    fetch('/api/estadisticas/completas')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error('Error cargando estadísticas');
                return;
            }
            
            // Actualizar tarjetas principales
            document.getElementById('puntosDisplay').textContent = data.usuario.puntos_totales;
            document.getElementById('nivelDisplay').innerHTML = 
                `${data.usuario.nivel}<br><small>${data.usuario.nombre_nivel}</small>`;
            document.getElementById('rachaDisplay').textContent = data.usuario.racha_actual;
            document.getElementById('mejorRachaDisplay').textContent = data.usuario.mejor_racha;
            
            // Actualizar progreso por categorías
            const categoriasHtml = data.categorias.map(cat => `
                <div class="col-md-6 mb-3">
                    <div class="card border-0 shadow-sm">
                        <div class="card-body">
                            <h6><i class="fas ${cat.icono} me-2"></i>${cat.nombre}</h6>
                            <div class="progress mb-2" style="height: 8px;">
                                <div class="progress-bar bg-success" 
                                     style="width: ${(cat.respuestas_correctas / 30) * 100}%"></div>
                            </div>
                            <small>${cat.respuestas_correctas} respuestas correctas</small><br>
                            <small class="text-muted">${cat.puntos} puntos</small>
                            ${cat.completada ? '<span class="badge bg-success float-end">Completada</span>' : ''}
                        </div>
                    </div>
                </div>
            `).join('');
            
            const categoriasContainer = document.getElementById('categoriasProgreso');
            if (categoriasContainer) {
                categoriasContainer.innerHTML = categoriasHtml;
            }
            
            // Logros
            const logros = [
                { icono: "fa-seedling", nombre: "Primeros Pasos", 
                  condicion: data.usuario.puntos_totales >= 100, color: "success" },
                { icono: "fa-fire", nombre: "En Racha", 
                  condicion: data.usuario.racha_actual >= 5, color: "warning" },
                { icono: "fa-crown", nombre: "Maestro", 
                  condicion: data.usuario.puntos_totales >= 500, color: "primary" },
                { icono: "fa-trophy", nombre: "Leyenda", 
                  condicion: data.usuario.puntos_totales >= 1000, color: "gold" }
            ];
            
            const logrosHtml = logros.map(logro => `
                <div class="col-md-3 text-center mb-3">
                    <div class="achievement-badge bg-${logro.condicion ? logro.color : 'secondary'} mx-auto mb-2" 
                         style="width:70px;height:70px;border-radius:50%;display:flex;align-items:center;justify-content:center">
                        <i class="fas ${logro.icono} text-white fa-2x"></i>
                    </div>
                    <h6>${logro.nombre}</h6>
                    <small class="text-muted">${logro.condicion ? 'Desbloqueado' : 'Bloqueado'}</small>
                </div>
            `).join('');
            
            const logrosContainer = document.getElementById('logrosList');
            if (logrosContainer) {
                logrosContainer.innerHTML = logrosHtml;
            }
        })
        .catch(error => console.error('Error:', error));
}

// Inicializar
if (document.getElementById('puntosDisplay')) {
    cargarEstadisticas();
}
