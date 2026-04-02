/* ============================================
   FLASHCARDS - LÓGICA ESPECÍFICA
   ============================================ */

let flashcardActual = null;
let flashcardGirada = false;

function cargarFlashcard() {
    const categoria = document.getElementById('categoriaFlashcard')?.value || '';
    let url = '/api/flashcard/random';
    if (categoria) url += `?categoria=${categoria}`;
    
    fetch(url)
        .then(res => res.json())
        .then(data => {
            flashcardActual = data;
            document.getElementById('preguntaFlashcard').textContent = data.pregunta;
            document.getElementById('respuestaFlashcard').textContent = data.respuesta;
            document.getElementById('categoriaBadge').innerHTML = getCategoriaNombre(data.categoria);
            resetFlip();
        })
        .catch(error => console.error('Error:', error));
}

function getCategoriaNombre(categoria) {
    const nombres = {
        'definicion': '📖 Definición',
        'parentesco': '👨‍👩‍👧 Parentesco',
        'animales': '🐾 Animales',
        'titulos': '👑 Títulos',
        'profesiones': '💼 Profesiones',
        'literario': '📖 Literario',
        'semantica': '🧠 Semántica',
        'etimologia': '📜 Etimología',
        'aprendizaje': '🎓 Aprendizaje',
        'preservacion': '🌍 Preservación',
        'clasificacion': '🏷️ Clasificación',
        'casos_especiales': '⚠️ Casos Especiales'
    };
    return nombres[categoria] || categoria;
}

function voltearFlashcard() {
    const flashcard = document.getElementById('flashcard');
    flashcardGirada = !flashcardGirada;
    flashcard.style.transform = flashcardGirada ? 'rotateY(180deg)' : 'rotateY(0deg)';
}

function siguienteFlashcard() {
    resetFlip();
    cargarFlashcard();
}

function resetFlip() {
    const flashcard = document.getElementById('flashcard');
    flashcardGirada = false;
    flashcard.style.transform = 'rotateY(0deg)';
}

function marcarCorrecta() {
    if (flashcardActual) {
        fetch('/api/flashcard/verificar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                flashcard_id: flashcardActual.id,
                respuesta: flashcardActual.respuesta
            })
        })
        .then(res => res.json())
        .then(() => {
            siguienteFlashcard();
            cargarProgreso();
            mostrarNotificacion('¡Respuesta correcta! +1 punto', 'success');
        });
    }
}

function cargarProgreso() {
    fetch('/api/estadisticas/flashcards')
        .then(res => res.json())
        .then(data => {
            const porcentaje = data.porcentaje;
            document.getElementById('progresoNumero').textContent = `${porcentaje}%`;
            document.getElementById('progresoTexto').textContent = 
                `${data.estudiadas} flashcards estudiadas de ${data.total}`;
            const circle = document.getElementById('progressCircle');
            if (circle) {
                circle.style.background = `conic-gradient(#28a745 ${porcentaje * 3.6}deg, #e9ecef 0deg)`;
            }
        });
}

function resetFlashcards() {
    if (confirm('¿Reiniciar todo el progreso de flashcards?')) {
        fetch('/api/flashcards/reset', { method: 'POST' })
            .then(() => cargarProgreso());
    }
}

// Inicializar
if (document.getElementById('flashcard')) {
    document.getElementById('flashcard').addEventListener('click', (e) => {
        if (!e.target.closest('button')) {
            voltearFlashcard();
        }
    });
    
    const categoriaSelect = document.getElementById('categoriaFlashcard');
    if (categoriaSelect) {
        categoriaSelect.addEventListener('change', cargarFlashcard);
    }
    
    cargarFlashcard();
    cargarProgreso();
}
