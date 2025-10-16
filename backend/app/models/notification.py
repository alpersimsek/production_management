from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func, String, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..db import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # info, warning, error, success
    is_read = Column(Boolean, nullable=False, server_default='false')
    data = Column(JSONB)  # Additional data for the notification
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    read_at = Column(TIMESTAMP(timezone=True))
    
    # Relationships
    user = relationship("User", backref="notifications")

# Indexes for performance
Index('idx_notifications_user', Notification.user_id)
Index('idx_notifications_type', Notification.notification_type)
Index('idx_notifications_read', Notification.is_read)
Index('idx_notifications_created', Notification.created_at)
