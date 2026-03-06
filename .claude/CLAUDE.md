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

## Running

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs

## Database

SQLite (`inventory.db`), auto-created on startup. Seed data runs automatically if the DB is empty.

## Key Design Notes

- Several orders intentionally compete for scarce products (motors, sensors, batteries) to create interesting allocation conflicts
- Order statuses: pending, confirmed, shipped
- Priority: 1 (urgent) to 4 (low)

## PR Guidelines

- Always follow conventional commit style for PR titles
- Format: `type(scope): description` — e.g. `feat(api): add inventory search endpoint (DEV-123)`
- Common types: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `ci`, `perf`
- Keep PR titles all lowercase
- Always include ticket numbers in PR titles
