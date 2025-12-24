from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalOut

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.get("/", response_model=list[GoalOut])
async def list_goals(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Goal).filter(Goal.student_id == user.student_id).order_by(Goal.deadline.asc()).all()
    return rows

@router.post("/", response_model=GoalOut)
async def create_goal(payload: GoalCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    goal = Goal(
        student_id=user.student_id,
        title=payload.title,
        description=payload.description,
        goal_type=payload.goal_type,
        target_value=payload.target_value,
        start_date=payload.start_date,
        deadline=payload.deadline,
        status='ACTIVE',
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

@router.patch("/{goal_id}", response_model=GoalOut)
async def update_goal(goal_id: int, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.student_id == user.student_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    for k, v in payload.items():
        if hasattr(goal, k):
            setattr(goal, k, v)
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/{goal_id}")
async def delete_goal(goal_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.student_id == user.student_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"status": "deleted"}
