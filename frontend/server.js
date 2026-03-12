// backend/server.js — Node.js + Express + WebSocket + MQTT
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const mqtt = require('mqtt');
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

app.use(cors());
app.use(express.json());

// ─── MongoDB Schemas ───────────────────────
const BinSchema = new mongoose.Schema({
  binId: { type: String, unique: true, required: true },
  location: String,
  coordinates: { lat: Number, lng: Number },
  sensors: {
    fillLevel: { type: Number, default: 0 },      // Ultrasonic %
    weight: { type: Number, default: 0 },          // Load cell kg
    temperature: { type: Number, default: 0 },     // °C
    humidity: { type: Number, default: 0 },        // %
    gasLevel: { type: Number, default: 0 },        // ppm
    irInsertions: { type: Number, default: 0 },    // IR count
  },
  aiClassification: {
    wasteType: { type: String, enum: ['Biodegradable','Recyclable','Hazardous','Unknown'] },
    confidence: Number,
    lastUpdated: Date,
  },
  status: { type: String, enum: ['good','moderate','critical'], default: 'good' },
  lastCollection: Date,
  isActive: { type: Boolean, default: true },
}, { timestamps: true });

const TruckSchema = new mongoose.Schema({
  truckId: String,
  driver: String,
  location: { lat: Number, lng: Number },
  status: { type: String, enum: ['idle','en-route','collecting','returning'] },
  fuel: Number,
  route: String,
  binsCollected: { type: Number, default: 0 },
}, { timestamps: true });

const AlertSchema = new mongoose.Schema({
  type: { type: String, enum: ['critical','warning','info'] },
  message: String,
  binId: String,
  resolved: { type: Boolean, default: false },
}, { timestamps: true });

const UserSchema = new mongoose.Schema({
  name: String,
  email: { type: String, unique: true },
  password: String,
  role: { type: String, enum: ['admin','citizen','worker'], default: 'citizen' },
  points: { type: Number, default: 0 },
  badges: [String],
  streak: { type: Number, default: 0 },
}, { timestamps: true });

const Bin = mongoose.model('Bin', BinSchema);
const Truck = mongoose.model('Truck', TruckSchema);
const Alert = mongoose.model('Alert', AlertSchema);
const User = mongoose.model('User', UserSchema);

// ─── MQTT Connection ──────────────────────
const mqttClient = mqtt.connect(process.env.MQTT_BROKER || 'mqtt://localhost:1883');

mqttClient.on('connect', () => {
  console.log('✅ MQTT Connected');
  mqttClient.subscribe('waste/bins/+/sensors');
  mqttClient.subscribe('waste/trucks/+/gps');
  mqttClient.subscribe('waste/ai/classification');
});

mqttClient.on('message', async (topic, payload) => {
  try {
    const data = JSON.parse(payload.toString());
    const parts = topic.split('/');

    if (parts[1] === 'bins' && parts[3] === 'sensors') {
      const binId = parts[2];
      const bin = await Bin.findOneAndUpdate(
        { binId },
        { sensors: data, status: computeStatus(data) },
        { new: true, upsert: true }
      );
      io.emit('bin:update', bin);

      // Auto-alert
      if (data.fillLevel >= 85) {
        const alert = await Alert.create({ type:'critical', message:`${binId}: Fill level ${data.fillLevel}%`, binId });
        io.emit('alert:new', alert);
      }
      if (data.gasLevel > 0.2) {
        const alert = await Alert.create({ type:'critical', message:`${binId}: Gas threshold exceeded ${data.gasLevel}ppm`, binId });
        io.emit('alert:new', alert);
      }
    }

    if (parts[1] === 'trucks' && parts[3] === 'gps') {
      const truckId = parts[2];
      const truck = await Truck.findOneAndUpdate({ truckId }, { location: data }, { new: true, upsert: true });
      io.emit('truck:update', truck);
    }

    if (topic === 'waste/ai/classification') {
      await Bin.findOneAndUpdate(
        { binId: data.binId },
        { aiClassification: { wasteType: data.type, confidence: data.confidence, lastUpdated: new Date() } }
      );
      io.emit('ai:classification', data);
    }
  } catch (err) {
    console.error('MQTT message error:', err);
  }
});

function computeStatus(sensors) {
  if (sensors.fillLevel >= 85 || sensors.gasLevel > 0.2) return 'critical';
  if (sensors.fillLevel >= 50 || sensors.gasLevel > 0.1) return 'moderate';
  return 'good';
}

// ─── Auth Middleware ──────────────────────
const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET || 'secret');
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// ─── REST API Routes ──────────────────────

// Auth
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user || user.password !== password) return res.status(401).json({ error: 'Invalid credentials' });
  const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET || 'secret', { expiresIn: '7d' });
  res.json({ token, user: { id: user._id, name: user.name, role: user.role } });
});

// Bins
app.get('/api/bins', authMiddleware, async (req, res) => {
  const bins = await Bin.find({ isActive: true });
  res.json(bins);
});

app.post('/api/bins', authMiddleware, async (req, res) => {
  const bin = await Bin.create(req.body);
  res.status(201).json(bin);
});

app.delete('/api/bins/:id', authMiddleware, async (req, res) => {
  await Bin.findByIdAndUpdate(req.params.id, { isActive: false });
  res.json({ success: true });
});

// Trucks
app.get('/api/trucks', authMiddleware, async (req, res) => {
  const trucks = await Truck.find();
  res.json(trucks);
});

// Alerts
app.get('/api/alerts', authMiddleware, async (req, res) => {
  const alerts = await Alert.find({ resolved: false }).sort('-createdAt').limit(50);
  res.json(alerts);
});

app.patch('/api/alerts/:id/resolve', authMiddleware, async (req, res) => {
  const alert = await Alert.findByIdAndUpdate(req.params.id, { resolved: true }, { new: true });
  res.json(alert);
});

// Analytics
app.get('/api/analytics/summary', authMiddleware, async (req, res) => {
  const totalBins = await Bin.countDocuments({ isActive: true });
  const criticalBins = await Bin.countDocuments({ status: 'critical', isActive: true });
  const allBins = await Bin.find({ isActive: true });
  const avgFill = allBins.reduce((s, b) => s + (b.sensors?.fillLevel || 0), 0) / (allBins.length || 1);
  res.json({ totalBins, criticalBins, avgFill: +avgFill.toFixed(1) });
});

// Leaderboard
app.get('/api/leaderboard', authMiddleware, async (req, res) => {
  const users = await User.find({ role: 'citizen' }).sort('-points').limit(10).select('name points badges streak');
  res.json(users);
});

// ─── WebSocket ─────────────────────────
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  socket.on('disconnect', () => console.log('Client disconnected:', socket.id));
});

// ─── Start Server ─────────────────────
const PORT = process.env.PORT || 4000;
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/waste_intelligence')
  .then(() => {
    server.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
  });
