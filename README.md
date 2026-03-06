# Inventory Demo

Warehouse/inventory REST API built with FastAPI + SQLAlchemy + SQLite.

## Project Structure

```
app/
  main.py          # FastAPI app entry point, includes routers, runs seed on startup
  database.py      # SQLAlchemy engine, session, Base (SQLite)
  models.py        # 4 tables: products, orders, order_items, allocations
  schemas.py       # Pydantic request/response models
  seed.py          # Seeds 20 products, 10 orders with competing demand
  routers/
    products.py    # CRUD for products
    orders.py      # CRUD for orders
    order_items.py # CRUD for order items
    allocations.py # CRUD for allocations
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

API docs available at http://localhost:8000/docs

## API Endpoints

| Resource      | Endpoints                          |
|---------------|------------------------------------|
| Products      | `GET/POST /products`, `GET/PUT/DELETE /products/{id}` |
| Orders        | `GET/POST /orders`, `GET/PUT/DELETE /orders/{id}` |
| Order Items   | `GET/POST /order-items`, `GET/PUT/DELETE /order-items/{id}` |
| Allocations   | `GET/POST /allocations`, `GET/PUT/DELETE /allocations/{id}` |
| Health        | `GET /health` |

## Database

SQLite (`inventory.db`), auto-created on startup. Seed data runs automatically if the DB is empty.

## Key Design Notes

- Several orders intentionally compete for scarce products (motors, sensors, batteries) to create interesting allocation conflicts
- Order statuses: `pending`, `confirmed`, `shipped`
- Priority: `1` (urgent) to `4` (low)
