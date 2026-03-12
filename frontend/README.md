# 🌿 AI-Driven Circular Waste Intelligence System

A production-ready smart city IoT dashboard for intelligent waste management.

## 📁 Project Structure

```
waste-intelligence/
├── index.html                    ← Main dashboard (open this)
├── README.md
├── src/
│   ├── data/
│   │   └── mockData.js          ← IoT sensor mock data
│   ├── components/
│   │   ├── dashboard/           ← Overview components
│   │   ├── bins/                ← Bin monitoring
│   │   ├── map/                 ← Fleet GPS map
│   │   ├── charts/              ← Chart components
│   │   ├── analytics/           ← AI analytics
│   │   ├── alerts/              ← Notification panel
│   │   ├── gamification/        ← Incentive system
│   │   └── admin/               ← Admin panel
│   ├── pages/                   ← Page-level components
│   ├── hooks/                   ← Custom React hooks
│   ├── utils/                   ← Helper functions
│   └── styles/                  ← Global styles
└── public/                      ← Static assets
```

## 🚀 Dashboard Pages

| Page | Description |
|------|-------------|
| 📊 Overview | KPI cards, weekly charts, live map, alerts |
| 🗑️ Bin Monitor | 6 smart bins with real-time IoT sensor data |
| 🗺️ Fleet Map | GPS truck tracking with route visualization |
| 🤖 AI Analytics | Classification stats, confidence scores |
| 🌡️ Environment | Temp, humidity, gas detection trends |
| 🏆 Incentives | Leaderboard, badges, citizen gamification |
| ⚙️ Admin | Bin/fleet management, sensor config |

## 🛠️ Tech Stack (Production)

**Frontend**
- React.js / Next.js
- TailwindCSS
- Chart.js / Recharts
- ShadCN UI

**Backend**
- Node.js + Express
- REST API + WebSocket
- JWT Authentication

**IoT**
- MQTT (Mosquitto/EMQX)
- Sensors: Ultrasonic, Load Cell, IR, Camera, Gas, GPS

**Database**
- MongoDB / PostgreSQL

**Deployment**
- Docker + Docker Compose
- Nginx reverse proxy

## 📡 IoT Data Flow

```
IoT Sensors → MQTT Broker → Node.js Backend → MongoDB → Dashboard (WebSocket)
                                     ↓
                              AI Classification API
```

## 🎨 Design System

- **Theme**: Dark eco-green glassmorphism
- **Fonts**: Syne (display) + Space Mono (data) + JetBrains Mono (code)
- **Colors**: #00ff88 (eco green), #00d4ff (cyan), #ff4757 (red alert), #ffb830 (amber)
- **Grid**: 40px dot grid background

## ⚡ Live Features

- Real-time bin fill level updates (every 3s)
- Animated circular progress rings
- GPS truck tracking map with route lines
- AI confidence score displays
- Alert notification drawer
- Environmental sensor monitoring
- Citizen leaderboard & gamification

## 🐳 Docker Deployment

```bash
docker-compose up -d
```

Services: frontend (3000), backend (4000), mongodb (27017), mqtt (1883)
