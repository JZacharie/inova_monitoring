# Configuration

All configuration is managed via environment variables. Copy `.env.example` to `.env` and set the values.

## PostgreSQL

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_HOST` | `localhost` | Server host |
| `POSTGRES_PORT` | `5432` | Server port |
| `POSTGRES_USER` | `postgres` | Username |
| `POSTGRES_PASSWORD` | `password` | Password |
| `POSTGRES_DB` | `inova_monitoring` | Database name |

## Prometheus

| Variable | Default | Description |
|---|---|---|
| `PROMETHEUS_URL` | `http://localhost:9090` | Base URL for metrics |

## SSO (OAuth2 / OIDC)

| Variable | Description |
|---|---|
| `SSO_CLIENT_ID` | Application client ID |
| `SSO_CLIENT_SECRET` | Application client secret |
| `SSO_AUTH_URL` | Authorization endpoint URL |
| `SSO_TOKEN_URL` | Token endpoint URL |

## Application

| Variable | Default | Description |
|---|---|---|
| `DEBUG` | `true` | Enable debug mode |
| `API_SECRET_KEY` | *(change me)* | Session signing key |
