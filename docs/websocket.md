# WebSocket Protocol

The backend exposes a single WebSocket endpoint at `/ws`. Communication uses typed, self-describing JSON message envelopes.

## Inbound Messages (Client → Server)

### `query_request`
Execute an SQL query.

```json
{
  "type": "query_request",
  "payload": {
    "sql": "SELECT * FROM users LIMIT 10"
  }
}
```

## Outbound Messages (Server → Client)

### `welcome`
Sent immediately on connection.

```json
{
  "type": "welcome",
  "payload": {
    "message": "Connected to Inova Monitoring",
    "version": "0.1.0"
  }
}
```

### `query_result`
Successful query result.

```json
{
  "type": "query_result",
  "payload": {
    "columns": ["id", "name", "email"],
    "rows": [
      { "id": 1, "name": "Alice", "email": "alice@example.com" }
    ],
    "row_count": 1
  }
}
```

### `query_error`
Sent when a query fails (parse error or database error).

```json
{
  "type": "query_error",
  "payload": {
    "detail": "relation \"missing_table\" does not exist"
  }
}
```

## Connection Lifecycle

1. Client connects → Server sends `welcome`.
2. Client sends `query_request` → Server responds with `query_result` or `query_error`.
3. If the connection drops, the client automatically reconnects after 3 seconds.
