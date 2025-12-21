import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from ..utils.logger import logger
from ..config.settings import settings


def remove_outliers_zscore(df: pd.DataFrame, cols: list, z_thresh: float):
    for c in cols:
        if c in df.columns:
            z = (df[c] - df[c].mean()) / (df[c].std(ddof=0) + 1e-9)
            df = df[np.abs(z) <= z_thresh]
    return df


def normalize_grades_to_100(grades_df: pd.DataFrame, grade_col: str = 'grade', max_possible_col: str = 'max_grade'):
    df = grades_df.copy()
    # Guard: if no grade column or empty, create placeholder and return
    if grade_col not in df.columns or df.empty:
        df['grade_normalized'] = 0.0
        return df
    # If max_possible not present, use MinMaxScaler
    if max_possible_col not in df.columns:
        scaler = MinMaxScaler(feature_range=(0, 100))
        df['grade_normalized'] = scaler.fit_transform(df[[grade_col]].astype(float))
    else:
        # avoid division by zero
        denom = df[max_possible_col].astype(float).replace(0, np.nan)
        df['grade_normalized'] = (df[grade_col].astype(float) / denom) * 100.0
        df['grade_normalized'] = df['grade_normalized'].fillna(0.0)
    df['grade_normalized'] = df['grade_normalized'].clip(lower=0, upper=100)
    return df


def standardize_timestamps(activity_df: pd.DataFrame, ts_col: str = 'timestamp'):
    df = activity_df.copy()
    if ts_col in df.columns:
        df[ts_col] = pd.to_datetime(df[ts_col], errors='coerce', utc=True)
    return df


def clean_and_transform(df_map: dict):
    logger.info("Cleaning data: removing duplicates, handling missing, outliers")
    # Drop duplicates
    for name, df in df_map.items():
        df_map[name] = df.drop_duplicates()

    # Handle missing: Simple forward/backward fill where reasonable
    for name in ['grades', 'activity']:
        if name in df_map:
            df_map[name] = df_map[name].fillna(method='ffill').fillna(method='bfill')

    # Remove outliers in time_spent or score if exists
    for name, cols in [('activity', ['time_spent']), ('grades', ['grade'])]:
        if name in df_map:
            df_map[name] = remove_outliers_zscore(df_map[name], cols, settings.OUTLIER_THRESHOLD)

    # Normalize grades
    if 'grades' in df_map:
        df_map['grades'] = normalize_grades_to_100(df_map['grades'])

    # Standardize timestamps
    if 'activity' in df_map:
        df_map['activity'] = standardize_timestamps(df_map['activity'])

    return df_map