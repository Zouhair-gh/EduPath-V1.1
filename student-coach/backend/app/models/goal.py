from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from datetime import datetime
from app.config.database import Base

class Goal(Base):
    __tablename__ = 'goals'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    title = Column(String(255), nullable=False)
    description = Column(String)
    goal_type = Column(String(50), nullable=False)
    target_value = Column(Integer, nullable=False)
    current_value = Column(Integer, default=0)
    start_date = Column(Date, nullable=False)
    deadline = Column(Date, nullable=False)
    status = Column(String(20), default='ACTIVE')
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
