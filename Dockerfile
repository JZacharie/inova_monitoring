# ─── Stage 1: dependency installer ───────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Copy dependency manifests first (cache layer)
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install runtime deps only (no dev) into /app/.venv
RUN uv sync --no-dev --frozen 2>/dev/null || uv sync --no-dev

# ─── Stage 2: production image ────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runner

# Create non-root user
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/sh -m appuser

WORKDIR /app

# Copy installed venv and source code from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/src /app/src

# Copy static assets and templates (needed at runtime)
COPY --chown=appuser:appuser src/inova_monitoring/templates /app/src/inova_monitoring/templates
COPY --chown=appuser:appuser src/inova_monitoring/static    /app/src/inova_monitoring/static

# activate venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "inova_monitoring.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
