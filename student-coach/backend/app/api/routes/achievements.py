from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.models.achievement import Achievement

router = APIRouter(prefix="/achievements", tags=["Achievements"])

@router.get("/")
async def list_achievements(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Achievement).filter(Achievement.student_id == user.student_id).order_by(Achievement.unlocked_at.desc()).all()
    return rows
