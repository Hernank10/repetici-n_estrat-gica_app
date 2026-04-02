/* ============================================
   EJERCICIOS - LÓGICA ESPECÍFICA
   ============================================ */

let ejercicioActual = null;
let quizActual = null;
let puntuacionEjercicios = 0;

function cargarEjercicios() {
    const dificultad = document.getElementById('dificultadSelect')?.value || 1;
    
    // Cargar ejercicio de completación
    fetch(`/api/ejercicio/completacion/random?dificultad=${dificultad}`)
        .then(res => res.json())
        .then(data => {
            ejercicioActual = data;
            document.getElementById('textoEjercicio').textContent = data.texto;
            document.getElementById('completacionInfo').innerHTML = `
                ${data.categoria} | Dificultad: ${'⭐'.repeat(data.dificultad)}
            `;
            document.getElementById('respuestaM').value = '';
            document.getElementById('respuestaF').value = '';
            document.getElementById('feedbackCompletacion').innerHTML = '';
        })
        .catch(error => console.error('Error:', error));
    
    // Cargar quiz
    fetch(`/api/ejercicio/quiz/random?dificultad=${dificultad}`)
        .then(res => res.json())
        .then(data => {
            quizActual = data;
            document.getElementById('preguntaQuiz').textContent = data.pregunta;
            document.getElementById('quizInfo').innerHTML = `
                ${data.categoria} | Dificultad: ${'⭐'.repeat(data.dificultad)}
            `;
            
            const opcionesHtml = data.opciones.map((op, idx) => `
                <div class="form-check mb-2">
                    <input class="form-check-input" type="radio" name="quizRespuesta" value="${op}" id="op_${idx}">
                    <label class="form-check-label" for="op_${idx}">${op}</label>
                </div>
            `).join('');
            document.getElementById('opcionesQuiz').innerHTML = opcionesHtml;
            document.getElementById('feedbackQuiz').innerHTML = '';
        })
        .catch(error => console.error('Error:', error));
}

function verificarCompletacion() {
    const masc = document.getElementById('respuestaM').value.toLowerCase().trim();
    const fem = document.getElementById('respuestaF').value.toLowerCase().trim();
    
    if (!masc || !fem) {
        mostrarNotificacion('Por favor completa ambos campos', 'danger');
        return;
    }
    
    fetch('/api/ejercicio/completacion/verificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ejercicio_id: ejercicioActual.id,
            masculino: masc,
            femenino: fem
        })
    })
    .then(res => res.json())
    .then(data => {
        const feedback = document.getElementById('feedbackCompletacion');
        if (data.correcto) {
            feedback.innerHTML = `
                <div class="alert alert-success rounded-pill">
                    <i class="fas fa-trophy me-2"></i>
                    ✅ ¡Correcto! +${data.puntos_ganados} puntos.
                </div>
            `;
            mostrarNotificacion(`¡Correcto! +${data.puntos_ganados} puntos`, 'success');
            actualizarPuntuacion(data.puntos_ganados);
        } else {
            feedback.innerHTML = `
                <div class="alert alert-danger rounded-pill">
                    <i class="fas fa-book me-2"></i>
                    ❌ Incorrecto. Respuesta correcta: "${data.respuesta_correcta_m}" y "${data.respuesta_correcta_f}"
                </div>
            `;
        }
        setTimeout(cargarEjercicios, 2000);
    });
}

function verificarQuiz() {
    const seleccion = document.querySelector('input[name="quizRespuesta"]:checked');
    if (!seleccion) {
        mostrarNotificacion('Por favor selecciona una respuesta', 'danger');
        return;
    }
    
    fetch('/api/ejercicio/quiz/verificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            quiz_id: quizActual.id,
            respuesta: seleccion.value
        })
    })
    .then(res => res.json())
    .then(data => {
        const feedback = document.getElementById('feedbackQuiz');
        if (data.correcto) {
            feedback.innerHTML = `
                <div class="alert alert-success rounded-pill">
                    <i class="fas fa-trophy me-2"></i>
                    ✅ ¡Correcto! +${data.puntos_ganados} puntos.
                </div>
            `;
            mostrarNotificacion(`¡Correcto! +${data.puntos_ganados} puntos`, 'success');
            actualizarPuntuacion(data.puntos_ganados);
        } else {
            feedback.innerHTML = `
                <div class="alert alert-danger rounded-pill">
                    <i class="fas fa-book me-2"></i>
                    ❌ Incorrecto. Respuesta correcta: "${data.respuesta_correcta}"
                </div>
            `;
        }
        setTimeout(cargarEjercicios, 2000);
    });
}

// Inicializar cuando la página cargue
if (document.getElementById('dificultadSelect')) {
    document.getElementById('dificultadSelect').addEventListener('change', cargarEjercicios);
    cargarEjercicios();
}
