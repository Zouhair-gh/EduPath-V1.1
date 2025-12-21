import os
from typing import Dict, Any, Tuple
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score
import mlflow
import mlflow.xgboost

XGB_PARAMS: Dict[str, Any] = {
    'n_estimators': 200,
    'max_depth': 6,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'objective': 'binary:logistic',
    'eval_metric': 'auc',
    'random_state': 42
}

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")


class Predictor:
    def __init__(self, params: Dict[str, Any] | None = None):
        self.params = params or XGB_PARAMS
        self.model = XGBClassifier(**self.params)
        self.feature_names: list[str] = []

    def fit_cv(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        aucs, f1s, ps, rs = [], [], [], []
        for train_idx, test_idx in skf.split(X, y):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            self.model.fit(X_train, y_train)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]
            y_pred = (y_pred_proba >= 0.5).astype(int)
            aucs.append(roc_auc_score(y_test, y_pred_proba))
            f1s.append(f1_score(y_test, y_pred))
            ps.append(precision_score(y_test, y_pred, zero_division=0))
            rs.append(recall_score(y_test, y_pred))
        return {
            'auc_mean': float(np.mean(aucs)),
            'f1_mean': float(np.mean(f1s)),
            'precision_mean': float(np.mean(ps)),
            'recall_mean': float(np.mean(rs)),
        }

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

    def predict_class(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X) >= threshold).astype(int)

    def log_to_mlflow(self, metrics: Dict[str, float]) -> Tuple[str, str]:
        with mlflow.start_run() as run:
            mlflow.log_params(self.params)
            for k, v in metrics.items():
                mlflow.log_metric(k, v)
            mlflow.xgboost.log_model(self.model, 'model')
            return run.info.run_id, run.info.run_uuid if hasattr(run.info, 'run_uuid') else run.info.run_id
