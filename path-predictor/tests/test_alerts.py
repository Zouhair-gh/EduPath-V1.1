from src.models.alert_engine import severity_from_fail_proba

def test_severity_thresholds():
    assert severity_from_fail_proba(0.8) == 'HIGH'
    assert severity_from_fail_proba(0.6) == 'MEDIUM'
    assert severity_from_fail_proba(0.3) == 'LOW'
