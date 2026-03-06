from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Allocation
from app.schemas import AllocationCreate, AllocationRead

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
