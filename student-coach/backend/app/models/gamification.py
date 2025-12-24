from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from datetime import datetime
from app.config.database import Base

class StudentGamification(Base):
    __tablename__ = 'student_gamification'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), unique=True)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_activity_date = Column(Date)
    badges_count = Column(Integer, default=0)
    goals_completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
