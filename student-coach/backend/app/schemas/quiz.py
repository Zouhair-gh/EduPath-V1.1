from pydantic import BaseModel
from typing import List

class QuizAnswerInput(BaseModel):
    question_id: int
    selected_index: int

class QuizSubmit(BaseModel):
    answers: List[QuizAnswerInput]

    class Config:
        from_attributes = True
