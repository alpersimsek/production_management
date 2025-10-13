from sqlalchemy import Column, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from ..db import Base

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(Text, unique=True, nullable=False)
    value = Column(JSONB, nullable=False)

