from datetime import datetime
from sqlalchemy.orm import Session
from app.models.notification import Notification

class MotivationEngine:
    def __init__(self, db: Session):
        self.db = db

    def generate_motivational_message(self, student_id: int, profile_label: str, recent_activity: dict):
        messages = []
        if profile_label == "Assidu Excellence":
            if recent_activity.get('engagement_trend', 0) > 0:
                messages.append({
                    "type": "praise",
                    "title": "Excellent travail ! 🔥",
                    "message": "Tu maintiens un rythme exceptionnel. Continue comme ça !",
                    "priority": "NORMAL",
                })
        elif profile_label == "En Difficulté":
            days_since_login = recent_activity.get('days_since_login', 0)
            if days_since_login > 5:
                messages.append({
                    "type": "gentle_nudge",
                    "title": "On pense à toi 👋",
                    "message": f"On ne t'a pas vu depuis {days_since_login} jours. Essaie 15 minutes aujourd'hui !",
                    "priority": "HIGH",
                })
            if recent_activity.get('success_rate', 100) < 50:
                messages.append({
                    "type": "support",
                    "title": "Besoin d'aide ? 💪",
                    "message": "On a préparé des ressources pour toi !",
                    "priority": "HIGH",
                })
        elif profile_label == "Procrastinateur":
            upcoming_deadlines = recent_activity.get('upcoming_deadlines', 0)
            if upcoming_deadlines >= 3:
                messages.append({
                    "type": "reminder",
                    "title": "Échéances approchent ⏰",
                    "message": f"Tu as {upcoming_deadlines} activités cette semaine.",
                    "priority": "HIGH",
                })
        streak_days = recent_activity.get('streak_days', 0)
        if streak_days > 0 and streak_days % 7 == 0:
            messages.append({
                "type": "achievement",
                "title": f"Série de {streak_days} jours ! 🎉",
                "message": f"Incroyable ! {streak_days} jours consécutifs !",
                "priority": "NORMAL",
            })

        for msg in messages:
            notification = Notification(
                student_id=student_id,
                type=msg['type'],
                title=msg['title'],
                message=msg['message'],
                priority=msg.get('priority', 'NORMAL'),
                scheduled_for=datetime.utcnow(),
            )
            self.db.add(notification)
        self.db.commit()
        return messages
