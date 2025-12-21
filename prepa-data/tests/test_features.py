import pandas as pd
from src.features.engagement import compute_engagement
from src.features.performance import compute_performance

def test_compute_engagement():
    df = pd.DataFrame({'student_id':[1], 'course_id':[1], 'login_count':[5], 'time_spent':[3600], 'forum_posts':[2], 'resources_viewed':[10]})
    out = compute_engagement(df)
    assert 'engagement_score' in out.columns
    assert 0 <= out['engagement_score'].iloc[0] <= 100


def test_compute_performance():
    df = pd.DataFrame({'student_id':[1], 'course_id':[1], 'passed_activities':[8], 'total_activities':[10], 'late_submissions':[1], 'total_submissions':[10]})
    out = compute_performance(df)
    assert out['success_rate'].iloc[0] == 80.0
    assert round(out['punctuality_score'].iloc[0], 2) == 90.0