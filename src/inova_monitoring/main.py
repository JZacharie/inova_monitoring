"""
FastAPI application — serves the dashboard and a WebSocket endpoint.

WebSocket message flow
    Client → { type: "query_request", payload: { sql: "..." } }
    Server → { type: "query_result",  payload: { columns, rows, row_count } }
    Server → { type: "query_error",   payload: { detail: "..." } }
    Server → { type: "welcome",       payload: { message, version } }
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import execute_query
from .messages import (
    AnalyticsRequest,
    ErrorPayload,
    QueryError,
    QueryRequest,
    QueryResult,
    QueryResultPayload,
    WelcomeMessage,
    WelcomePayload,
)

app = FastAPI(title="Inova Monitoring", version="0.1.0")

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    """Render the monitoring dashboard."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Inova Apps Monitoring"},
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    Persistent WebSocket endpoint.

    Message protocol (hexagonal envelopes):
      IN  → QueryRequest
      OUT → WelcomeMessage | QueryResult | QueryError
    """
    await websocket.accept()

    # Greet the client
    welcome = WelcomeMessage(
        payload=WelcomePayload(message="Connected to Inova Monitoring")
    )
    await websocket.send_text(welcome.model_dump_json())

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
                # Dispatch based on type
                msg_type = data.get("type")
                if msg_type == "query_request":
                    query_msg = QueryRequest.model_validate(data)
                    sql = query_msg.payload.sql
                elif msg_type == "analytics_request":
                    analytics_msg = AnalyticsRequest.model_validate(data)
                    # Map metric names to materialized views
                    metric_map = {
                        "daily_users": "SELECT * FROM daily_unique_users",
                        "duration_stats": "SELECT * FROM session_duration_stats",
                        "long_sessions": "SELECT * FROM top_long_sessions",
                        "reconnect_loops": "SELECT * FROM reconnect_loops",
                    }
                    metric = analytics_msg.payload.metric
                    sql = metric_map[metric]
                else:
                    raise ValueError(f"Unknown message type: {msg_type}")

            except Exception as parse_err:
                error = QueryError(
                    payload=ErrorPayload(detail=f"Invalid message: {parse_err}")
                )
                await websocket.send_text(error.model_dump_json())
                continue

            # Execute the SQL query
            try:
                rows = execute_query(sql)
                columns = list(rows[0].keys()) if rows else []
                result = QueryResult(
                    payload=QueryResultPayload(
                        columns=columns,
                        rows=rows,
                        row_count=len(rows),
                    )
                )
                await websocket.send_text(result.model_dump_json())
            except Exception as db_err:
                error = QueryError(payload=ErrorPayload(detail=str(db_err)))
                await websocket.send_text(error.model_dump_json())

    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
