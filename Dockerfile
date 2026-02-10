FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN --mount=type=cache,target=/root/.cache/uv uv sync --no-dev --no-install-project

COPY . .
RUN chmod -R 755 /opt/venv

ENV PYTHONPATH=/app
ENV PATH="/opt/venv/bin:$PATH"
