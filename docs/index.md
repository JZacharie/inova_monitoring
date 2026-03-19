# Inova Monitoring — Documentation

**Inova Monitoring** is a lightweight Python platform for monitoring Inova Apps instances in real-time.

## ✨ Features

- **PostgreSQL Query Interface** — Run any SQL query and see results appear live in a dynamic table.
- **Real-time WebSocket Communication** — Persistent connection with typed hexagonal message envelopes.
- **Prometheus Metrics Integration** — Visualize metrics from any Prometheus endpoint.
- **SSO Authentication** — OAuth2/OIDC-ready access control.
- **Environment-based Configuration** — All settings managed via `.env`.

## 🚀 Quick Start

```bash
# Clone & install
git clone git@github.com:JZacharie/inova_monitoring.git
cd inova_monitoring
uv sync --all-extras --dev

# Configure
cp .env.example .env

# Run
uv run uvicorn src.inova_monitoring.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) to access the dashboard.
