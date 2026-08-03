# Stockroom API

A warehouse inventory management REST API built with Python 3.12 and FastAPI. Manages categories, products, and stock movements backed by PostgreSQL.

## Environment Variables

| Variable       | Default                                                              | Description                          |
|----------------|----------------------------------------------------------------------|--------------------------------------|
| `DATABASE_URL` | `postgresql+asyncpg://stockroom:stockroom@localhost:5432/stockroom`  | Async PostgreSQL connection string   |
| `API_KEY`      | `demo-api-key`                                                       | Bearer token for all API requests    |

Copy `.env.example` to `.env` and adjust as needed.

## Running Locally

### With Docker Compose (recommended)

```yaml
# docker-compose.yml (create alongside the project)
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: stockroom
      POSTGRES_PASSWORD: stockroom
      POSTGRES_DB: stockroom
    ports:
      - "5432:5432"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://stockroom:stockroom@db:5432/stockroom
    depends_on:
      - db
```

```bash
docker compose up --build
```

### Direct (uvicorn)

```bash
pip install -e .
cp .env.example .env
uvicorn app.main:app --reload
```

## Running Migrations

```bash
# Apply all migrations
DATABASE_URL=postgresql+asyncpg://stockroom:stockroom@localhost:5432/stockroom \
  alembic upgrade head

# Generate a new migration after model changes
alembic revision --autogenerate -m "describe your change"
```

## API Endpoints

All endpoints require the header `X-Api-Key: <your api key>`.

Interactive docs available at `http://localhost:8000/docs`.

### Categories — `/api/v1/categories`

| Method   | Path                      | Description          |
|----------|---------------------------|----------------------|
| `GET`    | `/api/v1/categories`      | List all categories  |
| `POST`   | `/api/v1/categories`      | Create a category    |
| `GET`    | `/api/v1/categories/{id}` | Get a category       |
| `PUT`    | `/api/v1/categories/{id}` | Update a category    |
| `DELETE` | `/api/v1/categories/{id}` | Delete a category    |

### Products — `/api/v1/products`

| Method   | Path                    | Description                                     |
|----------|-------------------------|-------------------------------------------------|
| `GET`    | `/api/v1/products`      | List all products (optional `?category_id=`)    |
| `POST`   | `/api/v1/products`      | Create a product                                |
| `GET`    | `/api/v1/products/{id}` | Get a product                                   |
| `PUT`    | `/api/v1/products/{id}` | Update a product                                |
| `DELETE` | `/api/v1/products/{id}` | Delete a product                                |

### Stock Movements — `/api/v1/stock-movements`

| Method | Path                      | Description                                                    |
|--------|---------------------------|----------------------------------------------------------------|
| `GET`  | `/api/v1/stock-movements` | List movements, ordered newest first (optional `?product_id=`) |
| `POST` | `/api/v1/stock-movements` | Record a movement; updates `quantity_in_stock`                 |

**POST body example:**

```json
{
  "product_id": "uuid-here",
  "movement_type": "in",
  "quantity": 50,
  "reason": "Initial stock receipt"
}
```

A `400` is returned if an `"out"` movement would push stock below zero.
