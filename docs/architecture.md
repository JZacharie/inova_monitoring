# Architecture

Inova Monitoring follows the **Hexagonal Architecture** pattern (Ports & Adapters) to keep the domain logic independent of infrastructure concerns.

## Layers

```
Browser (WebSocket Client)
        │   WebSocket /ws
        ▼
FastAPI (main.py)          ← Interface Layer
        │
        ▼
messages.py                ← Port: typed envelopes (Pydantic)
   QueryRequest / QueryResult / QueryError / WelcomeMessage
        │
        ▼
database.py                ← Adapter: SQLAlchemy → PostgreSQL
        │
        ▼
PostgreSQL                 ← Infrastructure
```

## WebSocket Message Flow

```
Client  →  { "type": "query_request", "payload": { "sql": "SELECT ..." } }
Server  →  { "type": "query_result",  "payload": { "columns": [...], "rows": [...], "row_count": N } }
Server  →  { "type": "query_error",   "payload": { "detail": "..." } }
Server  →  { "type": "welcome",       "payload": { "message": "...", "version": "0.1.0" } }
```

## File Structure

| File | Role |
|---|---|
| `main.py` | FastAPI app, WebSocket `/ws` endpoint |
| `messages.py` | Pydantic hexagonal message envelopes |
| `database.py` | SQLAlchemy engine, raw query execution |
| `config.py` | Pydantic-Settings, loads from `.env` |
| `templates/index.html` | Dashboard HTML + WS client JS |
| `static/style.css` | Glassmorphism dark-mode CSS |
