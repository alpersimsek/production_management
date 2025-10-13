from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date
from sqlalchemy.dialects.postgresql import JSONB
from ..db import Base

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    tracking_number = Column(Text)
    carrier = Column(Text)
    status = Column(Text, nullable=False, server_default='pending')
    shipped_date = Column(Date)
    estimated_delivery = Column(Date)
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

