from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date
from sqlalchemy.dialects.postgresql import JSONB
from ..db import Base

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(Text)
    entity_type = Column(Text)  # 'order', 'production', 'shipment', etc.
    entity_id = Column(Integer)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

