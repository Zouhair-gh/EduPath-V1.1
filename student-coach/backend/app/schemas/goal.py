from pydantic import BaseModel
from datetime import date, datetime

class GoalCreate(BaseModel):
    title: str
    description: str | None = None
    goal_type: str
    target_value: int
    start_date: date
    deadline: date

class GoalOut(BaseModel):
    id: int
    title: str
    description: str | None
    goal_type: str
    target_value: int
    current_value: int
    start_date: date
    deadline: date
    status: str
    completed_at: datetime | None

    class Config:
        orm_mode = True
