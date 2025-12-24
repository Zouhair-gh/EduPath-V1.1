from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.config.database import Base
from sqlalchemy.orm import relationship

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='student', uselist=False)
