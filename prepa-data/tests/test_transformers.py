import pandas as pd
from src.etl.transformers import remove_outliers_zscore, normalize_grades_to_100

def test_remove_outliers_zscore():
    df = pd.DataFrame({'grade':[10, 12, 11, 99]})
    cleaned = remove_outliers_zscore(df, ['grade'], 3.0)
    assert cleaned['grade'].max() < 99


def test_normalize_grades_to_100():
    df = pd.DataFrame({'grade':[50, 75, 100], 'max_grade':[100,100,100]})
    out = normalize_grades_to_100(df)
    assert out['grade_normalized'].iloc[0] == 50
    assert out['grade_normalized'].iloc[-1] == 100