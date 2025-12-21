import pandas as pd
import numpy as np


def detect_zscore_anomalies(df: pd.DataFrame, col: str, threshold: float = 3.0) -> pd.Series:
    if col not in df.columns:
        return pd.Series([False]*len(df))
    z = (df[col] - df[col].mean()) / (df[col].std(ddof=0) + 1e-9)
    return np.abs(z) > threshold


def detect_iqr_outliers(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([False]*len(df))
    q1 = df[col].quantile(0.25); q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    return (df[col] < (q1 - 1.5*iqr)) | (df[col] > (q3 + 1.5*iqr))


def detect_absence(df: pd.DataFrame, ts_col: str = 'timestamp', days: int = 7) -> pd.Series:
    if ts_col not in df.columns:
        return pd.Series([False]*len(df))
    ts = pd.to_datetime(df[ts_col], errors='coerce')
    last = ts.max()
    return pd.Series([pd.isna(t) or (last - t).days >= days for t in ts])


def summarize_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    flags = pd.DataFrame()
    flags['spike_activity'] = detect_zscore_anomalies(df, 'activity', threshold=3.0)
    flags['outlier_grade'] = detect_iqr_outliers(df, 'grade')
    flags['absence_7d'] = detect_absence(df, 'timestamp', days=7)
    flags['type'] = flags.apply(lambda r: 'spike' if r['spike_activity'] else ('absence' if r['absence_7d'] else ('grade_outlier' if r['outlier_grade'] else 'none')), axis=1)
    flags['severity'] = flags.apply(lambda r: 'high' if r['spike_activity'] or r['absence_7d'] else ('medium' if r['outlier_grade'] else 'low'), axis=1)
    return flags