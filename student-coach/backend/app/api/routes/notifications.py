from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.models.notification import Notification
from app.schemas.notification import NotificationOut
from datetime import datetime

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=list[NotificationOut])
async def list_notifications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Notification).filter(Notification.student_id == user.student_id).order_by(Notification.created_at.desc()).limit(100).all()
    return rows

@router.patch("/{notification_id}/read")
async def mark_read(notification_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == notification_id, Notification.student_id == user.student_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification introuvable")
    n.is_read = True
    n.read_at = datetime.utcnow()
    db.commit()
    return {"success": True}

@router.post("/mark-all-read")
async def mark_all_read(db: Session = Depends(get_db), user=Depends(get_current_user)):
    db.query(Notification).filter(Notification.student_id == user.student_id, Notification.is_read == False).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()
    return {"success": True}
