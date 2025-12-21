from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Resource(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    resource_type: Optional[str] = None
    subject: Optional[str] = None
    difficulty_level: Optional[str] = None
    url: Optional[str] = None
    tags: Optional[List[str]] = None

class Recommendation(BaseModel):
    resource_id: int
    title: str
    description: Optional[str]
    difficulty_level: Optional[str]
    url: Optional[str]
    score: float

class FeedbackRequest(BaseModel):
    recommendation_id: int
    student_id: int
    action: str
    time_spent_seconds: Optional[int] = None

class SearchResponse(BaseModel):
    results: List[Resource]

class RecommendationsResponse(BaseModel):
    student_id: int
    recommendations: List[Recommendation]

class MetricsResponse(BaseModel):
    total_recommendations: int
    total_feedback: int
    click_through_rate: float
