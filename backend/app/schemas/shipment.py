from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal

class ShipmentBase(BaseModel):
    planned_date: date
    vehicle_capacity_m3: Optional[Decimal] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    vehicle_plate: Optional[str] = None
    notes: Optional[str] = None

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentUpdate(BaseModel):
    status: Optional[str] = None
    planned_date: Optional[date] = None
    vehicle_capacity_m3: Optional[Decimal] = None
    route_data: Optional[Dict[str, Any]] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    vehicle_plate: Optional[str] = None
    notes: Optional[str] = None

class ShipmentResponse(ShipmentBase):
    id: int
    shipment_number: str
    status: str
    route_data: Optional[Dict[str, Any]] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ShipmentItemBase(BaseModel):
    package_id: int
    sequence: Optional[int] = None
    volume_m3: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None

class ShipmentItemCreate(ShipmentItemBase):
    pass

class ShipmentItemUpdate(BaseModel):
    sequence: Optional[int] = None
    volume_m3: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None

class ShipmentItemResponse(ShipmentItemBase):
    id: int
    shipment_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
