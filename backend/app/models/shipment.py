from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date, String, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..db import Base

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    shipment_number = Column(String(20), unique=True, nullable=False)
    status = Column(String(20), nullable=False, server_default='planlandi')
    planned_date = Column(Date, nullable=False)
    vehicle_capacity_m3 = Column(Numeric(10, 2))
    route_data = Column(JSONB)  # rota_json
    driver_name = Column(String(100))
    driver_phone = Column(String(20))
    vehicle_plate = Column(String(20))
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", backref="shipments")

class ShipmentItem(Base):
    __tablename__ = "shipment_items"
    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("packaging.id"), nullable=False)
    sequence = Column(Integer)  # sıra
    volume_m3 = Column(Numeric(10, 2))
    weight_kg = Column(Numeric(10, 2))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    shipment = relationship("Shipment", backref="items")
    package = relationship("Packaging", backref="shipment_items")