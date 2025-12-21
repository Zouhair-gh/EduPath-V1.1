from typing import List, Dict, Any
import numpy as np
import shap

class Explainer:
    def __init__(self, model):
        self.explainer = shap.TreeExplainer(model)

    def explain_instance(self, X_row: np.ndarray, feature_names: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        shap_values = self.explainer.shap_values(X_row.reshape(1, -1))
        # shap returns array; take for positive class if list
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        vals = shap_values.flatten()
        indices = np.argsort(np.abs(vals))[::-1][:top_k]
        results: List[Dict[str, Any]] = []
        for idx in indices:
            results.append({
                'feature': feature_names[idx],
                'shap_value': float(vals[idx])
            })
        return results
