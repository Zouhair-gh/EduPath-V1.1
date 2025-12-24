from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.config.database import Base

class LessonQuiz(Base):
    __tablename__ = 'lesson_quizzes'
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='CASCADE'), index=True, nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), index=True, nullable=False)

    __table_args__ = (UniqueConstraint('lesson_id', 'quiz_id', name='uq_lesson_quiz'),)
