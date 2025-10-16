from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models.production import Lot, LotLog, DefectWaste
from ..schemas.production import LotResponse, LotLogResponse, DefectWasteResponse
from ..utils.rbac import RBACManager, Permission
from ..utils.state_machine import state_manager
from ..security.auth import get_current_user

router = APIRouter()

def get_rbac_manager(db: Session = Depends(get_db)) -> RBACManager:
    return RBACManager(db)

@router.get("/", response_model=List[LotResponse])
async def get_lots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    production_job_id: Optional[int] = Query(None),
    operator_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get list of lots"""
    if not rbac.has_permission(current_user["id"], Permission.LOT_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(Lot)
    
    if status:
        query = query.filter(Lot.status == status)
    
    if production_job_id:
        query = query.filter(Lot.production_job_id == production_job_id)
    
    if operator_id:
        query = query.filter(Lot.operator_id == operator_id)
    
    # Production operators can only see their own lots
    if current_user["role"] == "production_operator":
        query = query.filter(Lot.operator_id == current_user["id"])
    
    lots = query.offset(skip).limit(limit).all()
    return lots

@router.get("/{lot_id}", response_model=LotResponse)
async def get_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get lot by ID"""
    if not rbac.can_access_lot(current_user["id"], lot_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found"
        )
    
    return lot

@router.get("/{lot_id}/logs", response_model=List[LotLogResponse])
async def get_lot_logs(
    lot_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get lot logs"""
    if not rbac.can_access_lot(current_user["id"], lot_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    lot_logs = db.query(LotLog).filter(LotLog.lot_id == lot_id).offset(skip).limit(limit).all()
    return lot_logs

@router.get("/{lot_id}/waste", response_model=List[DefectWasteResponse])
async def get_lot_waste(
    lot_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get lot waste records"""
    if not rbac.can_access_lot(current_user["id"], lot_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    waste_records = db.query(DefectWaste).filter(
        DefectWaste.context_type == "lot",
        DefectWaste.context_id == lot_id
    ).offset(skip).limit(limit).all()
    
    return waste_records