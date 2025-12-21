import os
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File
from sqlalchemy import text
import numpy as np
import json
import csv
import io

from ..config.database import ensure_schema, fetch_features, insert_predictions, insert_alerts, get_current_model, set_model_stage, get_alerts
from ..config.database import FEATURE_COLUMNS
from ..config.mlflow_config import setup_mlflow
from ..models.predictor import Predictor
from ..models.explainer import Explainer
from ..models.alert_engine import severity_from_fail_proba, build_risk_factors, recommended_actions
from ..utils.feature_engineering import to_matrix, single_to_vector
from .schemas import PredictRequest, PredictResponse, BatchItem, BatchResponse, Alert, ExplainResponse, ModelMetadata, PromoteResponse

router = APIRouter(prefix="/api", tags=["path-predictor"])

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")

_model: Predictor | None = None
_explainer: Explainer | None = None


@router.on_event("startup")
async def startup_event():
    import threading
    def init():
        try:
            ensure_schema()
        except Exception as e:
            print(f"[WARN] ensure_schema skipped: {e}")
        try:
            setup_mlflow()
        except Exception as e:
            print(f"[WARN] MLflow setup skipped: {e}")
    threading.Thread(target=init, daemon=True).start()


def _ensure_model():
    global _model, _explainer
    if _model is None:
        # Train a simple baseline if not available from DB
        rows = fetch_features()
        rows = [r for r in rows if r.get('passed') is not None]
        if not rows:
            _model = Predictor()
            # create dummy model with zeros
            X = np.zeros((10, len(FEATURE_COLUMNS)))
            y = np.zeros(10)
            _model.fit(X, y)
        else:
            X = to_matrix(rows)
            y = np.array([int(r['passed']) for r in rows], dtype=int)
            _model = Predictor()
            _model.fit(X, y)
        _explainer = Explainer(_model.model)


@router.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    _ensure_model()
    if req.features:
        vec = single_to_vector(req.features)
    else:
        rows = fetch_features()
        row = next((r for r in rows if (req.student_id is not None and int(r['student_id']) == int(req.student_id))), None)
        if not row:
            raise HTTPException(status_code=400, detail="Features not found for student; provide features in request")
        vec = single_to_vector(row)
    proba = float(_model.predict_proba(vec.reshape(1, -1))[0])
    pred_class = int(proba >= 0.5)
    record = {
        'student_id': req.student_id or int(req.features.get('student_id', 0)),
        'course_id': req.course_id,
        'module_id': req.module_id,
        'prediction_proba': round(proba, 4),
        'prediction_class': pred_class,
        'model_version': MODEL_VERSION,
    }
    ids = insert_predictions([record])
    pid = ids[0] if ids else None

    # Alert generation
    sev = severity_from_fail_proba(proba)
    shap_top = _explainer.explain_instance(vec, FEATURE_COLUMNS, top_k=3)
    rf = build_risk_factors({c: float(vec[i]) for i, c in enumerate(FEATURE_COLUMNS)}, shap_top)
    ra = recommended_actions(sev)
    insert_alerts([{
        'prediction_id': pid,
        'student_id': record['student_id'],
        'course_id': record['course_id'],
        'severity': sev,
        'risk_factors': json.dumps(rf),
        'recommended_actions': json.dumps(ra),
    }])

    return PredictResponse(
        prediction_id=pid,
        student_id=record['student_id'],
        course_id=record['course_id'],
        module_id=record['module_id'],
        probability_fail=proba,
        predicted_class=pred_class,
        model_version=MODEL_VERSION,
    )


@router.post("/predict/batch", response_model=BatchResponse)
async def predict_batch(file: UploadFile = File(...)):
    _ensure_model()
    content = await file.read()
    text_stream = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(text_stream)
    items: List[BatchItem] = []
    for row in reader:
        features = {c: float(row.get(c, 0.0)) for c in FEATURE_COLUMNS}
        items.append(BatchItem(
            student_id=int(row.get('student_id', 0)),
            course_id=int(row.get('course_id', 0)) if row.get('course_id') else None,
            module_id=int(row.get('module_id', 0)) if row.get('module_id') else None,
            features=features,
        ))
    preds: List[PredictResponse] = []
    for it in items:
        vec = single_to_vector(it.features)
        proba = float(_model.predict_proba(vec.reshape(1, -1))[0])
        pred_class = int(proba >= 0.5)
        record = {
            'student_id': it.student_id,
            'course_id': it.course_id,
            'module_id': it.module_id,
            'prediction_proba': round(proba, 4),
            'prediction_class': pred_class,
            'model_version': MODEL_VERSION,
        }
        ids = insert_predictions([record])
        pid = ids[0] if ids else None
        preds.append(PredictResponse(
            prediction_id=pid,
            student_id=it.student_id,
            course_id=it.course_id,
            module_id=it.module_id,
            probability_fail=proba,
            predicted_class=pred_class,
            model_version=MODEL_VERSION,
        ))
    return BatchResponse(predictions=preds)


@router.get("/alerts")
async def alerts(severity: str | None = None):
    return get_alerts(severity)


@router.get("/explain/{prediction_id}", response_model=ExplainResponse)
async def explain_prediction(prediction_id: int):
    # For simplicity, re-compute explanation using latest features for student
    rows = fetch_features()
    if not rows:
        raise HTTPException(status_code=404, detail="No features available")
    row = rows[0]
    vec = single_to_vector(row)
    _ensure_model()
    top = _explainer.explain_instance(vec, FEATURE_COLUMNS, top_k=3)
    return ExplainResponse(prediction_id=prediction_id, top_features=top)


@router.get("/models/current", response_model=ModelMetadata)
async def current_model():
    m = get_current_model()
    if not m:
        raise HTTPException(status_code=404, detail="No production model")
    return ModelMetadata(
        id=int(m['id']),
        model_name=m['model_name'],
        version=m['version'],
        mlflow_run_id=m['mlflow_run_id'],
        stage=m['stage'],
        metrics=m['metrics'] if isinstance(m['metrics'], dict) else {},
    )


@router.post("/models/promote/{model_id}", response_model=PromoteResponse)
async def promote_model(model_id: int):
    set_model_stage(model_id, 'PRODUCTION')
    return PromoteResponse(id=model_id, stage='PRODUCTION')


@router.get("/metrics/performance")
async def performance():
    return {"message": "Metrics logged to MLflow; query MLflow UI for details."}
