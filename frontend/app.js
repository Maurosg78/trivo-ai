document.getElementById('nutrition-form').addEventListener('submit', async (event) => {
    event.preventDefault();
  
    const searchInput = document.getElementById('search-input').value.trim();
    const resultContainer = document.getElementById('result-container');
  
    resultContainer.innerHTML = '<p>Loading...</p>';
  
    try {
      const response = await fetch(`http://localhost:4000/api/nutrition/${encodeURIComponent(searchInput)}`);
      const data = await response.json();
  
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
  