"""
FastAPI application — serves the dashboard and a WebSocket endpoint.

WebSocket message flow
    Client → { type: "query_request", payload: { sql: "..." } }
    Server → { type: "query_result",  payload: { columns, rows, row_count } }
    Server → { type: "query_error",   payload: { detail: "..." } }
    Server → { type: "welcome",       payload: { message, version } }
"""

from __future__ import annotations

from typing import Any

import json
from pathlib import Path

import os

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

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

# Session Middleware is required for Authlib OAuth
app.add_middleware(
    SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "inova_super_secret_dev_key")
)

# OAuth Configuration
oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.getenv("GOOGLE_CLIENT_ID", "dummy_client_id_for_dev"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", "dummy_client_secret_for_dev"),
    client_kwargs={"scope": "openid email profile"},
)

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def get_current_user(request: Request) -> Any:
    """Helper to get authentication user from session."""
    return request.session.get("user")


@app.get("/login")
async def login(request: Request):
    """Initiate Google OAuth login."""
    user = get_current_user(request)
    if user:
        return RedirectResponse("/")
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, str(redirect_uri))


@app.get("/auth")
async def auth(request: Request):
    """Callback for Google OAuth."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f"<h1>OAuth Error</h1><p>{error.error}</p>")

    user = token.get("userinfo")
    if user:
        request.session["user"] = dict(user)
    return RedirectResponse("/")


@app.get("/logout")
async def logout(request: Request):
    """Logout current user."""
    request.session.pop("user", None)
    return RedirectResponse("/")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the monitoring dashboard."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Inova Apps Monitoring", "user": user},
    )


@app.get("/users", response_class=HTMLResponse)
async def read_users(request: Request):
    """Render the user activity & profiling page."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={"title": "User Activity & Profiling", "user": user},
    )


@app.get("/reports", response_class=HTMLResponse)
async def read_reports(request: Request):
    """Render the reports page."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={"title": "Reports", "user": user},
    )


@app.get("/logs", response_class=HTMLResponse)
async def read_logs(request: Request):
    """Render the current system logs page."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        request=request,
        name="logs.html",
        context={"title": "Logs", "user": user},
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
