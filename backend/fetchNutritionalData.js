async function fetchNutritionalData(barcode) {
    const API_URL = 'https://world.openfoodfacts.org/api/v0/product/';

    try {
        const response = await fetch(`${API_URL}${barcode}.json`);
        if (!response.ok) {
            console.error(`API responded with status ${response.status}: ${response.statusText}`);
            return null;
        }

        const data = await response.json();

        if (data.status === 1) {
            // Simplificar la estructura del resultado
            const product = {
                name: data.product.product_name || 'Unknown Product',
                ingredients: data.product.ingredients_text || 'No ingredients listed',
                nutriments: data.product.nutriments || {},
            };
            console.log('Product Data:', product);
            return product;
        } else {
            console.warn('Product not found. Please try a different barcode.');
            return null;
        }
    } catch (error) {
        console.error('Error fetching nutritional data:', error.message);
        return null;
    }
}

// Exporta la función
module.exports = { fetchNutritionalData };
