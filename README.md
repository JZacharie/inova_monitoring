# Inova Monitoring

A Python-based monitoring platform for **Inova Apps** instances. It provides real-time visibility into your PostgreSQL database, Prometheus metrics, and application health — all through a modern, secure web interface.

---

## ✨ Capabilities

### 🔍 PostgreSQL Query Interface
Execute any SQL query directly from the browser. Results stream back in real-time over a **WebSocket** connection and are displayed in a dynamic, animated table — no page refresh required.

### ⚡ Real-time WebSocket Communication
The frontend maintains a persistent WebSocket connection to the backend. Communication uses a typed **hexagonal message protocol**:

| Message | Direction | Description |
|---|---|---|
| `welcome` | Server → Client | Sent on connect, includes server version |
| `query_request` | Client → Server | Contains the SQL to execute |
| `query_result` | Server → Client | Columns + rows of the result set |
| `query_error` | Server → Client | Error detail if the query failed |

The WebSocket automatically reconnects on disconnection.

### 📊 Prometheus Metrics Integration
Fetch and visualize metrics from any Prometheus endpoint configured via environment variables.

### 🔐 SSO Authentication
The interface is designed to integrate with SSO providers (OAuth2/OIDC) via configurable environment variables (`SSO_CLIENT_ID`, `SSO_AUTH_URL`, etc.).

### ⚙️ Environment-based Configuration
All settings are managed through environment variables or a local `.env` file. Copy `.env.example` to `.env` and fill in your values — no code changes required.

---

## 🚀 Quick Start

### 1. Clone & install dependencies

```bash
git clone git@github.com:JZacharie/inova_monitoring.git
cd inova_monitoring
uv sync --all-extras --dev
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials and other settings
```

### 3. Run

```bash
uv run uvicorn src.inova_monitoring.main:app --reload
```

Then open [http://localhost:8000](http://localhost:8000).

---

## 🗂️ Project Structure

```
src/inova_monitoring/
├── main.py         # FastAPI app + WebSocket endpoint
├── database.py     # SQLAlchemy connection + query execution
├── messages.py     # Hexagonal WebSocket message envelopes (Pydantic)
├── config.py       # Pydantic-Settings environment configuration
├── templates/      # Jinja2 HTML templates
└── static/         # CSS and assets
```

---

## 🧪 Development

```bash
uv run ruff check .         # Lint
uv run mypy .               # Type check
uv run pytest               # Tests
uv run mkdocs serve         # Live documentation preview
```

---

## 📚 Documentation

Full documentation is auto-generated and published to GitHub Pages on every push to `main`. Run locally with:

```bash
uv run mkdocs serve
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_HOST` | `localhost` | PostgreSQL server host |
| `POSTGRES_PORT` | `5432` | PostgreSQL server port |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `password` | Database password |
| `POSTGRES_DB` | `inova_monitoring` | Target database |
| `PROMETHEUS_URL` | `http://localhost:9090` | Prometheus base URL |
| `SSO_CLIENT_ID` | *(none)* | OAuth2 / OIDC client ID |
| `SSO_CLIENT_SECRET` | *(none)* | OAuth2 / OIDC client secret |
| `SSO_AUTH_URL` | *(none)* | Authorization endpoint |
| `SSO_TOKEN_URL` | *(none)* | Token endpoint |
| `DEBUG` | `true` | Enable debug mode |
| `API_SECRET_KEY` | *(change me)* | Secret key for signing sessions |
