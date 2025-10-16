from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, Numeric, Date, String, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from ..db import Base
import uuid

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    reference_type = Column(String(20), nullable=False)  # ref_türü
    reference_id = Column(Integer, nullable=False)  # ref_id
    file_path = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    schema_version = Column(String(10), server_default='1.0')
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    uploader = relationship("User", backref="attachments")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module = Column(String(30), nullable=False)
    action = Column(String(30), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="audit_logs")

# Indexes for performance
Index('idx_attachments_reference', Attachment.reference_type, Attachment.reference_id)
Index('idx_audit_logs_user_module', AuditLog.user_id, AuditLog.module)