from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from ..db import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    code = Column(Text, unique=True, nullable=False)
    description = Column(Text)
    unit_price = Column(Numeric(10, 2))
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

