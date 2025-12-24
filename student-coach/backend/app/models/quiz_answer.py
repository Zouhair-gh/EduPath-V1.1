from sqlalchemy import Column, Integer, ForeignKey
from app.config.database import Base
from sqlalchemy.orm import relationship

class QuizAnswer(Base):
    __tablename__ = 'quiz_answers'
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey('quiz_attempts.id', ondelete='CASCADE'), index=True, nullable=False)
    question_id = Column(Integer, ForeignKey('quiz_questions.id', ondelete='CASCADE'), index=True, nullable=False)
    selected_index = Column(Integer, nullable=False, default=0)
    is_correct = Column(Integer, nullable=False, default=0)  # 0/1

    attempt = relationship('QuizAttempt', back_populates='answers')
