// script.js
document.getElementById('getNutritionalDataButton').addEventListener('click', async () => {
    const ingredient = document.getElementById('ingredientInput').value; // Obtener el ingrediente desde el input
    if (ingredient.trim() === '') {
        alert('Por favor ingresa un ingrediente.');
        return;
    }

    try {
        const response = await fetch(`http://localhost:4000/api/nutrition?ingredient=${ingredient}`);
        const data = await response.json();

        if (data.nutrients) {
            // Mostrar los datos nutricionales en el frontend
            document.getElementById('result').innerHTML = `
                <h2>Datos nutricionales para ${data.ingredient}:</h2>
                <ul>
                    ${data.nutrients.map(nutrient => `
                        <li><strong>${nutrient.nutrientName}:</strong> ${nutrient.value} ${nutrient.unitName}</li>
                    `).join('')}
                </ul>
            `;
        } else {
            document.getElementById('result').innerHTML = `<p>No se encontraron datos para el ingrediente solicitado.</p>`;
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `<p>Error al obtener los datos nutricionales. Intenta nuevamente.</p>`;
        console.error(error);
    }
});
