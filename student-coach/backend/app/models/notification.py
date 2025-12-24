from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.config.database import Base

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(String, nullable=False)
    action_url = Column(String(500))
    action_label = Column(String(100))
    priority = Column(String(20), default='NORMAL')
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    scheduled_for = Column(DateTime)
    delivered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
