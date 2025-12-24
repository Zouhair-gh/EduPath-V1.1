from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.models.student import Student
from app.models.interaction_event import InteractionEvent
from app.models.achievement import Achievement
from app.models.notification import Notification

router = APIRouter(prefix="/student", tags=["Interactions"])

class InteractionCreate(BaseModel):
    type: str
    value: Optional[int] = None
    details: Optional[Dict[str, object]] = None

    class Config:
        from_attributes = True

@router.post("/interactions")
async def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(Student).get(user.student_id) if user.student_id else None
    if not student:
        return {"ok": False, "error": "student_not_found"}
    ev = InteractionEvent(
        student_id=student.id,
        event_type=payload.type,
        value=payload.value,
        details=payload.details,
    )
    db.add(ev)
    db.commit()
    # If check-in, evaluate streak achievements (7/30 days) and notify
    if payload.type == 'check_in':
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        # Collect check-ins for last 30 days
        events = db.query(InteractionEvent).filter(
            InteractionEvent.student_id == student.id,
            InteractionEvent.event_type == 'check_in',
        ).all()
        dates = {e.created_at.date() for e in events}
        # Compute streak from today backwards
        streak = 0
        tmp = today
        while tmp in dates:
            streak += 1
            tmp = tmp - timedelta(days=1)
            if streak > 365:
                break
        # Unlock achievements at 7 and 30 days
        def ensure_achievement(kind: str, title: str, desc: str, xp: int):
            exists = db.query(Achievement).filter(Achievement.student_id == student.id, Achievement.achievement_type == kind).first()
            if not exists:
                ach = Achievement(student_id=student.id, achievement_type=kind, title=title, description=desc, xp_reward=xp)
                db.add(ach)
                db.add(Notification(student_id=student.id, type='achievement', title=title, message=desc, priority='HIGH'))
                db.commit()
        if streak >= 7:
            ensure_achievement('streak_7', 'Streak 7 jours', "Bravo ! 7 jours d'affilée.", 50)
        if streak >= 30:
            ensure_achievement('streak_30', 'Streak 30 jours', "Incroyable ! 30 jours d'affilée.", 200)
    return {"ok": True, "id": ev.id}
