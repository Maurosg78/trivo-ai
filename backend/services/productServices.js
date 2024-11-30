const axios = require('axios');

const getProductData = async (productName) => {
    try {
        // URL de Open Food Facts para obtener datos del producto por nombre
        const openFoodFactsUrl = `https://world.openfoodfacts.org/api/v0/product/${encodeURIComponent(productName)}.json`;
        const response = await axios.get(openFoodFactsUrl);

        if (response.data.status === 1) {
            return response.data.product; // Datos del producto si se encuentra
        } else {
            throw new Error('Producto no encontrado en Open Food Facts');
        }
    } catch (error) {
        console.error("Error al obtener datos del producto:", error.message);
        throw new Error('Error al obtener los datos del producto');
    }
};

module.exports = { getProductData };
