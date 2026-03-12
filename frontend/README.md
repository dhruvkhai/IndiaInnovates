# Frontend Dashboard (React)

Minimal dashboard:

- Bins table (latest readings)
- Alerts list

## Run (Docker)

From repo root:

```bash
docker compose up --build frontend
```

## Run (local)

```bash
cd frontend
npm install
npm run dev
```

Env:
- `VITE_API_BASE_URL` (defaults to `http://localhost:8000`)

