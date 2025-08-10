// Archivo: static/script.js (Lógica para renderizar recursos híbridos)

document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const userInput = document.getElementById('userInput');
    const levelSelect = document.getElementById('level');
    const resultContainer = document.getElementById('result-container');
    const loader = document.getElementById('loader');

    generateBtn.addEventListener('click', generarRuta);

    async function generarRuta() {
        if (!userInput.value) {
            alert("Por favor, define un objetivo de aprendizaje.");
            return;
        }

        generateBtn.disabled = true;
        generateBtn.textContent = 'Generando...';
        loader.style.display = 'block';
        resultContainer.innerHTML = '';

        try {
            const response = await fetch('/generate-path', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    goal: userInput.value,
                    level: levelSelect.value
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: `Error del servidor: ${response.status}` }));
                throw new Error(errorData.error);
            }
            
            const data = await response.json();
            
            if (!data.core_topic || !data.specializations) {
                throw new Error("La IA devolvió una estructura de datos inesperada.");
            }

            renderMindMap(data);

        } catch (error) {
            resultContainer.innerHTML = `<p class="error">ERROR: ${error.message}</p>`;
        } finally {
            loader.style.display = 'none';
            generateBtn.disabled = false;
            generateBtn.textContent = '[ Generar Ruta Visual ]';
        }
    }

    function buildSearchLink(recurso) {
        const query = encodeURIComponent(recurso.query);
        switch (recurso.plataforma) {
            case "YouTube":
                return `https://www.youtube.com/results?search_query=${query}`;
            case "Google":
            default:
                return `https://www.google.com/search?q=${query}`;
        }
    }

    function renderMindMap(data) {
        resultContainer.innerHTML = '';
        let html = `<h2>${data.titulo_ruta}</h2>`;
        html += '<div class="mindmap">';
        
        const allPhases = [data.core_topic, ...data.specializations];

        allPhases.forEach(fase => {
            if (!fase || !fase.pasos) return;
            
            html += '<div class="fase-container">';
            html += `<div class="fase-title">${fase.nombre_fase}</div>`;
            html += '<div class="steps-wrapper">';
            
            fase.pasos.forEach(paso => {
                const principal = paso.recursos.recurso_principal;
                const alternativas = paso.recursos.alternativas;

                html += `
                    <div class="step-node">
                        <h4>${paso.titulo}</h4>
                        <p>${paso.descripcion}</p>
                        <div class="resource-container">
                            <a href="${principal.url}" class="primary-resource" target="_blank" rel="noopener noreferrer">
                                <strong>Recurso Principal:</strong> ${principal.titulo} &rarr;
                            </a>
                            <div class="alternatives-container">
                                <span>Alternativas (si el link falla):</span>
                                <a href="${buildSearchLink(alternativas[0])}" class="alternative-link" target="_blank" rel="noopener noreferrer">Buscar en ${alternativas[0].plataforma}</a>
                                <a href="${buildSearchLink(alternativas[1])}" class="alternative-link" target="_blank" rel="noopener noreferrer">Buscar en ${alternativas[1].plataforma}</a>
                            </div>
                        </div>
                    </div>
                `;
            });

            html += '</div></div>';
        });

        html += '</div>';
        resultContainer.innerHTML = html;
    }
});