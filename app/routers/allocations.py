from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Allocation, Order, OrderItem, Product
from app.schemas import (
    AllocationCreate,
    AllocationDetail,
    AllocationRead,
    AllocateInventoryResponse,
    OrderAllocationSummary,
)

router = APIRouter(prefix="/allocations", tags=["allocations"])


@router.get("/", response_model=list[AllocationRead])
def list_allocations(order_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Allocation)
    if order_id is not None:
        query = query.filter(Allocation.order_id == order_id)
    return query.all()


@router.get("/{allocation_id}", response_model=AllocationRead)
def get_allocation(allocation_id: int, db: Session = Depends(get_db)):
    alloc = db.get(Allocation, allocation_id)
    if not alloc:
        raise HTTPException(404, "Allocation not found")
    return alloc


@router.post("/", response_model=AllocationRead, status_code=201)
def create_allocation(body: AllocationCreate, db: Session = Depends(get_db)):
    alloc = Allocation(**body.model_dump())
    db.add(alloc)
    db.commit()
    db.refresh(alloc)
    return alloc


@router.delete("/{allocation_id}", status_code=204)
def delete_allocation(allocation_id: int, db: Session = Depends(get_db)):
    alloc = db.get(Allocation, allocation_id)
    if not alloc:
        raise HTTPException(404, "Allocation not found")
    db.delete(alloc)
    db.commit()


@router.post("/allocate-inventory", response_model=AllocateInventoryResponse)
def allocate_inventory(db: Session = Depends(get_db)):
    # Step 1: Get all pending orders
    pending_orders = (
        db.query(Order)
        .filter(Order.status == "pending")
        .order_by(Order.priority.asc(), Order.created_at.asc())
        .all()
    )
    pending_order_ids = [o.id for o in pending_orders]

    # Step 2: Clear existing allocations for pending orders and restore quantities
    existing_allocs = (
        db.query(Allocation)
        .filter(Allocation.order_id.in_(pending_order_ids))
        .all()
    )
    for alloc in existing_allocs:
        product = db.get(Product, alloc.product_id)
        if product:
            product.available_quantity += alloc.allocated_quantity
        db.delete(alloc)

    # Step 3: Allocate inventory by priority
    products = {p.id: p for p in db.query(Product).all()}
    total_allocations = 0
    order_summaries = []

    for order in pending_orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        allocations = []
        fully_fulfilled = True

        for item in items:
            product = products.get(item.product_id)
            if not product:
                fully_fulfilled = False
                continue

            allocate_qty = min(item.requested_quantity, product.available_quantity)
            if allocate_qty > 0:
                alloc = Allocation(
                    order_id=order.id,
                    product_id=item.product_id,
                    allocated_quantity=allocate_qty,
                )
                db.add(alloc)
                product.available_quantity -= allocate_qty
                total_allocations += 1

            if allocate_qty < item.requested_quantity:
                fully_fulfilled = False

            allocations.append(
                AllocationDetail(
                    order_id=order.id,
                    product_id=item.product_id,
                    requested_quantity=item.requested_quantity,
                    allocated_quantity=allocate_qty if allocate_qty > 0 else 0,
                )
            )

        order_summaries.append(
            OrderAllocationSummary(
                order_id=order.id,
                customer=order.customer,
                priority=order.priority,
                fully_fulfilled=fully_fulfilled,
                allocations=allocations,
            )
        )

    db.commit()

    orders_fully = sum(1 for s in order_summaries if s.fully_fulfilled)
    return AllocateInventoryResponse(
        total_allocations_created=total_allocations,
        orders_processed=len(pending_orders),
        orders_fully_fulfilled=orders_fully,
        orders_partially_fulfilled=len(pending_orders) - orders_fully,
        order_summaries=order_summaries,
    )
