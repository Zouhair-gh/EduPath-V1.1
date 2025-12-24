from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from datetime import datetime
from app.config.database import Base

class InteractionEvent(Base):
    __tablename__ = 'interaction_events'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), index=True, nullable=False)
    event_type = Column(String(50), index=True, nullable=False)
    value = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
