from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

class OrderItemBase(BaseModel):
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    notes: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    delivery_status: Optional[str] = None
    notes: Optional[str] = None

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    total_price: Decimal
    delivery_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_id: int
    salesperson_id: Optional[int] = None
    due_date: date
    total_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    markup_amount: Optional[Decimal] = None
    fuel_cost: Optional[Decimal] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    salesperson_id: Optional[int] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    total_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    markup_amount: Optional[Decimal] = None
    fuel_cost: Optional[Decimal] = None
    profitability: Optional[Decimal] = None
    notes: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    order_number: str
    status: str
    order_date: date
    profitability: Optional[Decimal] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    customer_name: Optional[str] = None
    
    class Config:
        from_attributes = True
