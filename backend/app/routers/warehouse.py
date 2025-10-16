from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..db import get_db
from ..models.warehouse import Warehouse, WarehouseReceipt, Inventory
from ..models.production import Packaging
from ..schemas.warehouse import (
    WarehouseCreate, WarehouseUpdate, WarehouseResponse,
    WarehouseReceiptCreate, WarehouseReceiptUpdate, WarehouseReceiptResponse,
    InventoryMovementCreate, InventoryMovementResponse
)
from ..utils.rbac import RBACManager, Permission
from ..security.auth import get_current_user

router = APIRouter()

def get_rbac_manager(db: Session = Depends(get_db)) -> RBACManager:
    return RBACManager(db)

# Warehouse endpoints
@router.get("/", response_model=List[WarehouseResponse])
async def get_warehouses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get list of warehouses"""
    if not rbac.has_permission(current_user["id"], Permission.WAREHOUSE_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(Warehouse)
    
    if active_only:
        query = query.filter(Warehouse.is_active == True)
    
    warehouses = query.offset(skip).limit(limit).all()
    return warehouses

@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get warehouse by ID"""
    if not rbac.has_permission(current_user["id"], Permission.WAREHOUSE_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    return warehouse

@router.post("/", response_model=WarehouseResponse)
async def create_warehouse(
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create new warehouse"""
    if not rbac.has_permission(current_user["id"], Permission.WAREHOUSE_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if warehouse with same code already exists
    existing_warehouse = db.query(Warehouse).filter(Warehouse.code == warehouse_data.code).first()
    if existing_warehouse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warehouse with this code already exists"
        )
    
    warehouse = Warehouse(**warehouse_data.dict())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    
    return warehouse

@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: int,
    warehouse_data: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Update warehouse"""
    if not rbac.has_permission(current_user["id"], Permission.WAREHOUSE_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    # Check if code is being changed and if it already exists
    if warehouse_data.code and warehouse_data.code != warehouse.code:
        existing_warehouse = db.query(Warehouse).filter(Warehouse.code == warehouse_data.code).first()
        if existing_warehouse:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Warehouse with this code already exists"
            )
    
    # Update warehouse fields
    for field, value in warehouse_data.dict(exclude_unset=True).items():
        setattr(warehouse, field, value)
    
    db.commit()
    db.refresh(warehouse)
    
    return warehouse

# Warehouse Receipt endpoints
@router.get("/receipts", response_model=List[WarehouseReceiptResponse])
async def get_warehouse_receipts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    warehouse_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get list of warehouse receipts"""
    if not rbac.has_permission(current_user["id"], Permission.WAREHOUSE_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(WarehouseReceipt)
    
    if warehouse_id:
        query = query.filter(WarehouseReceipt.warehouse_id == warehouse_id)
    
    if status:
        query = query.filter(WarehouseReceipt.status == status)
    
    receipts = query.offset(skip).limit(limit).all()
    return receipts

@router.post("/receipts", response_model=WarehouseReceiptResponse)
async def create_warehouse_receipt(
    receipt_data: WarehouseReceiptCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create new warehouse receipt"""
    if not rbac.has_permission(current_user["id"], Permission.WAREHOUSE_RECEIPT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify package exists
    package = db.query(Packaging).filter(Packaging.id == receipt_data.package_id).first()
    if not package:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Package not found"
        )
    
    # Verify warehouse exists
    warehouse = db.query(Warehouse).filter(Warehouse.id == receipt_data.warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warehouse not found"
        )
    
    receipt = WarehouseReceipt(
        package_id=receipt_data.package_id,
        warehouse_id=receipt_data.warehouse_id,
        weight_kg=receipt_data.weight_kg,
        notes=receipt_data.notes,
        approved_by=current_user["id"]
    )
    
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    
    return receipt

@router.put("/receipts/{receipt_id}", response_model=WarehouseReceiptResponse)
async def update_warehouse_receipt(
    receipt_id: int,
    receipt_data: WarehouseReceiptUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Update warehouse receipt"""
    if not rbac.has_permission(current_user["id"], Permission.WAREHOUSE_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    receipt = db.query(WarehouseReceipt).filter(WarehouseReceipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse receipt not found"
        )
    
    # Update receipt fields
    for field, value in receipt_data.dict(exclude_unset=True).items():
        setattr(receipt, field, value)
    
    db.commit()
    db.refresh(receipt)
    
    return receipt

@router.post("/receipts/{receipt_id}/approve")
async def approve_warehouse_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Approve warehouse receipt"""
    if not rbac.has_permission(current_user["id"], Permission.WAREHOUSE_APPROVE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    receipt = db.query(WarehouseReceipt).filter(WarehouseReceipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse receipt not found"
        )
    
    if receipt.status != "kabul_bekliyor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending receipts can be approved"
        )
    
    receipt.status = "depoya_alindi"
    receipt.approved_by = current_user["id"]
    
    # Create inventory movement
    inventory_movement = Inventory(
        product_id=receipt.package.lot.production_job.order_item.product_id,
        lot_id=receipt.package.lot_id,
        warehouse_id=receipt.warehouse_id,
        quantity=receipt.weight_kg,
        unit="kg",
        movement_type="giris",
        reference_id=receipt.id,
        reference_type="warehouse_receipt",
        notes=f"Warehouse receipt approval - {receipt.id}",
        created_by=current_user["id"]
    )
    
    db.add(inventory_movement)
    db.commit()
    
    return {"message": "Warehouse receipt approved successfully"}

# Inventory endpoints
@router.get("/inventory", response_model=List[InventoryMovementResponse])
async def get_inventory_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    warehouse_id: Optional[int] = Query(None),
    product_id: Optional[int] = Query(None),
    movement_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get inventory movements"""
    if not rbac.has_permission(current_user["id"], Permission.WAREHOUSE_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(Inventory)
    
    if warehouse_id:
        query = query.filter(Inventory.warehouse_id == warehouse_id)
    
    if product_id:
        query = query.filter(Inventory.product_id == product_id)
    
    if movement_type:
        query = query.filter(Inventory.movement_type == movement_type)
    
    movements = query.offset(skip).limit(limit).all()
    return movements

@router.post("/inventory", response_model=InventoryMovementResponse)
async def create_inventory_movement(
    movement_data: InventoryMovementCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create inventory movement"""
    if not rbac.has_permission(current_user["id"], Permission.WAREHOUSE_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify warehouse exists
    warehouse = db.query(Warehouse).filter(Warehouse.id == movement_data.warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warehouse not found"
        )
    
    movement = Inventory(
        product_id=movement_data.product_id,
        lot_id=movement_data.lot_id,
        warehouse_id=movement_data.warehouse_id,
        quantity=movement_data.quantity,
        unit=movement_data.unit,
        movement_type=movement_data.movement_type,
        reference_id=movement_data.reference_id,
        reference_type=movement_data.reference_type,
        notes=movement_data.notes,
        created_by=current_user["id"]
    )
    
    db.add(movement)
    db.commit()
    db.refresh(movement)
    
    return movement