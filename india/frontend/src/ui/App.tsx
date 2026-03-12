import { useEffect, useMemo, useState } from "react";

type Bin = { id: string; name?: string | null; lat: number; lng: number };
type Reading = {
  id: number;
  bin_id: string;
  ts: string;
  fill_level_pct: number;
  weight_kg: number;
  gas_ppm: number;
  temperature_c: number;
  humidity_pct: number;
};
type Alert = { id: number; bin_id: string; type: string; message: string; created_at: string; active: number };
type TruckLocation = { id: number; truck_id: string; ts: string; lat: number; lng: number; status: string };

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function apiGet<T>(path: string): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`);
  if (!r.ok) throw new Error(`GET ${path} failed: ${r.status}`);
  return (await r.json()) as T;
}

export function App() {
  const [bins, setBins] = useState<Bin[]>([]);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [trucks, setTrucks] = useState<TruckLocation[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    const tick = async () => {
      try {
        const [b, r, a, t] = await Promise.all([
          apiGet<Bin[]>("/bins"),
          apiGet<Reading[]>("/telemetry/latest?limit=200"),
          apiGet<Alert[]>("/alerts?active=1&limit=200"),
          apiGet<TruckLocation[]>("/trucks/locations?limit=50"),
        ]);
        if (!alive) return;
        setBins(b);
        setReadings(r);
        setAlerts(a);
        setTrucks(t);
        setErr(null);
      } catch (e: any) {
        if (!alive) return;
        setErr(e?.message ?? String(e));
      }
    };
    tick();
    const id = window.setInterval(tick, 3000);
    return () => {
      alive = false;
      window.clearInterval(id);
    };
  }, []);

  const latestByBin = useMemo(() => {
    const m = new Map<string, Reading>();
    for (const r of readings) {
      if (!m.has(r.bin_id)) m.set(r.bin_id, r);
    }
    return m;
  }, [readings]);

  return (
    <div className="page">
      <header className="header">
        <div>
          <div className="title">Smart Waste Management Dashboard</div>
          <div className="subtitle">MQTT telemetry → FastAPI → Postgres → React</div>
        </div>
        <div className="pill">API: {API_BASE}</div>
      </header>

      {err ? <div className="error">Error: {err}</div> : null}

      <div className="grid">
        <section className="card">
          <h2>Bins (latest)</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Bin</th>
                <th>Fill %</th>
                <th>Weight (kg)</th>
                <th>Gas (ppm)</th>
                <th>Temp (°C)</th>
                <th>Humidity %</th>
                <th>Last update</th>
              </tr>
            </thead>
            <tbody>
              {bins.map((b) => {
                const r = latestByBin.get(b.id);
                const fill = r?.fill_level_pct ?? 0;
                return (
                  <tr key={b.id}>
                    <td>
                      <div className="binName">{b.name || b.id}</div>
                      <div className="muted">
                        {b.lat.toFixed(4)}, {b.lng.toFixed(4)}
                      </div>
                    </td>
                    <td>
                      <div className="bar">
                        <div className="barFill" style={{ width: `${Math.min(100, Math.max(0, fill))}%` }} />
                      </div>
                      <div className="mono">{fill.toFixed(1)}</div>
                    </td>
                    <td className="mono">{(r?.weight_kg ?? 0).toFixed(2)}</td>
                    <td className="mono">{(r?.gas_ppm ?? 0).toFixed(0)}</td>
                    <td className="mono">{(r?.temperature_c ?? 0).toFixed(1)}</td>
                    <td className="mono">{(r?.humidity_pct ?? 0).toFixed(0)}</td>
                    <td className="mono">{r ? new Date(r.ts).toLocaleTimeString() : "-"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </section>

        <section className="card">
          <h2>Active alerts</h2>
          {alerts.length === 0 ? (
            <div className="muted">No active alerts.</div>
          ) : (
            <ul className="alerts">
              {alerts.map((a) => (
                <li key={a.id} className="alert">
                  <div className="alertTitle">
                    {a.type} • {a.bin_id}
                  </div>
                  <div className="muted">{a.message}</div>
                  <div className="muted mono">{new Date(a.created_at).toLocaleString()}</div>
                </li>
              ))}
            </ul>
          )}

          <div style={{ height: 12 }} />

          <h2>Truck locations (latest)</h2>
          {trucks.length === 0 ? (
            <div className="muted">No truck updates yet.</div>
          ) : (
            <ul className="alerts">
              {trucks.map((t) => (
                <li key={t.id} className="alert" style={{ borderColor: "rgba(45,212,191,0.35)", background: "rgba(45,212,191,0.07)" }}>
                  <div className="alertTitle">
                    {t.truck_id} • {t.status}
                  </div>
                  <div className="muted">
                    {t.lat.toFixed(4)}, {t.lng.toFixed(4)}
                  </div>
                  <div className="muted mono">{new Date(t.ts).toLocaleString()}</div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}

