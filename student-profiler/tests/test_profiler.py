from src.models.profiler import interpret_cluster

def test_interpretation_rules():
    cid, label, _ = interpret_cluster(85, 90, 95)
    assert cid == 0 and "Assidu" in label
    cid, label, _ = interpret_cluster(65, 70, 75)
    assert cid in (1, 2)
    cid, label, _ = interpret_cluster(25, 35, 30)
    assert cid == 4
