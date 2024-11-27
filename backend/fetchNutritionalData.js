async function fetchNutritionalData(barcode) {
    try {
        const response = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
        const data = await response.json();

        if (data.status === 1) {
            console.log('Product Data:', data.product);
            return data.product;
        } else {
            console.warn('Product not found. Please try a different barcode.');
            return null;
        }
    } catch (error) {
        console.error('Error fetching nutritional data:', error);
        return null;
    }
}

// Prueba la función
fetchNutritionalData('3274080005003').then(product => {
    if (product) {
        console.log('Nutritional Information:', product.nutriments);
    } else {
        console.log('No product data found for this barcode.');
    }
});
