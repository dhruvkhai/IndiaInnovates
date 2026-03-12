export const bins = [
  { id: "BIN-001", location: "MG Road", lat: 19.076, lng: 72.877, fill: 87, weight: 42.3, temp: 34, humidity: 68, gas: 0.12, status: "critical", type: "Recyclable", confidence: 94, insertions: 23, lastCollection: "2h ago" },
  { id: "BIN-002", location: "Bandra West", lat: 19.059, lng: 72.836, fill: 54, weight: 28.1, temp: 31, humidity: 62, gas: 0.04, status: "moderate", type: "Biodegradable", confidence: 88, insertions: 15, lastCollection: "5h ago" },
  { id: "BIN-003", location: "Andheri East", lat: 19.115, lng: 72.868, fill: 23, weight: 11.7, temp: 30, humidity: 55, gas: 0.02, status: "good", type: "Recyclable", confidence: 91, insertions: 8, lastCollection: "1h ago" },
  { id: "BIN-004", location: "Dadar", lat: 19.018, lng: 72.843, fill: 95, weight: 48.6, temp: 38, humidity: 74, gas: 0.28, status: "critical", type: "Hazardous", confidence: 97, insertions: 31, lastCollection: "8h ago" },
  { id: "BIN-005", location: "Kurla", lat: 19.072, lng: 72.888, fill: 71, weight: 36.2, temp: 33, humidity: 65, gas: 0.09, status: "moderate", type: "Biodegradable", confidence: 85, insertions: 19, lastCollection: "3h ago" },
  { id: "BIN-006", location: "Colaba", lat: 18.906, lng: 72.814, fill: 38, weight: 19.4, temp: 29, humidity: 58, gas: 0.03, status: "good", type: "Recyclable", confidence: 92, insertions: 11, lastCollection: "2h ago" },
];

export const trucks = [
  { id: "TRK-01", driver: "Rajesh Kumar", lat: 19.082, lng: 72.862, status: "en-route", fuel: 68, speed: 32, collected: 4, route: "North Zone" },
  { id: "TRK-02", driver: "Priya Sharma", lat: 19.045, lng: 72.855, status: "collecting", fuel: 45, speed: 0, collected: 7, route: "South Zone" },
  { id: "TRK-03", driver: "Amit Patel", lat: 19.098, lng: 72.876, status: "returning", fuel: 22, speed: 48, collected: 12, route: "East Zone" },
];

export const weeklyData = [
  { day: "Mon", biodegradable: 420, recyclable: 310, hazardous: 45 },
  { day: "Tue", biodegradable: 380, recyclable: 290, hazardous: 32 },
  { day: "Wed", biodegradable: 510, recyclable: 380, hazardous: 58 },
  { day: "Thu", biodegradable: 460, recyclable: 340, hazardous: 41 },
  { day: "Fri", biodegradable: 540, recyclable: 410, hazardous: 63 },
  { day: "Sat", biodegradable: 620, recyclable: 490, hazardous: 78 },
  { day: "Sun", biodegradable: 350, recyclable: 260, hazardous: 29 },
];

export const envHistory = Array.from({ length: 24 }, (_, i) => ({
  time: `${String(i).padStart(2, "0")}:00`,
  temp: 28 + Math.sin(i * 0.3) * 6 + Math.random() * 2,
  humidity: 60 + Math.cos(i * 0.2) * 12 + Math.random() * 3,
  gas: 0.05 + Math.random() * 0.15,
}));

export const leaderboard = [
  { rank: 1, name: "Sunita M.", points: 4820, badge: "♻️ Eco Champion", streak: 45 },
  { rank: 2, name: "Rohan T.", points: 4310, badge: "🌿 Green Star", streak: 38 },
  { rank: 3, name: "Kavya R.", points: 3980, badge: "🌱 Earth Saver", streak: 31 },
  { rank: 4, name: "Arjun S.", points: 3450, badge: "💚 Recycler", streak: 27 },
  { rank: 5, name: "Meena P.", points: 2980, badge: "🔄 Sorter", streak: 22 },
];

export const alerts = [
  { id: 1, type: "critical", message: "BIN-004 at Dadar: Hazardous waste detected!", time: "2 min ago", icon: "⚠️" },
  { id: 2, type: "critical", message: "BIN-001 at MG Road: Fill level 87% — Schedule pickup", time: "8 min ago", icon: "🗑️" },
  { id: 3, type: "warning", message: "BIN-004: Gas threshold exceeded (0.28 ppm)", time: "15 min ago", icon: "💨" },
  { id: 4, type: "info", message: "TRK-03 completed East Zone route — 12 bins collected", time: "32 min ago", icon: "🚛" },
  { id: 5, type: "info", message: "AI Model updated: +2.3% classification accuracy", time: "1h ago", icon: "🤖" },
];

export const kpis = {
  totalCollected: "2,847 kg",
  avgFillTime: "4.2 hrs",
  efficiency: "91.3%",
  accuracy: "93.7%",
  activeBins: 6,
  activeRoutes: 3,
  co2Saved: "142 kg",
  recycled: "68%",
};
