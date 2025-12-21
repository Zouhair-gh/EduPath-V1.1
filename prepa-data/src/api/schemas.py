from pydantic import BaseModel
from typing import Optional, List

class StudentMetric(BaseModel):
    student_id: int
    course_id: int
    engagement_score: float
    success_rate: float
    punctuality_score: float

class CourseMetric(BaseModel):
    course_id: int
    avg_engagement: float
    avg_success_rate: float

class PipelineStatus(BaseModel):
    run_id: str
    status: str
    records_processed: int
    records_failed: int

class TemporalFeature(BaseModel):
    student_id: int
    course_id: int
    feature_date: str
    engagement_ma7: float
    engagement_ma30: float
    grade_ma7: float
    grade_ma30: float
    engagement_trend: float
