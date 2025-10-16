from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models.production import Packaging, Lot
from ..schemas.packaging import PackagingCreate, PackagingUpdate, PackagingResponse
from ..utils.rbac import RBACManager, Permission
from ..security.auth import get_current_user

router = APIRouter()

def get_rbac_manager(db: Session = Depends(get_db)) -> RBACManager:
    return RBACManager(db)

@router.get("/", response_model=List[PackagingResponse])
async def get_packaging(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    lot_id: Optional[int] = Query(None),
    package_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get list of packaging records"""
    if not rbac.has_permission(current_user["id"], Permission.PACKAGING_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(Packaging)
    
    if lot_id:
        query = query.filter(Packaging.lot_id == lot_id)
    
    if package_type:
        query = query.filter(Packaging.package_type == package_type)
    
    if status:
        query = query.filter(Packaging.status == status)
    
    packaging_records = query.offset(skip).limit(limit).all()
    return packaging_records

@router.get("/{packaging_id}", response_model=PackagingResponse)
async def get_packaging(
    packaging_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get packaging record by ID"""
    if not rbac.has_permission(current_user["id"], Permission.PACKAGING_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    packaging = db.query(Packaging).filter(Packaging.id == packaging_id).first()
    if not packaging:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Packaging record not found"
        )
    
    return packaging

@router.post("/", response_model=PackagingResponse)
async def create_packaging(
    packaging_data: PackagingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create new packaging record"""
    if not rbac.has_permission(current_user["id"], Permission.PACKAGING_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify lot exists
    lot = db.query(Lot).filter(Lot.id == packaging_data.lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lot not found"
        )
    
    packaging = Packaging(
        lot_id=packaging_data.lot_id,
        package_type=packaging_data.package_type,
        quantity=packaging_data.quantity,
        package_weight=packaging_data.package_weight,
        notes=packaging_data.notes,
        created_by=current_user["id"]
    )
    
    db.add(packaging)
    db.commit()
    db.refresh(packaging)
    
    return packaging

@router.put("/{packaging_id}", response_model=PackagingResponse)
async def update_packaging(
    packaging_id: int,
    packaging_data: PackagingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Update packaging record"""
    if not rbac.has_permission(current_user["id"], Permission.PACKAGING_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    packaging = db.query(Packaging).filter(Packaging.id == packaging_id).first()
    if not packaging:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Packaging record not found"
        )
    
    # Update packaging fields
    for field, value in packaging_data.dict(exclude_unset=True).items():
        setattr(packaging, field, value)
    
    db.commit()
    db.refresh(packaging)
    
    return packaging

@router.delete("/{packaging_id}")
async def delete_packaging(
    packaging_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Delete packaging record"""
    if not rbac.has_permission(current_user["id"], Permission.PACKAGING_DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    packaging = db.query(Packaging).filter(Packaging.id == packaging_id).first()
    if not packaging:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Packaging record not found"
        )
    
    db.delete(packaging)
    db.commit()
    
    return {"message": "Packaging record deleted successfully"}