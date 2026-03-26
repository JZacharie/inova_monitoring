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

import httpx
import json
from pathlib import Path

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .database import execute_query
from .prometheus import metrics_fetcher
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
app.add_middleware(SessionMiddleware, secret_key=settings.api_secret_key)

# OAuth Configuration
oauth = OAuth()

# Google Registration
if settings.google_client_id and settings.google_client_secret:
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        client_kwargs={"scope": "openid email profile"},
    )

# GitHub Registration
if settings.github_client_id and settings.github_client_secret:
    oauth.register(
        name="github",
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
        access_token_url="https://github.com/login/oauth/access_token",
        access_token_params=None,
        authorize_url="https://github.com/login/oauth/authorize",
        authorize_params=None,
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )

# Microsoft Entra ID Registration
if (
    settings.entra_id_client_id
    and settings.entra_id_client_secret
    and settings.entra_id_tenant_id
):
    oauth.register(
        name="entra",
        server_metadata_url=f"https://login.microsoftonline.com/{settings.entra_id_tenant_id}/v2.0/.well-known/openid-configuration",
        client_id=settings.entra_id_client_id,
        client_secret=settings.entra_id_client_secret,
        client_kwargs={"scope": "openid email profile"},
    )

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def get_current_user(request: Request) -> Any:
    """Helper to get authentication user from session."""
    return request.session.get("user")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str | None = None):
    """Render the multi-method login page."""
    user = get_current_user(request)
    if user:
        return RedirectResponse("/")

    # Filter allowed methods based on configuration
    allowed = settings.auth_methods_allowed.split(",")
    methods = [m.strip().lower() for m in allowed]

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"methods": methods, "error": error},
    )


@app.post("/login")
async def login_basic(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    """Handle Basic Auth from the login form by checking the database."""
    if not settings.enable_basic_auth:
        return await login_page(request, error="Basic Auth is disabled")

    # Check database for user - in a real app, use password hashing!
    # The 'username' field in the form corresponds to 'email' in the database
    query = "SELECT * FROM users WHERE email = :email AND hashed_password = :password"
    params = {"email": username, "password": password}
    try:
        results = execute_query(query, params)
        if results:
            user = results[0]
            request.session["user"] = {
                "name": user["full_name"],
                "email": user["email"],
                "picture": user["picture_url"],
            }
            # Update last login
            execute_query(
                "UPDATE users SET last_login = NOW() WHERE id = :id", {"id": user["id"]}
            )
            return RedirectResponse("/", status_code=303)
    except Exception:
        # Fallback to hardcoded admin if database is not reachable/ready
        if username == "admin" and password == "admin":
            request.session["user"] = {
                "name": "Administrator",
                "email": "admin@inova.local",
                "picture": None,
            }
            return RedirectResponse("/", status_code=303)

    return await login_page(request, error="Invalid credentials")


@app.get("/login/{provider}")
async def login_oauth(request: Request, provider: str):
    """Initiate OAuth login for a specific provider."""
    client = getattr(oauth, provider, None)
    if not client:
        return await login_page(request, error=f"Provider {provider} not configured")

    redirect_uri = request.url_for("auth_callback", provider=provider)
    return await client.authorize_redirect(request, str(redirect_uri))


@app.get("/auth/{provider}")
async def auth_callback(request: Request, provider: str):
    """Handle OAuth callback for a specific provider."""
    client = getattr(oauth, provider, None)
    if not client:
        return await login_page(request, error="Provider not found")

    try:
        token = await client.authorize_access_token(request)
    except OAuthError as error:
        return await login_page(request, error=f"Auth Error: {error.error}")

    # Extract user info based on provider
    user_info = None
    if provider == "google" or provider == "entra":
        user_info = token.get("userinfo")
    elif provider == "github":
        resp = await client.get("user", token=token)
        user_info = resp.json()

    if user_info:
        # Normalize/Map the user info to our database
        email = user_info.get("email")
        if not email:
            # Fallback for GitHub if email is not in the top-level
            if provider == "github":
                resp = await client.get("user/emails", token=token)
                emails = resp.json()
                primary_email = next((e["email"] for e in emails if e["primary"]), None)
                email = primary_email or emails[0]["email"]

        name = user_info.get("name") or user_info.get("login")
        picture = user_info.get("picture") or user_info.get("avatar_url")
        provider_id = str(user_info.get("sub") or user_info.get("id"))

        # Map/Upsert user in database
        try:
            # Attempt to find by email (as per mapping requirements)
            query_find = "SELECT * FROM users WHERE email = :email"
            existing = execute_query(query_find, {"email": email})
            if existing:
                # Update existing user (Basic or other SSO)
                update_query = """
                    UPDATE users
                    SET full_name = :name, picture_url = :picture,
                        provider = :provider, provider_id = :provider_id,
                        last_login = NOW()
                    WHERE email = :email
                """
                execute_query(
                    update_query,
                    {
                        "name": name,
                        "picture": picture,
                        "provider": provider,
                        "provider_id": provider_id,
                        "email": email,
                    },
                )
            else:
                # Insert new user
                insert_query = """
                    INSERT INTO users (email, full_name, picture_url, provider, provider_id, last_login)
                    VALUES (:email, :name, :picture, :provider, :provider_id, NOW())
                """
                execute_query(
                    insert_query,
                    {
                        "email": email,
                        "name": name,
                        "picture": picture,
                        "provider": provider,
                        "provider_id": provider_id,
                    },
                )
        except Exception:
            # Continue even if DB mapping fails (optional: log error)
            pass

        request.session["user"] = {
            "name": name,
            "email": email,
            "picture": picture,
        }

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
    section = request.query_params.get("section", "dashboard")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Inova Apps Monitoring", 
            "user": user, 
            "active_page": "dashboard",
            "section": section
        },
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
        context={"title": "User Activity & Profiling", "user": user, "active_page": "users"},
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
        context={"title": "Reports", "user": user, "active_page": "reports"},
    )


@app.get("/catalog", response_class=HTMLResponse)
async def read_catalog(request: Request):
    """Render the Service Catalog & Instance Dashboard."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context={"title": "Service Catalog", "user": user, "active_page": "catalog"},
    )


@app.get("/api/catalog/instances")
async def get_instances(request: Request):
    """API endpoint to fetch all monitored instances."""
    user = get_current_user(request)
    if not user:
        return {"detail": "Unauthorized"}

    try:
        # Fetch instances from database
        query = "SELECT * FROM instances ORDER BY name ASC"
        rows = execute_query(query)
        return rows
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/catalog/instances/{instance_id}/status")
async def get_instance_status(instance_id: int):
    """Fetch real-time status for an instance from ArgoCD."""
    try:
        query = "SELECT argocd_app_name FROM instances WHERE id = :id"
        result = execute_query(query, {"id": instance_id})
        if not result:
            return {"error": "Instance not found"}

        app_name = result[0]["argocd_app_name"]
        if not app_name:
            return {"status": "unknown", "message": "No ArgoCD app configured"}

        # If token is not set, return a mock status for demonstration
        if not settings.argocd_token:
            import random

            statuses = ["Synced", "OutOfSync"]
            healths = ["Healthy", "Degraded", "Progressing"]
            return {
                "sync_status": random.choice(statuses),
                "health_status": random.choice(healths),
                "repo_url": "https://github.com/JZacharie/inova_monitoring",
                "rev": "v3.4.5",
            }

        # Real API call to ArgoCD
        async with httpx.AsyncClient(verify=settings.argocd_verify_ssl) as client:
            headers = {"Authorization": f"Bearer {settings.argocd_token}"}
            url = f"{settings.argocd_url}/api/v1/applications/{app_name}"
            resp = await client.get(url, headers=headers)

            if resp.status_code == 200:
                data = resp.json()
                return {
                    "sync_status": data.get("status", {}).get("sync", {}).get("status"),
                    "health_status": data.get("status", {})
                    .get("health", {})
                    .get("status"),
                    "repo_url": data.get("spec", {}).get("source", {}).get("repoURL"),
                    "rev": data.get("status", {}).get("sync", {}).get("revision"),
                }
            else:
                return {
                    "error": f"ArgoCD API Error: {resp.status_code}",
                    "detail": resp.text,
                }

    except Exception as e:
        return {"error": str(e)}


@app.get("/logs", response_class=HTMLResponse)
async def read_logs(request: Request):
    """Render the current system logs page."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        request=request,
        name="logs.html",
        context={"title": "Logs", "user": user, "active_page": "logs"},
    )


@app.get("/api/metrics")
async def get_metrics(request: Request):
    """Fetch and return Prometheus metrics for allowed endpoints."""
    user = get_current_user(request)
    if not user:
        return {"detail": "Unauthorized"}

    metrics = await metrics_fetcher.fetch_metrics()
    return metrics


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
