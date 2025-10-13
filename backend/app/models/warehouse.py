from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date
from sqlalchemy.dialects.postgresql import JSONB
from ..db import Base

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    code = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    location = Column(Text)
    capacity = Column(Numeric(10, 2))
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

