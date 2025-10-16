from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..db import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    permissions = Column(JSONB, nullable=False, server_default='{}')
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default='true')
    phone = Column(String(20))
    department = Column(String(50))  # Üretim, Paketleme, Depo, Sevkiyat, Plasiyer
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_login = Column(TIMESTAMP(timezone=True))
    
    # Relationships
    role = relationship("Role", backref="users")