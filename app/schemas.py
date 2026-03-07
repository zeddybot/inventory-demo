from datetime import datetime

from pydantic import BaseModel


# -- Products --

class ProductCreate(BaseModel):
    name: str
    sku: str
    available_quantity: int = 0


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    available_quantity: int | None = None


class ProductRead(BaseModel):
    id: int
    name: str
    sku: str
    available_quantity: int

    model_config = {"from_attributes": True}


# -- Orders --

class OrderCreate(BaseModel):
    customer: str
    priority: int = 3
    status: str = "pending"


class OrderUpdate(BaseModel):
    customer: str | None = None
    priority: int | None = None
    status: str | None = None


class OrderRead(BaseModel):
    id: int
    customer: str
    priority: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# -- Order Items --

class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    requested_quantity: int


class OrderItemRead(BaseModel):
    id: int
    order_id: int
    product_id: int
    requested_quantity: int

    model_config = {"from_attributes": True}


# -- Allocations --

class AllocationCreate(BaseModel):
    order_id: int
    product_id: int
    allocated_quantity: int


class AllocationRead(BaseModel):
    id: int
    order_id: int
    product_id: int
    allocated_quantity: int

    model_config = {"from_attributes": True}


# -- Allocate Inventory Response --

class AllocationDetail(BaseModel):
    order_id: int
    product_id: int
    requested_quantity: int
    allocated_quantity: int

    model_config = {"from_attributes": True}


class OrderAllocationSummary(BaseModel):
    order_id: int
    customer: str
    priority: int
    fully_fulfilled: bool
    allocations: list[AllocationDetail]


class AllocateInventoryResponse(BaseModel):
    total_allocations_created: int
    orders_processed: int
    orders_fully_fulfilled: int
    orders_partially_fulfilled: int
    order_summaries: list[OrderAllocationSummary]
