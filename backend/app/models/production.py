from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date
from sqlalchemy.dialects.postgresql import JSONB
from ..db import Base

class ProductionJob(Base):
    __tablename__ = "production_jobs"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    status = Column(Text, nullable=False, server_default='pending')
    start_date = Column(Date)
    end_date = Column(Date)
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

