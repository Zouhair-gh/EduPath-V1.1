import pandas as pd
from ..config.settings import settings


def compute_engagement(activity_df: pd.DataFrame, expected_logins: int = 5, expected_time: float = 3600.0,
                        avg_forum_posts: float = 2.0, total_resources: float = 10.0) -> pd.DataFrame:
    w1, w2, w3, w4 = settings.weights()
    df = activity_df.copy()
    df['login_count'] = df.get('login_count', pd.Series([0]*len(df))).fillna(0)
    df['time_spent'] = df.get('time_spent', pd.Series([0]*len(df))).fillna(0)
    df['forum_posts'] = df.get('forum_posts', pd.Series([0]*len(df))).fillna(0)
    df['resources_viewed'] = df.get('resources_viewed', pd.Series([0]*len(df))).fillna(0)
    score = (
        w1 * (df['login_count'] / max(expected_logins, 1)) +
        w2 * (df['time_spent'] / max(expected_time, 1)) +
        w3 * (df['forum_posts'] / max(avg_forum_posts, 1)) +
        w4 * (df['resources_viewed'] / max(total_resources, 1))
    ) / max(sum([w1,w2,w3,w4]), 1)
    df['engagement_score'] = (score * 100).clip(lower=0, upper=100)
    return df[['student_id','course_id','engagement_score','login_count','time_spent','forum_posts','resources_viewed']]