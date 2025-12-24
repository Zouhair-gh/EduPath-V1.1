from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.models.student_profile import StudentProfile
from app.models.student import Student
from app.models.goal import Goal
from app.models.interaction_event import InteractionEvent
from app.services.motivation_engine import MotivationEngine
from datetime import datetime, timedelta

scheduler: BackgroundScheduler | None = None


def generate_notifications_job():
    db: Session = SessionLocal()
    try:
        # For demo: iterate a small set of student_ids
        engine = MotivationEngine(db)
        for sid in [1, 2, 3]:
            engine.generate_motivational_message(student_id=sid, profile_label="En Difficulté", recent_activity={"days_since_login": 6})
    finally:
        db.close()


def update_profiles_job():
    db: Session = SessionLocal()
    try:
        students = db.query(Student).all()
        for student in students:
            profile = db.query(StudentProfile).filter(StudentProfile.student_id == student.id).first()
            if not profile:
                continue
            # Engagement last 7 days
            cutoff7 = datetime.utcnow() + timedelta(days=-7)
            events7 = db.query(InteractionEvent).filter(InteractionEvent.student_id == student.id, InteractionEvent.created_at >= cutoff7).all()
            weights = {'check_in': 3, 'study_session': 0.2, 'like_recommendation': 1, 'complete_goal': 5, 'view_content': 1}
            score7 = 0.0
            for ev in events7:
                if ev.event_type == 'study_session':
                    score7 += (ev.value or 0) * weights['study_session']
                else:
                    score7 += weights.get(ev.event_type, 0)
            profile.engagement_ma7 = max(0, min(100, int(score7)))

            # Engagement last 30 days (approximate, reuse weights)
            cutoff30 = datetime.utcnow() + timedelta(days=-30)
            events30 = db.query(InteractionEvent).filter(InteractionEvent.student_id == student.id, InteractionEvent.created_at >= cutoff30).all()
            score30 = 0.0
            for ev in events30:
                if ev.event_type == 'study_session':
                    score30 += (ev.value or 0) * weights['study_session']
                else:
                    score30 += weights.get(ev.event_type, 0)
            profile.engagement_ma30 = max(0, min(100, int(score30 / 4)))  # rough scaling

            # Success rate: completed goals / active goals (30-day window)
            completed_count = db.query(InteractionEvent).filter(InteractionEvent.student_id == student.id, InteractionEvent.event_type == 'complete_goal', InteractionEvent.created_at >= cutoff30).count()
            active_goals = db.query(Goal).filter(Goal.student_id == student.id, Goal.status == 'ACTIVE').count()
            profile.success_rate = max(0, min(100, int(100 * (completed_count / active_goals)))) if active_goals > 0 else profile.success_rate

            db.commit()
    finally:
        db.close()


def start_scheduler():
    global scheduler
    if scheduler:
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(generate_notifications_job, 'interval', seconds=3600, id='notif_job')
    scheduler.add_job(update_profiles_job, 'cron', hour=2, id='profiles_job')
    scheduler.start()
