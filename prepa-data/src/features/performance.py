import pandas as pd


def compute_performance(metrics_df: pd.DataFrame) -> pd.DataFrame:
    df = metrics_df.copy()
    df['passed_activities'] = df.get('passed_activities', 0)
    df['total_activities'] = df.get('total_activities', 0)
    df['late_submissions'] = df.get('late_submissions', 0)
    df['total_submissions'] = df.get('total_submissions', df['total_activities'])
    df['success_rate'] = (df['passed_activities'] / df['total_activities'].replace(0, 1)) * 100.0
    df['punctuality_score'] = 100.0 - ((df['late_submissions'] / df['total_submissions'].replace(0, 1)) * 100.0)
    return df[['student_id','course_id','success_rate','punctuality_score','passed_activities','total_activities','late_submissions','total_submissions']]