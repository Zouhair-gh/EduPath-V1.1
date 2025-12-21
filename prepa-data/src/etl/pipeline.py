import uuid
from ..utils.logger import logger
from .extractors import extract_raw_data
from .validators import validate_quality
from .transformers import clean_and_transform
from ..features.engagement import compute_engagement
from ..features.performance import compute_performance
from ..features.temporal import compute_temporal_features
from .loaders import write_student_metrics, write_temporal_features, log_pipeline


def run_pipeline_once():
    run_id = str(uuid.uuid4())
    processed = 0; failed = 0
    try:
        raw = extract_raw_data()
        validate_quality(raw)
        clean = clean_and_transform(raw)
        # Engagement
        engagement_df = compute_engagement(clean['activity'])
        # Performance (merge grades/activities to derive counts)
        perf_src = engagement_df.copy()
        perf_src['passed_activities'] = perf_src.get('activities_completed', 0)
        perf_src['total_activities'] = perf_src.get('activities_total', perf_src['passed_activities'])
        perf_src['late_submissions'] = perf_src.get('late_submissions', 0)
        perf_src['total_submissions'] = perf_src.get('total_submissions', perf_src['total_activities'])
        performance_df = compute_performance(perf_src)
        # Aggregate for student_metrics
        student_metrics = engagement_df.merge(performance_df, on=['student_id','course_id'], how='outer')
        write_student_metrics(student_metrics)
        processed += len(student_metrics)
        # Temporal features: derive simple daily snapshot (placeholder)
        if not clean['activity'].empty:
            daily = clean['activity'].copy()
            daily = daily.rename(columns={'timestamp': 'feature_date', 'engagement_score': 'engagement'})
            if 'feature_date' in daily.columns:
                tf = compute_temporal_features(daily[['student_id','course_id','feature_date','engagement']].assign(grade=0.0))
                write_temporal_features(tf)
                processed += len(tf)
        log_pipeline(run_id, 'success', processed, failed)
        logger.info(f"Pipeline {run_id} completed: processed={processed}")
        return {'run_id': run_id, 'status': 'success', 'processed': processed}
    except Exception as e:
        failed = 1
        log_pipeline(run_id, 'failed', processed, failed, error_message=str(e))
        logger.exception("Pipeline failed")
        return {'run_id': run_id, 'status': 'failed', 'error': str(e)}