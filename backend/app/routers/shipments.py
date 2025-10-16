from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..db import get_db
from ..models.shipment import Shipment, ShipmentItem
from ..models.production import Packaging
from ..schemas.shipment import (
    ShipmentCreate, ShipmentUpdate, ShipmentResponse,
    ShipmentItemCreate, ShipmentItemUpdate, ShipmentItemResponse
)
from ..utils.rbac import RBACManager, Permission
from ..utils.state_machine import state_manager
from ..security.auth import get_current_user

router = APIRouter()

def get_rbac_manager(db: Session = Depends(get_db)) -> RBACManager:
    return RBACManager(db)

# Shipment endpoints
@router.get("/", response_model=List[ShipmentResponse])
async def get_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    planned_date_from: Optional[date] = Query(None),
    planned_date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get list of shipments"""
    if not rbac.has_permission(current_user["id"], Permission.SHIPMENT_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(Shipment)
    
    if status:
        query = query.filter(Shipment.status == status)
    
    if planned_date_from:
        query = query.filter(Shipment.planned_date >= planned_date_from)
    
    if planned_date_to:
        query = query.filter(Shipment.planned_date <= planned_date_to)
    
    shipments = query.offset(skip).limit(limit).all()
    return shipments

@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get shipment by ID"""
    if not rbac.has_permission(current_user["id"], Permission.SHIPMENT_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    return shipment

@router.post("/", response_model=ShipmentResponse)
async def create_shipment(
    shipment_data: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create new shipment"""
    if not rbac.has_permission(current_user["id"], Permission.SHIPMENT_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Generate shipment number
    shipment_number = f"SHIP-{date.today().strftime('%Y%m%d')}-{db.query(Shipment).count() + 1:04d}"
    
    shipment = Shipment(
        shipment_number=shipment_number,
        planned_date=shipment_data.planned_date,
        vehicle_capacity_m3=shipment_data.vehicle_capacity_m3,
        driver_name=shipment_data.driver_name,
        driver_phone=shipment_data.driver_phone,
        vehicle_plate=shipment_data.vehicle_plate,
        notes=shipment_data.notes,
        created_by=current_user["id"]
    )
    
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    
    return shipment

@router.put("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(
    shipment_id: int,
    shipment_data: ShipmentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Update shipment"""
    if not rbac.has_permission(current_user["id"], Permission.SHIPMENT_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    # Update shipment fields
    for field, value in shipment_data.dict(exclude_unset=True).items():
        setattr(shipment, field, value)
    
    db.commit()
    db.refresh(shipment)
    
    return shipment

@router.post("/{shipment_id}/plan")
async def plan_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Plan shipment"""
    if not rbac.has_permission(current_user["id"], Permission.SHIPMENT_PLAN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    if shipment.status != "planlandi":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only planned shipments can be planned"
        )
    
    # Update status to planned
    shipment.status = "planlandi"
    db.commit()
    
    return {"message": "Shipment planned successfully"}

@router.post("/{shipment_id}/deliver")
async def deliver_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Mark shipment as delivered"""
    if not rbac.has_permission(current_user["id"], Permission.SHIPMENT_DELIVER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    if shipment.status not in ["yuklendi", "teslimde"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only loaded or in-transit shipments can be delivered"
        )
    
    # Update status to delivered
    shipment.status = "teslim_edildi"
    db.commit()
    
    return {"message": "Shipment delivered successfully"}

# Shipment Items endpoints
@router.get("/{shipment_id}/items", response_model=List[ShipmentItemResponse])
async def get_shipment_items(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get shipment items"""
    if not rbac.has_permission(current_user["id"], Permission.SHIPMENT_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    shipment_items = db.query(ShipmentItem).filter(ShipmentItem.shipment_id == shipment_id).all()
    return shipment_items

@router.post("/{shipment_id}/items", response_model=ShipmentItemResponse)
async def create_shipment_item(
    shipment_id: int,
    item_data: ShipmentItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create shipment item"""
    if not rbac.has_permission(current_user["id"], Permission.SHIPMENT_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify shipment exists
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    # Verify package exists
    package = db.query(Packaging).filter(Packaging.id == item_data.package_id).first()
    if not package:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Package not found"
        )
    
    shipment_item = ShipmentItem(
        shipment_id=shipment_id,
        package_id=item_data.package_id,
        sequence=item_data.sequence,
        volume_m3=item_data.volume_m3,
        weight_kg=item_data.weight_kg
    )
    
    db.add(shipment_item)
    db.commit()
    db.refresh(shipment_item)
    
    return shipment_item

@router.put("/items/{item_id}", response_model=ShipmentItemResponse)
async def update_shipment_item(
    item_id: int,
    item_data: ShipmentItemUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Update shipment item"""
    if not rbac.has_permission(current_user["id"], Permission.SHIPMENT_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    shipment_item = db.query(ShipmentItem).filter(ShipmentItem.id == item_id).first()
    if not shipment_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment item not found"
        )
    
    # Update shipment item fields
    for field, value in item_data.dict(exclude_unset=True).items():
        setattr(shipment_item, field, value)
    
    db.commit()
    db.refresh(shipment_item)
    
    return shipment_item

@router.delete("/items/{item_id}")
async def delete_shipment_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Delete shipment item"""
    if not rbac.has_permission(current_user["id"], Permission.SHIPMENT_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    shipment_item = db.query(ShipmentItem).filter(ShipmentItem.id == item_id).first()
    if not shipment_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment item not found"
        )
    
    db.delete(shipment_item)
    db.commit()
    
    return {"message": "Shipment item deleted successfully"}