from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.config.database import Base

class AchievementDefinition(Base):
    __tablename__ = 'achievement_definitions'
    id = Column(Integer, primary_key=True)
    achievement_type = Column(String(50), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String)
    icon_url = Column(String(500))
    xp_reward = Column(Integer, default=0)
    criteria = Column(String)  # JSON stored as text for simplicity
    created_at = Column(DateTime, default=datetime.utcnow)
