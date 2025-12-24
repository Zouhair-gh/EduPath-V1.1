from sqlalchemy import Column, Integer, String, ForeignKey
from app.config.database import Base
from sqlalchemy.orm import relationship

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    content_url = Column(String(1000), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)

    course = relationship('Course', back_populates='lessons')
