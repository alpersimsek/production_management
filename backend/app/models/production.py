from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date, String, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..db import Base

class ProductionJob(Base):
    __tablename__ = "production_jobs"
    id = Column(Integer, primary_key=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=False)
    priority = Column(Integer, server_default='1')  # öncelik
    assigned_operator_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), nullable=False, server_default='beklemede')
    formula_snapshot = Column(JSONB)  # formül anlık görüntüsü
    planned_start_date = Column(Date)
    planned_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    order_item = relationship("OrderItem", backref="production_jobs")
    assigned_operator = relationship("User", foreign_keys=[assigned_operator_id], backref="assigned_jobs")
    creator = relationship("User", foreign_keys=[created_by], backref="created_jobs")

class Lot(Base):
    __tablename__ = "lots"
    id = Column(Integer, primary_key=True)
    lot_number = Column(String(50), unique=True, nullable=False)
    production_job_id = Column(Integer, ForeignKey("production_jobs.id"), nullable=False)
    status = Column(String(20), nullable=False, server_default='olusturuldu')
    shift = Column(String(10))  # vardiya
    operator_id = Column(Integer, ForeignKey("users.id"))
    planned_quantity = Column(Numeric(10, 2))
    actual_quantity = Column(Numeric(10, 2))
    waste_quantity = Column(Numeric(10, 2), server_default='0')
    efficiency_percentage = Column(Numeric(5, 2))
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    production_job = relationship("ProductionJob", backref="lots")
    operator = relationship("User", backref="lots")

class LotLog(Base):
    __tablename__ = "lot_logs"
    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    event_type = Column(String(30), nullable=False)  # olay_tipi
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text)
    photo_ref = Column(String(100))  # fotoğraf referansı
    meta_data = Column(JSONB)  # ek meta veriler
    ip_address = Column(String(45))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    lot = relationship("Lot", backref="logs")
    user = relationship("User", backref="lot_logs")

class DefectWaste(Base):
    __tablename__ = "defects_waste"
    id = Column(Integer, primary_key=True)
    context_type = Column(String(20), nullable=False)  # lot, paket, order
    context_id = Column(Integer, nullable=False)  # bağlam_id
    waste_kg = Column(Numeric(10, 2), nullable=False)
    waste_percentage = Column(Numeric(5, 2))
    reason_code = Column(String(20))  # neden_kodu
    description = Column(Text)
    level = Column(Integer, server_default='1')  # seviye (1 veya 2)
    photo_ref = Column(String(100))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="waste_records")

class Packaging(Base):
    __tablename__ = "packaging"
    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    package_type = Column(String(20), nullable=False)  # koli, rulo, paket
    quantity = Column(Integer, nullable=False)  # adet
    package_weight = Column(Numeric(10, 2))  # kg
    waste_kg = Column(Numeric(10, 2), server_default='0')
    photo_ref = Column(String(100))
    status = Column(String(20), nullable=False, server_default='olusturuldu')
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    lot = relationship("Lot", backref="packages")
    creator = relationship("User", backref="packages")

class WeeklyWeighing(Base):
    __tablename__ = "weekly_weighings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department = Column(String(50))
    week_start_date = Column(Date, nullable=False)
    theoretical_data = Column(JSONB, nullable=False)  # teorik_json
    actual_data = Column(JSONB, nullable=False)  # gerçek_json
    calculated_deviations = Column(JSONB)  # hesaplanan_sapmalar
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="weekly_weighings")

# Indexes for performance
Index('idx_production_jobs_status', ProductionJob.status)
Index('idx_production_jobs_operator', ProductionJob.assigned_operator_id)
Index('idx_lots_status', Lot.status)
Index('idx_lots_production_job', Lot.production_job_id)
Index('idx_lot_logs_lot', LotLog.lot_id)
Index('idx_lot_logs_event_type', LotLog.event_type)
Index('idx_defects_waste_context', DefectWaste.context_type, DefectWaste.context_id)