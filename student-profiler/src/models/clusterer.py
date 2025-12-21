import os
from typing import Tuple, Dict, Any
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

N_CLUSTERS = int(os.getenv("N_CLUSTERS", "5"))
PCA_COMPONENTS = int(os.getenv("PCA_COMPONENTS", "2"))
RANDOM_STATE = 42


class ClusterPipeline:
    def __init__(self, n_clusters: int = N_CLUSTERS, pca_components: int = PCA_COMPONENTS):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=pca_components, random_state=RANDOM_STATE)
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=RANDOM_STATE, n_init="auto")

    def fit(self, X: np.ndarray) -> Tuple[np.ndarray, float, float]:
        X_scaled = self.scaler.fit_transform(X)
        X_pca = self.pca.fit_transform(X_scaled)
        labels = self.kmeans.fit_predict(X_pca)
        sil = silhouette_score(X_pca, labels) if len(set(labels)) > 1 else 0.0
        inertia = float(self.kmeans.inertia_)
        return labels, sil, inertia

    def transform_distances(self, X: np.ndarray) -> np.ndarray:
        X_scaled = self.scaler.transform(X)
        X_pca = self.pca.transform(X_scaled)
        return self.kmeans.transform(X_pca)

    def predict(self, X: np.ndarray) -> np.ndarray:
        X_scaled = self.scaler.transform(X)
        X_pca = self.pca.transform(X_scaled)
        return self.kmeans.predict(X_pca)

    def project(self, X: np.ndarray) -> np.ndarray:
        """Project original features into PCA space used by the model."""
        X_scaled = self.scaler.transform(X)
        return self.pca.transform(X_scaled)

    def centroids_original_space(self, X: np.ndarray, labels: np.ndarray) -> Dict[int, np.ndarray]:
        # Compute centroids in original feature space using label groups
        centroids: Dict[int, np.ndarray] = {}
        for cid in sorted(set(labels)):
            centroids[cid] = np.mean(X[labels == cid], axis=0)
        return centroids

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "n_clusters": int(self.kmeans.n_clusters),
            "pca_components": int(self.pca.n_components_),
            "random_state": RANDOM_STATE,
        }
