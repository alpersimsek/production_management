from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from ..db import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    permissions = Column(JSONB, nullable=False, server_default='{}')

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

