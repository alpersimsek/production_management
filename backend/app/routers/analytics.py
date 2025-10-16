from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from ..db import get_db
from ..utils.rbac import RBACManager, Permission
from ..utils.fire_management import FireAnalytics
from ..utils.termin_manager import TerminAnalytics
from ..security.auth import get_current_user

router = APIRouter()

def get_rbac_manager(db: Session = Depends(get_db)) -> RBACManager:
    return RBACManager(db)

def get_fire_analytics(db: Session = Depends(get_db)) -> FireAnalytics:
    return FireAnalytics(db)

def get_termin_analytics(db: Session = Depends(get_db)) -> TerminAnalytics:
    return TerminAnalytics(db)

@router.get("/fire")
async def get_fire_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    product_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager),
    fire_analytics: FireAnalytics = Depends(get_fire_analytics)
):
    """Get fire analytics and statistics"""
    if not rbac.has_permission(current_user["id"], Permission.ANALYTICS_FIRE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Convert dates to datetime if provided
    start_datetime = None
    end_datetime = None
    
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
    
    fire_summary = fire_analytics.get_fire_summary(
        start_date=start_datetime,
        end_date=end_datetime,
        product_type=product_type
    )
    
    return fire_summary

@router.get("/fire/performance")
async def get_fire_performance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager),
    fire_analytics: FireAnalytics = Depends(get_fire_analytics)
):
    """Get fire performance by operator"""
    if not rbac.has_permission(current_user["id"], Permission.ANALYTICS_PERFORMANCE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Convert dates to datetime if provided
    start_datetime = None
    end_datetime = None
    
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
    
    performance_data = fire_analytics.get_operator_fire_performance(
        start_date=start_datetime,
        end_date=end_datetime
    )
    
    return performance_data

@router.get("/termin")
async def get_termin_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager),
    termin_analytics: TerminAnalytics = Depends(get_termin_analytics)
):
    """Get termin analytics and performance"""
    if not rbac.has_permission(current_user["id"], Permission.ANALYTICS_TERMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    performance_data = termin_analytics.get_termin_performance(
        start_date=start_date,
        end_date=end_date
    )
    
    return performance_data

@router.get("/termin/salesperson")
async def get_salesperson_performance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager),
    termin_analytics: TerminAnalytics = Depends(get_termin_analytics)
):
    """Get salesperson performance analytics"""
    if not rbac.has_permission(current_user["id"], Permission.ANALYTICS_SALES):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    performance_data = termin_analytics.get_salesperson_performance(
        start_date=start_date,
        end_date=end_date
    )
    
    return performance_data

@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager),
    fire_analytics: FireAnalytics = Depends(get_fire_analytics),
    termin_analytics: TerminAnalytics = Depends(get_termin_analytics)
):
    """Get dashboard data with key metrics"""
    dashboard_data = {}
    
    # Fire analytics (last 30 days)
    if rbac.has_permission(current_user["id"], Permission.ANALYTICS_FIRE):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        fire_summary = fire_analytics.get_fire_summary(
            start_date=start_date,
            end_date=end_date
        )
        dashboard_data["fire"] = fire_summary
    
    # Termin analytics (last 30 days)
    if rbac.has_permission(current_user["id"], Permission.ANALYTICS_TERMIN):
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        termin_performance = termin_analytics.get_termin_performance(
            start_date=start_date,
            end_date=end_date
        )
        dashboard_data["termin"] = termin_performance
    
    # Production metrics
    if rbac.has_permission(current_user["id"], Permission.PRODUCTION_READ):
        from ..models.production import ProductionJob, Lot
        
        # Active production jobs
        active_jobs = db.query(ProductionJob).filter(
            ProductionJob.status.in_(["beklemede", "uretimde"])
        ).count()
        
        # Completed lots today
        today = date.today()
        completed_lots_today = db.query(Lot).filter(
            Lot.end_time >= datetime.combine(today, datetime.min.time()),
            Lot.end_time <= datetime.combine(today, datetime.max.time())
        ).count()
        
        # Pending lots
        pending_lots = db.query(Lot).filter(Lot.status == "olusturuldu").count()
        
        dashboard_data["production"] = {
            "active_jobs": active_jobs,
            "completed_lots_today": completed_lots_today,
            "pending_lots": pending_lots
        }
    
    # Order metrics
    if rbac.has_permission(current_user["id"], Permission.ORDER_READ):
        from ..models.order import Order
        
        # Total orders
        total_orders = db.query(Order).count()
        
        # Orders due this week
        week_end = date.today() + timedelta(days=7)
        orders_due_week = db.query(Order).filter(
            Order.due_date <= week_end,
            Order.status.notin_(["teslim_edildi", "kapatildi"])
        ).count()
        
        # Overdue orders
        overdue_orders = db.query(Order).filter(
            Order.due_date < date.today(),
            Order.status.notin_(["teslim_edildi", "kapatildi"])
        ).count()
        
        dashboard_data["orders"] = {
            "total_orders": total_orders,
            "orders_due_week": orders_due_week,
            "overdue_orders": overdue_orders
        }
    
    # Warehouse metrics
    if rbac.has_permission(current_user["id"], Permission.WAREHOUSE_READ):
        from ..models.warehouse import WarehouseReceipt
        
        # Pending receipts
        pending_receipts = db.query(WarehouseReceipt).filter(
            WarehouseReceipt.status == "kabul_bekliyor"
        ).count()
        
        # Receipts today
        today = date.today()
        receipts_today = db.query(WarehouseReceipt).filter(
            WarehouseReceipt.receipt_date == today
        ).count()
        
        dashboard_data["warehouse"] = {
            "pending_receipts": pending_receipts,
            "receipts_today": receipts_today
        }
    
    # Shipment metrics
    if rbac.has_permission(current_user["id"], Permission.SHIPMENT_READ):
        from ..models.shipment import Shipment
        
        # Planned shipments
        planned_shipments = db.query(Shipment).filter(
            Shipment.status == "planlandi"
        ).count()
        
        # In transit shipments
        in_transit_shipments = db.query(Shipment).filter(
            Shipment.status.in_(["yuklendi", "teslimde"])
        ).count()
        
        dashboard_data["shipments"] = {
            "planned_shipments": planned_shipments,
            "in_transit_shipments": in_transit_shipments
        }
    
    return dashboard_data

@router.get("/kpis")
async def get_kpis(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get Key Performance Indicators"""
    # Calculate date range based on period
    end_date = date.today()
    if period == "7d":
        start_date = end_date - timedelta(days=7)
    elif period == "30d":
        start_date = end_date - timedelta(days=30)
    elif period == "90d":
        start_date = end_date - timedelta(days=90)
    else:  # 1y
        start_date = end_date - timedelta(days=365)
    
    kpis = {}
    
    # Fire KPIs
    if rbac.has_permission(current_user["id"], Permission.ANALYTICS_FIRE):
        fire_analytics = FireAnalytics(db)
        fire_summary = fire_analytics.get_fire_summary(
            start_date=datetime.combine(start_date, datetime.min.time()),
            end_date=datetime.combine(end_date, datetime.max.time())
        )
        
        kpis["fire"] = {
            "total_waste_kg": fire_summary["total_waste_kg"],
            "fire_incidents": fire_summary["total_records"],
            "critical_incidents": fire_summary["level2_count"],
            "warning_incidents": fire_summary["level1_count"]
        }
    
    # Termin KPIs
    if rbac.has_permission(current_user["id"], Permission.ANALYTICS_TERMIN):
        termin_analytics = TerminAnalytics(db)
        termin_performance = termin_analytics.get_termin_performance(
            start_date=start_date,
            end_date=end_date
        )
        
        kpis["termin"] = {
            "on_time_percentage": termin_performance["on_time_percentage"],
            "total_orders": termin_performance["total_orders"],
            "late_deliveries": termin_performance["late_delivery"],
            "average_delay_days": termin_performance["average_delay_days"]
        }
    
    # Production KPIs
    if rbac.has_permission(current_user["id"], Permission.PRODUCTION_READ):
        from ..models.production import ProductionJob, Lot
        from sqlalchemy import func
        
        # Production efficiency
        lots_in_period = db.query(Lot).filter(
            Lot.created_at >= datetime.combine(start_date, datetime.min.time()),
            Lot.created_at <= datetime.combine(end_date, datetime.max.time())
        ).all()
        
        if lots_in_period:
            total_planned = sum(float(lot.planned_quantity or 0) for lot in lots_in_period)
            total_actual = sum(float(lot.actual_quantity or 0) for lot in lots_in_period)
            total_waste = sum(float(lot.waste_quantity or 0) for lot in lots_in_period)
            
            efficiency = (total_actual / total_planned * 100) if total_planned > 0 else 0
            waste_percentage = (total_waste / total_planned * 100) if total_planned > 0 else 0
        else:
            efficiency = 0
            waste_percentage = 0
        
        kpis["production"] = {
            "efficiency_percentage": round(efficiency, 2),
            "waste_percentage": round(waste_percentage, 2),
            "total_lots": len(lots_in_period),
            "completed_lots": len([lot for lot in lots_in_period if lot.status == "depoda"])
        }
    
    return kpis