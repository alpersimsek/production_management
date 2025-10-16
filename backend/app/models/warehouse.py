from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date, String, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..db import Base

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    capacity_m3 = Column(Numeric(10, 2))
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class WarehouseReceipt(Base):
    __tablename__ = "warehouse_receipts"
    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey("packaging.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    weight_kg = Column(Numeric(10, 2), nullable=False)
    receipt_date = Column(Date, nullable=False, server_default=func.current_date())
    receipt_time = Column(TIMESTAMP(timezone=True), server_default=func.now())
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    photo_ref = Column(String(100))
    status = Column(String(20), nullable=False, server_default='kabul_bekliyor')
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    package = relationship("Packaging", backref="warehouse_receipts")
    warehouse = relationship("Warehouse", backref="receipts")
    approver = relationship("User", backref="warehouse_receipts")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("lots.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(10), nullable=False)
    movement_type = Column(String(20), nullable=False)  # giris, cikis, sayim, transfer
    reference_id = Column(Integer)  # referans ID (order, shipment, etc.)
    reference_type = Column(String(20))  # order, shipment, count, etc.
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", backref="inventory")
    lot = relationship("Lot", backref="inventory")
    warehouse = relationship("Warehouse", backref="inventory")
    creator = relationship("User", backref="inventory_movements")

# Indexes for performance
Index('idx_inventory_product_warehouse', Inventory.product_id, Inventory.warehouse_id)