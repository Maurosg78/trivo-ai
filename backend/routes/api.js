const express = require('express');
const axios = require('axios');
const router = express.Router();
const Recipe = require('../models/recipe');

// Función auxiliar para obtener datos nutricionales de un ingrediente
async function fetchNutritionalData(ingredient, apiKey) {
    try {
        const response = await axios.get(`https://api.nal.usda.gov/fdc/v1/foods/search`, {
            params: { query: ingredient, api_key: apiKey }
        });
        if (response.data.foods && response.data.foods.length > 0) {
            // Filtrar solo los nutrientes importantes
            const nutrients = response.data.foods[0].foodNutrients;
            const filteredNutrients = {
                protein: nutrients.find(n => n.nutrientName === "Protein")?.value || 0,
                fiber: nutrients.find(n => n.nutrientName === "Fiber, total dietary")?.value || 0,
                vitaminC: nutrients.find(n => n.nutrientName === "Vitamin C, total ascorbic acid")?.value || 0,
            };
            return filteredNutrients;
        }
        return null;
    } catch (error) {
        console.error("Error al obtener datos nutricionales:", error.message);
        return null;
    }
}

// Ruta de prueba
router.get('/test', (req, res) => {
  res.json({ message: 'API test endpoint is working!' });
});

// Ruta para mejorar la receta con recomendaciones personalizadas
router.post('/improve-recipe', async (req, res) => {
    const { ingredients, goal } = req.body;
    const apiKey = process.env.USDA_API_KEY;
    const nutrientData = [];
    let totalNutrients = { protein: 0, fiber: 0, vitaminC: 0 };

    if (!Array.isArray(ingredients)) {
        return res.status(400).json({ error: "El campo 'ingredients' debe ser un array" });
    }

    try {
        for (const ingredient of ingredients) {
            let preparedIngredient = ingredient.toLowerCase() === 'quinoa' ? 'harina de quinoa' : ingredient;
            const nutrients = await fetchNutritionalData(preparedIngredient, apiKey);

            if (nutrients) {
                const protein = nutrients.find(n => n.nutrientName === "Protein")?.value || 0;
                const fiber = nutrients.find(n => n.nutrientName === "Fiber, total dietary")?.value || 0;
                const vitaminC = nutrients.find(n => n.nutrientName === "Vitamin C, total ascorbic acid")?.value || 0;

                totalNutrients.protein += protein;
                totalNutrients.fiber += fiber;
                totalNutrients.vitaminC += vitaminC;

                nutrientData.push({ ingredient, protein, fiber, vitaminC });
            } else {
                nutrientData.push({ ingredient, error: "No se encontraron datos para este ingrediente" });
            }
        }

        let recommendations = [];
        if (goal === "improve nutrition") {
            if (totalNutrients.protein < 50) recommendations.push("Agregar ingredientes ricos en proteínas, como tofu o legumbres.");
            if (totalNutrients.fiber < 25) recommendations.push("Agregar más fibra con ingredientes como avena o frutas.");
            if (totalNutrients.vitaminC < 60) recommendations.push("Agregar fuentes de vitamina C, como cítricos o pimientos.");
        }

        // Nuevas recomendaciones según los objetivos de los usuarios
        if (goal === "lose weight") {
            if (totalNutrients.fiber < 30) recommendations.push("Incluir más alimentos ricos en fibra, como verduras y granos enteros.");
            if (totalNutrients.protein < 40) recommendations.push("Incluir más proteínas bajas en grasa, como pollo o pescado.");
        }

        if (goal === "increase protein") {
            if (totalNutrients.protein < 60) recommendations.push("Aumentar la ingesta de proteínas con fuentes como carnes magras, pescado, huevos y legumbres.");
        }

        res.json({ message: "Datos nutricionales obtenidos y recomendaciones generadas", nutrientData, totalNutrients, recommendations });
    } catch (error) {
        console.error("Error al obtener datos nutricionales de los ingredientes:", error.message);
        res.status(500).send("Error al obtener datos nutricionales de los ingredientes");
    }
});
