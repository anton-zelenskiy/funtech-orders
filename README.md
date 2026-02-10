# funtech-orders

Order management service on FastAPI (PostgreSQL, Redis, Kafka, taskiq).

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Build and run containers
docker compose up -d --build

# Apply migrations
docker compose exec api alembic upgrade head
```

### Done! You can start making api requests in [API docs](http://localhost:8000/docs)
