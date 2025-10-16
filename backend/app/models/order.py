from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date, String, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..db import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    tax_number = Column(String(20))
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_number = Column(String(20), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    salesperson_id = Column(Integer, ForeignKey("users.id"))  # plasiyer
    status = Column(String(20), nullable=False, server_default='taslak')
    order_date = Column(Date, nullable=False, server_default=func.current_date())
    due_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(12, 2))
    discount_amount = Column(Numeric(12, 2), server_default='0')
    markup_amount = Column(Numeric(12, 2), server_default='0')  # bindirim
    fuel_cost = Column(Numeric(10, 2), server_default='0')  # yakıt gideri
    profitability = Column(Numeric(10, 2))  # karlılık
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", backref="orders")
    salesperson = relationship("User", foreign_keys=[salesperson_id], backref="sales_orders")
    creator = relationship("User", foreign_keys=[created_by], backref="created_orders")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    delivery_status = Column(String(20), server_default='beklemede')
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", backref="items")
    product = relationship("Product", backref="order_items")

# Indexes for performance
Index('idx_orders_status', Order.status)
Index('idx_orders_due_date', Order.due_date)
Index('idx_orders_customer', Order.customer_id)