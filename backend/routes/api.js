const express = require('express');
const axios = require('axios');
const router = express.Router();

// Función para obtener datos nutricionales desde la API de USDA
async function fetchNutritionalData(ingredient) {
    const apiKey = process.env.USDA_API_KEY;
    const url = `https://api.nal.usda.gov/fdc/v1/foods/search?query=${ingredient}&api_key=${apiKey}`;
    
    try {
        const response = await axios.get(url);
        if (response.data.foods && response.data.foods.length > 0) {
            return response.data.foods[0].foodNutrients; // Obtenemos los nutrientes del primer resultado
        } else {
            return null;
        }
    } catch (error) {
        console.error("Error fetching data from USDA API:", error);
        return null;
    }
}

// Ruta para obtener los datos nutricionales de un ingrediente
router.get('/nutrition', async (req, res) => {
    const { ingredient } = req.query; // Recibimos el ingrediente a buscar

    if (!ingredient) {
        return res.status(400).json({ error: "Se debe proporcionar un ingrediente." });
    }

    const nutrients = await fetchNutritionalData(ingredient);

    if (nutrients) {
        return res.json({ ingredient, nutrients });
    } else {
        return res.status(404).json({ error: "No se encontraron datos nutricionales para este ingrediente." });
    }
});

module.exports = router;
