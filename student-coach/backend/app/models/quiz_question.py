from sqlalchemy import Column, Integer, String, ForeignKey
from app.config.database import Base
from sqlalchemy.orm import relationship

class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), index=True, nullable=False)
    prompt = Column(String(1000), nullable=False)
    options_json = Column(String(4000), nullable=False)  # JSON-encoded list of options
    correct_index = Column(Integer, nullable=False, default=0)
    points = Column(Integer, nullable=False, default=1)

    quiz = relationship('Quiz', back_populates='questions')
