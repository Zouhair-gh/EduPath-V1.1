from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime
from app.config.database import Base

class StudentLessonProgress(Base):
    __tablename__ = 'student_lesson_progress'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), index=True, nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), index=True, nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='CASCADE'), index=True, nullable=False)
    is_unlocked = Column(Integer, nullable=False, default=0)  # 0/1
    quiz_passed = Column(Integer, nullable=False, default=0)  # 0/1
    completed_at = Column(DateTime, nullable=True)
