// Importar dependencias
const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");
const morgan = require("morgan");
const axios = require("axios");
const fs = require("fs");
const path = require("path");
const mongoose = require("mongoose");

// Configuración de variables de entorno
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
let server;

// Middleware global
app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

// Conexión a la base de datos MongoDB
const connectToDatabase = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log("✅ Conexión exitosa a MongoDB");
  } catch (error) {
    console.error("❌ Error al conectar a MongoDB:", error.message);
    process.exit(1);
  }
};

const closeDatabase = async () => {
  await mongoose.connection.close();
  console.log("✅ Conexión a MongoDB cerrada");
};

// Cargar la base de datos de ingredientes problemáticos
let problematicIngredientsDB = {};
try {
  const dataPath = path.resolve("./data/problematicIngredients.json");
  problematicIngredientsDB = JSON.parse(fs.readFileSync(dataPath, "utf-8"));

  if (Object.keys(problematicIngredientsDB).length === 0) {
    throw new Error("La base de datos está vacía");
  }
  console.log(`✅ Base de datos cargada: ${Object.keys(problematicIngredientsDB).length} ingredientes.`);
} catch (error) {
  console.error("❌ Error al cargar la base de datos de ingredientes problemáticos:", error.message);
  process.exit(1);
}

// Normas de nutrientes
const nutrientStandards = {
  "energy-kcal": { max: 250 },
  fat: { max: 10 },
  "saturated-fat": { max: 5 },
  carbohydrates: { max: 30 },
  sugars: { max: 5 },
  proteins: { min: 5 },
  salt: { max: 1.5 },
};

// Función para normalizar texto
const normalizeText = (text) =>
  text.toLowerCase().replace(/[^a-z0-9áéíóúñü\s]/gi, "").trim();

// Función para analizar ingredientes
const analyzeIngredients = (ingredientsText) => {
  const detectedProblems = [];
  const normalizedIngredients = normalizeText(ingredientsText).split(/\s*,\s*/);

  for (const ingredient of normalizedIngredients) {
    for (const [key, value] of Object.entries(problematicIngredientsDB)) {
      if (
        value.aliases.some((alias) =>
          normalizeText(ingredient).includes(normalizeText(alias))
        )
      ) {
        detectedProblems.push({
          ingredient: key,
          reason: value.reason,
          substitutes: value.substitutes,
        });
      }
    }
  }
  return detectedProblems;
};

// Función para analizar nutrientes
const analyzeNutrients = (nutrients) => {
  const analysis = {};
  for (const [key, value] of Object.entries(nutrientStandards)) {
    if (nutrients[key]) {
      if (value.max && nutrients[key] > value.max) {
        analysis[key] = { status: "exceeds", value: nutrients[key], max: value.max };
      } else if (value.min && nutrients[key] < value.min) {
        analysis[key] = { status: "below", value: nutrients[key], min: value.min };
      } else {
        analysis[key] = { status: "within", value: nutrients[key] };
      }
    }
  }
  return analysis;
};

// Modelo de Producto
const productSchema = new mongoose.Schema({
  barcode: { type: String, required: true, unique: true },
  name: String,
  ingredients: String,
  nutriments: Object,
  problematicIngredients: Array,
  nutrientAnalysis: Object,
});
const Product = mongoose.model("Product", productSchema);

// Rutas
app.get("/", (req, res) => {
  res.send("¡Bienvenido a TRIVO AI!");
});

app.post("/api/barcode", async (req, res) => {
  const { barcode } = req.body;

  if (!barcode || typeof barcode !== "string" || barcode.length < 8) {
    return res.status(400).json({
      status: "error",
      message: "Debes proporcionar un código de barras válido.",
    });
  }

  try {
    let product = await Product.findOne({ barcode });

    if (!product) {
      const response = await axios.get(
        `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`
      );

      if (response.data && response.data.product) {
        const productData = response.data.product;
        const problematicIngredients = analyzeIngredients(productData.ingredients_text || "");
        const nutrientAnalysis = analyzeNutrients(productData.nutriments || {});

        product = new Product({
          barcode,
          name: productData.product_name,
          ingredients: productData.ingredients_text || "No especificado",
          nutriments: productData.nutriments || {},
          problematicIngredients,
          nutrientAnalysis,
        });

        await product.save();
      } else {
        return res.status(404).json({ status: "error", message: "Producto no encontrado." });
      }
    }

    res.json({
      status: "success",
      product: {
        barcode: product.barcode,
        name: product.name,
        ingredients: product.ingredients,
        nutriments: product.nutriments,
        problematicIngredients: product.problematicIngredients,
        nutrientAnalysis: product.nutrientAnalysis,
      },
    });
  } catch (error) {
    console.error("Error en /api/barcode:", error.message);
    res.status(500).json({ status: "error", message: "Error interno del servidor." });
  }
});

// Iniciar servidor
if (process.env.NODE_ENV !== "test") {
  connectToDatabase();
  server = app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
  });
}

// Exportar para pruebas
module.exports = { app, server, connectToDatabase, closeDatabase };


