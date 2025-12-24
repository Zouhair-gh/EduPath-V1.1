from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.config.database import Base

class Achievement(Base):
    __tablename__ = 'achievements'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    achievement_type = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String)
    icon_url = Column(String(500))
    xp_reward = Column(Integer, default=0)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
