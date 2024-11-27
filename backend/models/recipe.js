const mongoose = require('mongoose');

// Esquema de receta
const recipeSchema = new mongoose.Schema({
  name: { type: String, required: true },
  ingredients: [{ type: String }],
  steps: [{ type: String }],
  nutrition: {
    protein: Number,
    fiber: Number,
    vitamins: { type: Map, of: Number }, // Vitaminas con valores detallados
  },
  physicoChemicalProperties: {
    consistency: String,
    elasticity: Number,
    moistureLevel: Number,
  },
  industrialApplications: [String], // Ejemplo: ["Pizza", "Pasta", "Tortilla"]
});

// Exportar el modelo Recipe
module.exports = mongoose.model('Recipe', recipeSchema);
