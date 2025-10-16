from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class WarehouseBase(BaseModel):
    code: str
    name: str
    location: Optional[str] = None
    capacity_m3: Optional[Decimal] = None

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    capacity_m3: Optional[Decimal] = None
    is_active: Optional[bool] = None

class WarehouseResponse(WarehouseBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class WarehouseReceiptBase(BaseModel):
    package_id: int
    warehouse_id: int
    weight_kg: Decimal
    notes: Optional[str] = None

class WarehouseReceiptCreate(WarehouseReceiptBase):
    pass

class WarehouseReceiptUpdate(BaseModel):
    warehouse_id: Optional[int] = None
    weight_kg: Optional[Decimal] = None
    photo_ref: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class WarehouseReceiptResponse(WarehouseReceiptBase):
    id: int
    receipt_date: date
    receipt_time: datetime
    approved_by: int
    photo_ref: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class InventoryMovementBase(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: Decimal
    unit: str
    movement_type: str
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None

class InventoryMovementCreate(InventoryMovementBase):
    lot_id: Optional[int] = None

class InventoryMovementResponse(InventoryMovementBase):
    id: int
    lot_id: Optional[int] = None
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True
