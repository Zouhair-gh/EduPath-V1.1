from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.config.database import Base
from sqlalchemy.orm import relationship

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    teacher_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lessons = relationship('Lesson', back_populates='course', cascade='all, delete-orphan')
