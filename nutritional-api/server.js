const express = require('express');
const axios = require('axios');

const app = express();
const PORT = 4000;

// Endpoint para obtener datos nutricionales por código de barras
app.get('/api/nutrition/:barcode', async (req, res) => {
    const { barcode } = req.params;

    try {
        const response = await axios.get(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
        const data = response.data;

        if (data.status === 1) {
            res.json({
                success: true,
                product: {
                    name: data.product.product_name,
                    nutriments: data.product.nutriments
                }
            });
        } else {
            res.status(404).json({ success: false, message: 'Product not found' });
        }
    } catch (error) {
        console.error('Error fetching product data:', error);
        res.status(500).json({ success: false, message: 'Error fetching product data' });
    }
});

// Iniciar el servidor
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});

