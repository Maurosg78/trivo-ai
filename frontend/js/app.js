document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('nutrition-form');
    const resultContainer = document.getElementById('result-container');

    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Previene el envío del formulario

        const searchInput = document.getElementById('search-input').value.trim();
        
        // Verifica si el campo está vacío
        if (!searchInput) {
            resultContainer.innerHTML = '<p>Please enter a product name or barcode.</p>';
            return;
        }

        // Muestra mensaje de carga
        resultContainer.innerHTML = '<p>Loading...</p>';

        try {
            // Realiza la solicitud al backend
            const response = await fetch(`http://localhost:4000/api/nutrition?input=${encodeURIComponent(searchInput)}`);
            const data = await response.json();

            // Procesa la respuesta
            if (data.success) {
                const product = data.product;
                const sources = product.sources.join(', ');
                const nutriments = product.nutriments;
                const ingredients = product.ingredients.length ? product.ingredients.join(', ') : 'Not available';

                resultContainer.innerHTML = `
                    <div class="result">
                        <h3>${product.name}</h3>
                        <p><strong>Sources:</strong> ${sources}</p>
                        <p><strong>Nutritional Information:</strong></p>
                        <ul>
                            ${Object.entries(nutriments).map(([key, value]) => `<li>${key}: ${value}</li>`).join('')}
                        </ul>
                        <p><strong>Ingredients:</strong> ${ingredients}</p>
                    </div>
                `;
            } else {
                resultContainer.innerHTML = `<p>${data.message}</p>`;
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            resultContainer.innerHTML = `<p>Error fetching product data. Please try again later.</p>`;
        }
    });
});
