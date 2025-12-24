from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.config.database import Base


class RecommendationFeedback(Base):
    __tablename__ = 'recommendations_feedback'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    recommendation_id = Column(Integer, ForeignKey('recommendations.id'))
    action = Column(String(20), nullable=False)  # clicked, completed, liked, dismissed, saved
    time_spent_seconds = Column(Integer)
    rating = Column(Integer)
    feedback_text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
