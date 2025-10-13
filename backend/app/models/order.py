from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date
from sqlalchemy.dialects.postgresql import JSONB
from ..db import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_name = Column(Text, nullable=False)
    customer_email = Column(Text)
    order_date = Column(Date, nullable=False, server_default=func.current_date())
    due_date = Column(Date, nullable=False)
    status = Column(Text, nullable=False, server_default='pending')
    total_amount = Column(Numeric(10, 2))
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

