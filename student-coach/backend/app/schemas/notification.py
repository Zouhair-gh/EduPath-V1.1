from pydantic import BaseModel
from datetime import datetime

class NotificationOut(BaseModel):
  id: int
  type: str
  title: str
  message: str
  action_url: str | None = None
  action_label: str | None = None
  priority: str
  is_read: bool
  scheduled_for: datetime | None = None
  delivered_at: datetime | None = None
  created_at: datetime

  class Config:
    orm_mode = True
