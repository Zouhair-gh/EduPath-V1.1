from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class PredictRequest(BaseModel):
    student_id: Optional[int] = None
    course_id: Optional[int] = None
    module_id: Optional[int] = None
    features: Optional[Dict[str, float]] = None

class PredictResponse(BaseModel):
    prediction_id: Optional[int]
    student_id: int
    course_id: Optional[int]
    module_id: Optional[int]
    probability_fail: float
    predicted_class: int
    model_version: str

class BatchItem(BaseModel):
    student_id: int
    course_id: Optional[int]
    module_id: Optional[int]
    features: Dict[str, float]

class BatchResponse(BaseModel):
    predictions: List[PredictResponse]

class Alert(BaseModel):
    id: int
    prediction_id: int
    student_id: int
    course_id: Optional[int]
    severity: str
    risk_factors: List[str]
    recommended_actions: List[str]
    status: str
    created_at: Optional[str]

class ExplainResponse(BaseModel):
    prediction_id: int
    top_features: List[Dict[str, float]]

class ModelMetadata(BaseModel):
    id: int
    model_name: str
    version: str
    mlflow_run_id: str
    stage: str
    metrics: Dict[str, Any]

class PromoteResponse(BaseModel):
    id: int
    stage: str

class PerformanceMetrics(BaseModel):
    auc: float
    f1: float
    precision: float
    recall: float
