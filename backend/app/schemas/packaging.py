from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class PackagingBase(BaseModel):
    lot_id: int
    package_type: str
    quantity: int
    package_weight: Optional[Decimal] = None
    notes: Optional[str] = None

class PackagingCreate(PackagingBase):
    pass

class PackagingUpdate(BaseModel):
    package_type: Optional[str] = None
    quantity: Optional[int] = None
    package_weight: Optional[Decimal] = None
    waste_kg: Optional[Decimal] = None
    photo_ref: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class PackagingResponse(PackagingBase):
    id: int
    waste_kg: Optional[Decimal] = None
    photo_ref: Optional[str] = None
    status: str
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True
