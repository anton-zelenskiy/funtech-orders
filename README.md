# funtech-orders

Order management service on FastAPI (PostgreSQL, Redis, Kafka, taskiq).

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
# Create venv and install dependencies
uv sync

# With dev dependencies (pytest, etc.)
uv sync --group dev

# Run API locally
uv run uvicorn app.main:app --reload
```

Generate/update the lockfile for reproducible installs:

```bash
uv lock
```

## Docker

```bash
docker compose up --build
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs
