"""
Hexagonal message envelopes for WebSocket communication.

Inbound  (Frontend → Backend): QueryRequest
Outbound (Backend → Frontend): WelcomeMessage | QueryResult | QueryError
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Shared payload types
# ---------------------------------------------------------------------------

class QueryPayload(BaseModel):
    sql: str


class QueryResultPayload(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int


class ErrorPayload(BaseModel):
    detail: str


class WelcomePayload(BaseModel):
    message: str
    version: str = "0.1.0"


# ---------------------------------------------------------------------------
# Inbound messages  (Frontend → Backend)
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    type: Literal["query_request"] = "query_request"
    payload: QueryPayload


# ---------------------------------------------------------------------------
# Outbound messages  (Backend → Frontend)
# ---------------------------------------------------------------------------

class WelcomeMessage(BaseModel):
    type: Literal["welcome"] = "welcome"
    payload: WelcomePayload


class QueryResult(BaseModel):
    type: Literal["query_result"] = "query_result"
    payload: QueryResultPayload


class QueryError(BaseModel):
    type: Literal["query_error"] = "query_error"
    payload: ErrorPayload


# Union helpers for dispatch
InboundMessage = QueryRequest
OutboundMessage = WelcomeMessage | QueryResult | QueryError
