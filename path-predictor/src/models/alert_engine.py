import os
from typing import Dict, Any, List

TH_HIGH = float(os.getenv("ALERT_THRESHOLD_HIGH", "0.70"))
TH_MED = float(os.getenv("ALERT_THRESHOLD_MEDIUM", "0.50"))


def severity_from_fail_proba(p: float) -> str:
    if p > TH_HIGH:
        return 'HIGH'
    if p > TH_MED:
        return 'MEDIUM'
    return 'LOW'


def build_risk_factors(features: Dict[str, float], shap_top: List[Dict[str, float]]) -> List[str]:
    items: List[str] = []
    for item in shap_top:
        fname = item['feature']
        sval = item['shap_value']
        fval = features.get(fname)
        items.append(f"{fname} ({fval}) shap={sval:.3f}")
    return items


def recommended_actions(severity: str) -> List[str]:
    if severity == 'HIGH':
        return [
            'Schedule tutor session',
            'Send motivational message',
            'Assign remedial exercises',
        ]
    if severity == 'MEDIUM':
        return [
            'Encourage forum participation',
            'Monitor attendance next 2 weeks',
        ]
    return ['No immediate action; continue monitoring']
