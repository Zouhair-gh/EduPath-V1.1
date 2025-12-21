import pandas as pd
import numpy as np
from datetime import timedelta


def moving_averages(df: pd.DataFrame, value_col: str, window: int):
    return df[value_col].rolling(window=window, min_periods=1).mean()


def linear_trend(df: pd.DataFrame, value_col: str):
    # simple linear regression slope on last 30 points
    y = df[value_col].astype(float).values
    x = np.arange(len(y))
    if len(y) < 2:
        return 0.0
    x_mean = x.mean(); y_mean = y.mean()
    num = ((x - x_mean) * (y - y_mean)).sum()
    den = ((x - x_mean)**2).sum() + 1e-9
    return float(num / den)


def compute_temporal_features(daily_df: pd.DataFrame) -> pd.DataFrame:
    df = daily_df.copy()
    df = df.sort_values('feature_date')
    df['engagement_ma7'] = moving_averages(df, 'engagement', 7)
    df['engagement_ma30'] = moving_averages(df, 'engagement', 30)
    df['grade_ma7'] = moving_averages(df, 'grade', 7)
    df['grade_ma30'] = moving_averages(df, 'grade', 30)
    df['engagement_trend'] = linear_trend(df, 'engagement')
    # weekly pattern: fraction per day of week
    pattern = df.groupby(df['feature_date'].dt.day_name())['engagement'].sum()
    total = pattern.sum() or 1.0
    activity_pattern = {day: float(val/total) for day, val in pattern.to_dict().items()}
    df['activity_pattern'] = [activity_pattern]*len(df)
    return df[['student_id','course_id','feature_date','engagement_ma7','engagement_ma30','grade_ma7','grade_ma30','engagement_trend','activity_pattern']]