from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.config.database import Base


class StudentProfile(Base):
    __tablename__ = 'student_profiles'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), unique=True)
    engagement_ma7 = Column(Integer, default=50)
    engagement_ma30 = Column(Integer, default=50)
    success_rate = Column(Integer, default=70)
    profile_label = Column(String(100), default='Assidu Moyen')
    last_activity_date = Column(Date)
