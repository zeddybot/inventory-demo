from fastapi import FastAPI

from app.database import Base, engine
from app.routers import allocations, order_items, orders, products
from app.seed import seed

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Demo API")

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(order_items.router)
app.include_router(allocations.router)


@app.on_event("startup")
def on_startup():
    seed()


@app.get("/health")
def health():
    return {"status": "ok"}
