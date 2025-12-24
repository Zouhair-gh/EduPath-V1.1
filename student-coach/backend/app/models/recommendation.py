from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.config.database import Base


class Recommendation(Base):
    __tablename__ = 'recommendations'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    title = Column(String(255), nullable=False)
    description = Column(String)
    url = Column(String(500))
    kind = Column(String(50))  # video, exercise, article
    created_at = Column(DateTime, default=datetime.utcnow)
