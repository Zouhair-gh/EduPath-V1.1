from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db, get_current_user
from app.models.recommendation import Recommendation

router = APIRouter(prefix="/student/recommendations", tags=["Recommendations"])

@router.get("/", response_model=List[dict])
async def list_recommendations(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Recommendation).filter(Recommendation.student_id == user.student_id).order_by(Recommendation.created_at.desc()).limit(20).all()
    return [{
        "id": r.id,
        "title": r.title,
        "description": r.description,
        "url": r.url,
        "kind": r.kind,
        "created_at": r.created_at,
    } for r in rows]
