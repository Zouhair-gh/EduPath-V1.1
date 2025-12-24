from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from datetime import datetime
from app.config.database import Base

class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), index=True, nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), index=True, nullable=False)
    status = Column(String(50), nullable=False, default='ACTIVE')
    enrolled_at = Column(DateTime, default=datetime.utcnow)
