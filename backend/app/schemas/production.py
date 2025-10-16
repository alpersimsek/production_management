from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class ProductionJobBase(BaseModel):
    order_item_id: int
    priority: Optional[int] = 1
    assigned_operator_id: Optional[int] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    notes: Optional[str] = None

class ProductionJobCreate(ProductionJobBase):
    pass

class ProductionJobUpdate(BaseModel):
    priority: Optional[int] = None
    assigned_operator_id: Optional[int] = None
    status: Optional[str] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    notes: Optional[str] = None

class ProductionJobResponse(ProductionJobBase):
    id: int
    status: str
    formula_snapshot: Optional[Dict[str, Any]] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LotBase(BaseModel):
    production_job_id: int
    shift: Optional[str] = None
    operator_id: Optional[int] = None
    planned_quantity: Optional[Decimal] = None
    notes: Optional[str] = None

class LotCreate(LotBase):
    pass

class LotUpdate(BaseModel):
    status: Optional[str] = None
    shift: Optional[str] = None
    operator_id: Optional[int] = None
    planned_quantity: Optional[Decimal] = None
    actual_quantity: Optional[Decimal] = None
    waste_quantity: Optional[Decimal] = None
    efficiency_percentage: Optional[Decimal] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

class LotResponse(LotBase):
    id: int
    lot_number: str
    status: str
    actual_quantity: Optional[Decimal] = None
    waste_quantity: Optional[Decimal] = None
    efficiency_percentage: Optional[Decimal] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LotLogBase(BaseModel):
    event_type: str
    description: Optional[str] = None
    photo_ref: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class LotLogCreate(LotLogBase):
    pass

class LotLogResponse(LotLogBase):
    id: int
    lot_id: int
    user_id: int
    ip_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class DefectWasteBase(BaseModel):
    waste_kg: Decimal
    waste_percentage: Optional[Decimal] = None
    reason_code: Optional[str] = None
    description: Optional[str] = None
    photo_ref: Optional[str] = None

class DefectWasteCreate(DefectWasteBase):
    pass

class DefectWasteResponse(DefectWasteBase):
    id: int
    context_type: str
    context_id: int
    level: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
