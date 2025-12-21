import numpy as np
from src.models.clusterer import ClusterPipeline

def test_pipeline_fit_predict():
    X = np.random.RandomState(42).rand(100, 6)
    pipe = ClusterPipeline(n_clusters=5, pca_components=2)
    labels, sil, inertia = pipe.fit(X)
    assert len(labels) == X.shape[0]
    assert sil >= 0.0
    preds = pipe.predict(X)
    assert preds.shape == labels.shape
