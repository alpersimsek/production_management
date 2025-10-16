from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date, String, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..db import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    product_type = Column(String(20), nullable=False)  # poset, deterjan, al-sat
    unit = Column(String(10), nullable=False)  # kg, adet, m3
    efficiency = Column(Numeric(5, 2))  # verim yüzdesi
    label_template = Column(JSONB)  # etiket şablonu
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Formula(Base):
    __tablename__ = "formulas"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    version = Column(String(10), nullable=False)
    formula_data = Column(JSONB, nullable=False)  # formül satırları
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date)
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", backref="formulas")