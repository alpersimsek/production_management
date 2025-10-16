from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date

class ProductBase(BaseModel):
    name: str
    code: str
    product_type: str  # poset, deterjan, al-sat
    unit: str  # kg, adet, m3
    efficiency: Optional[float] = None
    label_template: Optional[Dict[str, Any]] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    product_type: Optional[str] = None
    unit: Optional[str] = None
    efficiency: Optional[float] = None
    label_template: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class FormulaBase(BaseModel):
    version: str
    formula_data: Dict[str, Any]
    valid_from: date
    valid_to: Optional[date] = None

class FormulaCreate(FormulaBase):
    pass

class FormulaResponse(FormulaBase):
    id: int
    product_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
