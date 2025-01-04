// Importar dependencias
const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");
const morgan = require("morgan");
const axios = require("axios");
const mongoose = require("mongoose");
const compression = require("compression");
const levenshtein = require("fast-levenshtein");

// Configuración de variables de entorno
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware global
app.use(cors());
app.use(express.json());
app.use(morgan("dev"));
app.use(compression());

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

// Modelo de Producto
const productSchema = new mongoose.Schema(
  {
    barcode: { type: String, required: true, unique: true },
    name: { type: String, default: "Producto sin nombre" },
    structuredIngredients: { type: Array, default: [] },
    problematicIngredients: { type: Array, default: [] },
    unclassifiedTerms: { type: Array, default: [] },
    nutritionalSummary: { type: Map, of: Object, default: {} },
    flaggedNutrients: { type: Array, default: [] },
  },
  { timestamps: true }
);

const Product = mongoose.model("Product", productSchema);

// Base de datos integrada de ingredientes problemáticos
const problematicIngredientsDB = {
  nutritionalLimits: {
    fat: { max: 3.0, unit: "g" },
    carbohydrates: { max: 50.0, unit: "g" },
    sugars: { max: 5.0, unit: "g" },
    proteins: { min: 6.0, unit: "g" },
    salt: { max: 1.5, unit: "g" },
  },
  ingredients: {
    gluten: {
      reason: "Común alérgeno presente en el trigo, la cebada y el centeno.",
      substitutes: ["almond flour", "coconut flour", "rice flour"],
      regulatedBy: ["EU", "USDA"],
      categories: ["allergen"],
      aliases: [
        "trigo",
        "cebada",
        "centeno",
        "harina de trigo",
        "farine de blé",
        "wheat flour",
        "kamut",
        "spelt",
        "einkorn",
        "emmer",
      ],
    },
    lactose: {
      reason: "Alérgeno común presente en productos lácteos.",
      substitutes: ["almond milk", "oat milk", "coconut milk"],
      regulatedBy: ["EU", "USDA"],
      categories: ["allergen"],
      aliases: [
        "lactosa",
        "milk",
        "leche",
        "dairy",
        "buttermilk",
        "cheese",
        "cream",
        "whey",
      ],
    },
    soy: {
      reason: "Alérgeno común presente en productos a base de soya.",
      substitutes: ["coconut-based products", "almond-based products"],
      regulatedBy: ["EU", "USDA"],
      categories: ["allergen"],
      aliases: [
        "soja",
        "soy protein",
        "edamame",
        "soy protein isolate",
        "tofu",
        "soya",
        "tempeh",
        "lecithin (soy)",
      ],
    },
    egg: {
      reason: "Común alérgeno en productos derivados del huevo.",
      substitutes: ["flaxseed meal", "aquafaba", "chia seeds"],
      regulatedBy: ["EU", "USDA"],
      categories: ["allergen"],
      aliases: ["huevo", "egg", "albumen", "ovoproductos", "ovum", "egg powder"],
    },
    "tree nuts": {
      reason: "Alérgeno presente en nueces, almendras, avellanas, entre otros.",
      substitutes: ["sunflower seeds", "pumpkin seeds"],
      regulatedBy: ["EU", "USDA"],
      categories: ["allergen"],
      aliases: [
        "nueces",
        "almendras",
        "avellanas",
        "pecans",
        "macadamia",
        "cashews",
        "brazil nuts",
        "walnuts",
      ],
    },
    crustaceans: {
      reason: "Alérgeno común en productos del mar como camarones y cangrejos.",
      substitutes: ["tofu", "jackfruit", "mushrooms"],
      regulatedBy: ["EU", "USDA"],
      categories: ["allergen"],
      aliases: ["crustáceos", "shrimp", "prawns", "lobster", "crab", "langoustine"],
    },
    "monosodium glutamate (MSG)": {
      reason: "Puede causar reacciones de sensibilidad en algunas personas.",
      substitutes: ["nutritional yeast", "mushroom powder"],
      regulatedBy: ["FAO", "USDA"],
      categories: ["chemical", "sensitivity"],
      aliases: ["MSG", "glutamato monosódico", "ajinomoto", "E621", "umami enhancer"],
    },
    "sodium nitrite (E250)": {
      reason: "Posible carcinógeno usado como conservante en carnes procesadas.",
      substitutes: ["celery juice powder", "natural salt"],
      regulatedBy: ["EU", "WHO"],
      categories: ["chemical", "preservative"],
      aliases: ["nitrito de sodio", "sodium nitrite"],
    },
    "tartrazine (E102)": {
      reason: "Colorante artificial amarillo vinculado a hiperactividad en niños y reacciones alérgicas.",
      substitutes: ["beet juice", "turmeric", "spirulina"],
      regulatedBy: ["EU", "USDA"],
      categories: ["chemical", "colorant"],
      aliases: ["tartrazine", "FD&C Yellow No. 5"],
    },
    "aspartame (E951)": {
      reason: "Edulcorante artificial asociado con posibles efectos neurotóxicos y trastornos metabólicos.",
      substitutes: ["stevia", "honey", "maple syrup"],
      regulatedBy: ["EU", "USDA"],
      categories: ["chemical", "sweetener"],
      aliases: ["aspartame", "NutraSweet", "Equal"],
    },
    "high fructose corn syrup": {
      reason: "Asociado con obesidad y problemas metabólicos.",
      substitutes: ["honey", "maple syrup"],
      regulatedBy: ["USDA"],
      categories: ["sweetener", "controversial"],
      aliases: ["HFCS", "jarabe de maíz de alta fructosa", "corn syrup solids", "glucose-fructose syrup"],
    },
  },
};

// Función para tokenizar ingredientes
const tokenizeIngredients = (text) => {
  const irrelevantWords = ["of", "and", "in", "on", "with", "by", "to", "for", "as"];
  const cleanedText = text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // Elimina diacríticos (tildes)
    .replace(/[^a-zA-Z0-9\s]/g, "")
    .toLowerCase();

  return cleanedText
    .split(/\s+/)
    .filter((word) => word.length >= 3 && !irrelevantWords.includes(word));
};

// Función para analizar ingredientes y clasificarlos
const analyzeIngredients = (ingredientsText, problematicDB) => {
  const detectedProblems = [];
  const unclassifiedTerms = [];
  const structuredIngredients = [];
  const seenTerms = new Set();

  const tokens = tokenizeIngredients(ingredientsText);

  tokens.forEach((token) => {
    if (seenTerms.has(token)) return;
    seenTerms.add(token);

    let found = false;

    Object.entries(problematicDB.ingredients).forEach(([key, value]) => {
      if (value.aliases.includes(token)) {
        detectedProblems.push({
          ingredient: key,
          reason: value.reason,
          substitutes: value.substitutes,
          regulatedBy: value.regulatedBy,
          categories: value.categories,
        });
        structuredIngredients.push({ name: token, problematic: true });
        found = true;
      }
    });

    if (!found) {
      structuredIngredients.push({ name: token, problematic: "check" });
      unclassifiedTerms.push(token);
    }
  });

  return {
    detectedProblems: [...new Set(detectedProblems)],
    unclassifiedTerms,
    structuredIngredients,
  };
};

// Función para analizar valores nutricionales
const analyzeNutritionalValues = (nutritionalValues, limits) => {
  const flaggedNutrients = [];

  Object.entries(nutritionalValues).forEach(([key, value]) => {
    if (limits[key]) {
      const { min, max } = limits[key];
      if ((min !== undefined && value < min) || (max !== undefined && value > max)) {
        flaggedNutrients.push({
          nutrient: key,
          value,
          limit: limits[key],
          status: value < min ? "below minimum" : "above maximum",
        });
      }
    }
  });

  return flaggedNutrients;
};

// Ruta del servidor para analizar productos por código de barras
app.get("/api/product/:barcode", async (req, res) => {
  const barcode = req.params.barcode;

  try {
    let product = await Product.findOne({ barcode });

    if (!product) {
      const offResponse = await axios.get(
        `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`
      );

      if (offResponse.data && offResponse.data.product) {
        const productData = offResponse.data.product;

        const { detectedProblems, unclassifiedTerms, structuredIngredients } =
          analyzeIngredients(
            productData.ingredients_text || "",
            problematicIngredientsDB
          );

        const nutritionalSummary = productData.nutriments || {};
        const flaggedNutrients = analyzeNutritionalValues(
          nutritionalSummary,
          problematicIngredientsDB.nutritionalLimits
        );

        product = new Product({
          barcode,
          name: productData.product_name || "Producto sin nombre",
          structuredIngredients,
          problematicIngredients: detectedProblems,
          unclassifiedTerms,
          nutritionalSummary,
          flaggedNutrients,
        });

        await product.save();
      } else {
        return res.status(404).json({
          status: "error",
          message: "Producto no encontrado en OpenFoodFacts.",
        });
      }
    }

    res.json({
      status: "success",
      product: {
        barcode: product.barcode,
        name: product.name,
        structuredIngredients: product.structuredIngredients,
        problematicIngredients: product.problematicIngredients,
        unclassifiedTerms: product.unclassifiedTerms,
        nutritionalSummary: product.nutritionalSummary,
        flaggedNutrients: product.flaggedNutrients,
      },
    });
  } catch (error) {
    console.error("Error en /api/product/:barcode:", error.message);
    res.status(500).json({ status: "error", message: "Error interno del servidor." });
  }
});

// Iniciar servidor
const startServer = async () => {
  await connectToDatabase();
  app.listen(PORT, () => {
    console.log(`🚀 Servidor corriendo en http://localhost:${PORT}`);
  });
};

startServer();
