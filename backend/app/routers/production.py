from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..db import get_db
from ..models.production import ProductionJob, Lot, LotLog, DefectWaste
from ..models.user import User, Role
from ..models.order import OrderItem
from ..schemas.production import (
    ProductionJobCreate, ProductionJobUpdate, ProductionJobResponse,
    LotCreate, LotUpdate, LotResponse,
    LotLogCreate, LotLogResponse,
    DefectWasteCreate, DefectWasteResponse
)
from ..utils.rbac import RBACManager, Permission
from ..utils.state_machine import state_manager
from ..utils.fire_management import FireNotificationManager
from ..security.auth import get_current_user

router = APIRouter()

def get_rbac_manager(db: Session = Depends(get_db)) -> RBACManager:
    return RBACManager(db)

def get_fire_manager(db: Session = Depends(get_db)) -> FireNotificationManager:
    return FireNotificationManager(db)

# Production Jobs endpoints
@router.get("/", response_model=List[ProductionJobResponse])
async def get_production_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    assigned_operator_id: Optional[int] = Query(None),
    priority: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get list of production jobs"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCTION_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(ProductionJob)
    
    if status:
        query = query.filter(ProductionJob.status == status)
    
    if assigned_operator_id:
        query = query.filter(ProductionJob.assigned_operator_id == assigned_operator_id)
    
    if priority:
        query = query.filter(ProductionJob.priority == priority)
    
    # Production operators can only see their assigned jobs
    role = db.query(Role).filter(Role.id == current_user.role_id).first()
    if role and role.name == "operator":
        query = query.filter(ProductionJob.assigned_operator_id == current_user.id)
    
    production_jobs = query.offset(skip).limit(limit).all()
    return production_jobs

@router.get("/{job_id}", response_model=ProductionJobResponse)
async def get_production_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get production job by ID"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCTION_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    production_job = db.query(ProductionJob).filter(ProductionJob.id == job_id).first()
    if not production_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production job not found"
        )
    
    return production_job

@router.post("/", response_model=ProductionJobResponse)
async def create_production_job(
    job_data: ProductionJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create new production job"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCTION_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify order item exists
    order_item = db.query(OrderItem).filter(OrderItem.id == job_data.order_item_id).first()
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order item not found"
        )
    
    # Verify assigned operator exists
    if job_data.assigned_operator_id:
        operator = db.query(User).filter(User.id == job_data.assigned_operator_id).first()
        if not operator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned operator not found"
            )
    
    production_job = ProductionJob(
        order_item_id=job_data.order_item_id,
        priority=job_data.priority or 1,
        assigned_operator_id=job_data.assigned_operator_id,
        planned_start_date=job_data.planned_start_date,
        planned_end_date=job_data.planned_end_date,
        notes=job_data.notes,
        created_by=current_user.id
    )
    
    db.add(production_job)
    db.commit()
    db.refresh(production_job)
    
    return production_job

@router.put("/{job_id}", response_model=ProductionJobResponse)
async def update_production_job(
    job_id: int,
    job_data: ProductionJobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Update production job"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCTION_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    production_job = db.query(ProductionJob).filter(ProductionJob.id == job_id).first()
    if not production_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production job not found"
        )
    
    # Update production job fields
    for field, value in job_data.dict(exclude_unset=True).items():
        setattr(production_job, field, value)
    
    db.commit()
    db.refresh(production_job)
    
    return production_job

@router.post("/{job_id}/assign")
async def assign_production_job(
    job_id: int,
    operator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Assign production job to operator"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCTION_ASSIGN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    production_job = db.query(ProductionJob).filter(ProductionJob.id == job_id).first()
    if not production_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production job not found"
        )
    
    # Verify operator exists
    operator = db.query(User).filter(User.id == operator_id).first()
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operator not found"
        )
    
    production_job.assigned_operator_id = operator_id
    db.commit()
    
    return {"message": "Production job assigned successfully"}

@router.post("/{job_id}/start")
async def start_production_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Start production job"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCTION_START):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    production_job = db.query(ProductionJob).filter(ProductionJob.id == job_id).first()
    if not production_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production job not found"
        )
    
    # Check if job can be started
    if production_job.status != "beklemede":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending jobs can be started"
        )
    
    # Update job status and start date
    production_job.status = "uretimde"
    production_job.actual_start_date = date.today()
    
    db.commit()
    
    return {"message": "Production job started successfully"}

@router.post("/{job_id}/finish")
async def finish_production_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Finish production job"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCTION_FINISH):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    production_job = db.query(ProductionJob).filter(ProductionJob.id == job_id).first()
    if not production_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production job not found"
        )
    
    # Check if job can be finished
    if production_job.status != "uretimde":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active jobs can be finished"
        )
    
    # Update job status and end date
    production_job.status = "tamamlandi"
    production_job.actual_end_date = date.today()
    
    db.commit()
    
    return {"message": "Production job finished successfully"}

# Lots endpoints
@router.get("/lots", response_model=List[LotResponse])
async def get_lots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    production_job_id: Optional[int] = Query(None),
    operator_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get list of lots"""
    if not rbac.has_permission(current_user.id, Permission.LOT_READ):
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
        query = query.filter(Lot.operator_id == current_user.id)
    
    lots = query.offset(skip).limit(limit).all()
    return lots

@router.get("/lots/{lot_id}", response_model=LotResponse)
async def get_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get lot by ID"""
    if not rbac.can_access_lot(current_user.id, lot_id):
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

@router.post("/lots", response_model=LotResponse)
async def create_lot(
    lot_data: LotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create new lot"""
    if not rbac.has_permission(current_user.id, Permission.LOT_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify production job exists
    production_job = db.query(ProductionJob).filter(ProductionJob.id == lot_data.production_job_id).first()
    if not production_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Production job not found"
        )
    
    # Generate lot number
    lot_number = f"{date.today().strftime('%Y%m%d')}-{production_job.order_item.product.code}-{db.query(Lot).count() + 1:04d}"
    
    lot = Lot(
        lot_number=lot_number,
        production_job_id=lot_data.production_job_id,
        shift=lot_data.shift,
        operator_id=lot_data.operator_id or current_user.id,
        planned_quantity=lot_data.planned_quantity,
        notes=lot_data.notes
    )
    
    db.add(lot)
    db.commit()
    db.refresh(lot)
    
    return lot

@router.put("/lots/{lot_id}", response_model=LotResponse)
async def update_lot(
    lot_id: int,
    lot_data: LotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Update lot"""
    if not rbac.can_modify_lot(current_user.id, lot_id):
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
    
    # Update lot fields
    for field, value in lot_data.dict(exclude_unset=True).items():
        setattr(lot, field, value)
    
    db.commit()
    db.refresh(lot)
    
    return lot

@router.post("/lots/{lot_id}/waste", response_model=DefectWasteResponse)
async def add_lot_waste(
    lot_id: int,
    waste_data: DefectWasteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager),
    fire_manager: FireNotificationManager = Depends(get_fire_manager)
):
    """Add waste record to lot"""
    if not rbac.has_permission(current_user.id, Permission.LOT_WASTE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify lot exists
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found"
        )
    
    # Create waste record
    waste_record = DefectWaste(
        context_type="lot",
        context_id=lot_id,
        waste_kg=waste_data.waste_kg,
        waste_percentage=waste_data.waste_percentage,
        reason_code=waste_data.reason_code,
        description=waste_data.description,
        photo_ref=waste_data.photo_ref,
        user_id=current_user.id
    )
    
    db.add(waste_record)
    db.commit()
    db.refresh(waste_record)
    
    # Check fire levels and send notifications
    fire_manager.check_and_send_notifications(waste_record.id)
    
    return waste_record

@router.get("/lots/{lot_id}/logs", response_model=List[LotLogResponse])
async def get_lot_logs(
    lot_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get lot logs"""
    if not rbac.can_access_lot(current_user.id, lot_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    lot_logs = db.query(LotLog).filter(LotLog.lot_id == lot_id).offset(skip).limit(limit).all()
    return lot_logs

@router.post("/lots/{lot_id}/logs", response_model=LotLogResponse)
async def create_lot_log(
    lot_id: int,
    log_data: LotLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create lot log"""
    if not rbac.has_permission(current_user.id, Permission.LOT_LOG):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify lot exists
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found"
        )
    
    lot_log = LotLog(
        lot_id=lot_id,
        event_type=log_data.event_type,
        user_id=current_user.id,
        description=log_data.description,
        photo_ref=log_data.photo_ref,
        meta_data=log_data.meta_data
    )
    
    db.add(lot_log)
    db.commit()
    db.refresh(lot_log)
    
    return lot_log