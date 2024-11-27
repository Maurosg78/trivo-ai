const express = require('express');
const cors = require('cors');
const axios = require('axios');
const app = express();

app.use(cors());

const PORT = 4000;

// Clave API de USDA
const api_key = 'kd28xuanbTU4ZhuAtWS29tHeoP2jtsEEahsaml43';

// Función para obtener los datos nutricionales de la API de USDA
async function fetchNutritionalData(ingredient) {
    try {
        // Realiza la solicitud GET a la API de USDA dentro de una función async
        const response = await axios.get('https://api.nal.usda.gov/fdc/v1/foods/search', {
            params: {
                query: ingredient,
                api_key: api_key // Usamos la clave API correcta aquí
            }
        });

        // Verifica si la respuesta tiene datos
        if (response.data && response.data.foods) {
            return {
                ingredient: ingredient,
                nutrients: response.data.foods[0].foodNutrients // Extrae los nutrientes del primer resultado
            };
        } else {
            return null; // Si no hay resultados, retorna null
        }
    } catch (error) {
        console.error('Error al obtener los datos de la API:', error);
        throw new Error('Error en la obtención de datos nutricionales'); // Lanza un error si algo falla
    }
}

// Endpoint para obtener datos nutricionales
app.get('/api/nutrition', async (req, res) => {
    const ingredient = req.query.ingredient;  // Obtener el ingrediente desde la URL

    if (!ingredient) {
        return res.status(400).json({ message: 'Por favor ingresa un ingrediente.' });
    }

    try {
        const nutrientData = await fetchNutritionalData(ingredient); // Obtener datos nutricionales

        if (nutrientData) {
            res.json(nutrientData);  // Si los datos se obtienen, devolverlos en formato JSON
        } else {
            res.status(404).json({ message: "No se encontraron datos para este ingrediente." });
        }
    } catch (error) {
        console.error("Error en la obtención de datos:", error);
        res.status(500).json({ message: "Error al obtener los datos nutricionales." });
    }
});

// Iniciar el servidor
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
});

