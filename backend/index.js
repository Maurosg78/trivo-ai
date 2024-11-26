require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const apiRoutes = require('./routes/api'); // Asegúrate de importar las rutas correctamente

const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(express.json());

// Usar las rutas definidas en api.js
app.use('/api', apiRoutes); // Esto hace que todas las rutas de 'api' estén disponibles

// Ruta simple
app.get('/', (req, res) => {
  res.send('Hello, Trivo AI Backend is running!');
});

// Conectar a MongoDB
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/trivoai';
mongoose
  .connect(MONGO_URI)
  .then(() => {
    console.log('Connected to MongoDB');
    app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });
  })
  .catch((err) => {
    console.error('Failed to connect to MongoDB', err);
  });

app.get('/test-mongo', async (req, res) => {
  try {
    const testCollection = mongoose.connection.db.collection('test');
    const result = await testCollection.insertOne({ message: 'MongoDB is working!' });
    res.json(result);
  } catch (err) {
    res.status(500).send(err.message);
  }
});

