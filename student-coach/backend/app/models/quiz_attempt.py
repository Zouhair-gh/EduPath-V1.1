from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime
from app.config.database import Base
from sqlalchemy.orm import relationship

class QuizAttempt(Base):
    __tablename__ = 'quiz_attempts'
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), index=True, nullable=False)
    score = Column(Integer, nullable=False, default=0)
    total_points = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    quiz = relationship('Quiz')
    answers = relationship('QuizAnswer', back_populates='attempt', cascade='all, delete-orphan')
