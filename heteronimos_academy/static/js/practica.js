/* ============================================
   PRÁCTICA - LÓGICA ESPECÍFICA
   ============================================ */

let heteronimosGlobal = [];

function cargarHeteronimoAleatorio() {
    fetch('/api/heteronimos/random')
        .then(res => res.json())
        .then(data => {
            heteronimosGlobal = data;
            document.getElementById('palabraActual').textContent = data.masculino;
        });
}

function verificarTraduccion() {
    const respuesta = document.getElementById('respuestaTraduccion').value.toLowerCase().trim();
    const correcta = heteronimosGlobal.femenino;
    const feedback = document.getElementById('feedbackTraduccion');
    
    if (!respuesta) {
        mostrarNotificacion('Por favor ingresa una respuesta', 'danger');
        return;
    }
    
    if (respuesta === correcta) {
        feedback.innerHTML = '<div class="alert alert-success rounded-pill">✅ ¡Correcto! Muy bien.</div>';
        mostrarNotificacion('¡Respuesta correcta!', 'success');
        cargarHeteronimoAleatorio();
        document.getElementById('respuestaTraduccion').value = '';
        actualizarPuntuacion(10);
    } else {
        feedback.innerHTML = `
            <div class="alert alert-danger rounded-pill">
                ❌ Incorrecto. La respuesta correcta es "${correcta}".
            </div>
        `;
    }
}

function guardarEjemplo() {
    const masculino = document.getElementById('mascRedaccion').value.trim();
    const femenino = document.getElementById('femRedaccion').value.trim();
    const oracion = document.getElementById('oracionRedaccion').value.trim();
    
    if (!masculino || !femenino || !oracion) {
        mostrarNotificacion('Por favor completa todos los campos', 'danger');
        return;
    }
    
    fetch('/api/ejemplo/guardar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ masculino, femenino, oracion })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            mostrarNotificacion('¡Ejemplo guardado correctamente!', 'success');
            document.getElementById('mascRedaccion').value = '';
            document.getElementById('femRedaccion').value = '';
            document.getElementById('oracionRedaccion').value = '';
            cargarEjemplos();
            actualizarPuntuacion(5);
        }
    });
}

function cargarEjemplos() {
    fetch('/api/ejemplos/usuario')
        .then(res => res.json())
        .then(ejemplos => {
            const container = document.getElementById('listaEjemplos');
            if (ejemplos.length === 0) {
                container.innerHTML = '<p class="text-muted text-center">Aún no has guardado ejemplos.</p>';
                return;
            }
            container.innerHTML = ejemplos.map(e => `
                <div class="card mb-2 border-0 shadow-sm">
                    <div class="card-body">
                        <strong class="text-primary">${e.masculino} / ${e.femenino}</strong>
                        <p class="mb-0 mt-1">${e.oracion}</p>
                        <small class="text-muted">${e.fecha}</small>
                    </div>
                </div>
            `).join('');
        });
}

// Inicializar
if (document.getElementById('palabraActual')) {
    cargarHeteronimoAleatorio();
    cargarEjemplos();
}
