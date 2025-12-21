from typing import List, Optional
from pydantic import BaseModel

class StudentProfile(BaseModel):
    student_id: int
    profile_id: int
    profile_label: str
    confidence_score: float
    model_version: str
    assigned_at: Optional[str] = None

class ProfileDefinition(BaseModel):
    profile_id: int
    label: str
    description: str
    avg_engagement: float
    avg_success_rate: float
    avg_punctuality: float
    student_count: int

class DistributionItem(BaseModel):
    profile_label: str
    count: int
    percentage: float

class Metrics(BaseModel):
    model_version: str
    n_clusters: int
    silhouette_score: float
    inertia: float

class Visualization(BaseModel):
    image_base64: str

class RetrainResponse(BaseModel):
    model_version: str
    n_clusters: int
    silhouette_score: float
    inertia: float
    assigned_count: int
