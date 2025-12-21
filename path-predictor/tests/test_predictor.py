import numpy as np
from src.models.predictor import Predictor

def test_predictor_fit_cv():
    rng = np.random.RandomState(42)
    X = rng.rand(100, 10)
    y = rng.randint(0, 2, size=100)
    model = Predictor()
    metrics = model.fit_cv(X, y)
    assert 'auc_mean' in metrics
    model.fit(X, y)
    proba = model.predict_proba(X[:5])
    assert proba.shape[0] == 5
