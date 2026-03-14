const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

require('dotenv').config();

const TOKEN_SECRETO = process.env.MICROSERVICES_API_KEY

const connectDB = require('./database');

const app = express();

app.use(cors());
app.use(express.json());

connectDB();

function requireToken(req, res, next) {
    const token = req.headers["authorization"] || req.headers["Authorization"];
    
    if (!token || token !== TOKEN_SECRETO) {
        return res.status(403).json({ error: "No autorizado" });
    }
    next();
}

app.use('/api', requireToken);


const ventaSchema = new mongoose.Schema({
  usuarioId: String,
  usuarioEmail: String,
  productos: [{
    productoId: String,
    nombre: String,
    cantidad: Number,
    precioUnitario: Number
  }],
  total: Number,
  fecha: { type: Date, default: Date.now },
  metodoPago: String
});

const Venta = mongoose.model('Venta', ventaSchema);

app.post('/api/ventas', async (req, res) => {
  try {
    const venta = new Venta(req.body);
    await venta.save();
    res.status(201).json(venta);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.get('/api/ventas', async (req, res) => {
  try {
    const ventas = await Venta.find().sort({ fecha: -1 });
    res.json(ventas);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/ventas/:id', async (req, res) => {
  try {
    const venta = await Venta.findById(req.params.id);
    if (!venta) return res.status(404).json({ error: 'Venta no encontrada' });
    res.json(venta);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/', (req, res) => {
  res.json({ mensaje: 'Microservicio de Ventas funcionando' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Servidor corriendo en http://localhost:${PORT}`);
});