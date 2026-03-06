from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OrderItem
from app.schemas import OrderItemCreate, OrderItemRead

router = APIRouter(prefix="/order-items", tags=["order_items"])


@router.get("/", response_model=list[OrderItemRead])
def list_order_items(order_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(OrderItem)
    if order_id is not None:
        query = query.filter(OrderItem.order_id == order_id)
    return query.all()


@router.get("/{item_id}", response_model=OrderItemRead)
def get_order_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OrderItem, item_id)
    if not item:
        raise HTTPException(404, "Order item not found")
    return item


@router.post("/", response_model=OrderItemRead, status_code=201)
def create_order_item(body: OrderItemCreate, db: Session = Depends(get_db)):
    item = OrderItem(**body.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_order_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OrderItem, item_id)
    if not item:
        raise HTTPException(404, "Order item not found")
    db.delete(item)
    db.commit()
