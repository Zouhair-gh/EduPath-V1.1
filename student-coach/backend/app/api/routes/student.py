from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.models.student import Student
from app.models.student_profile import StudentProfile
from app.models.interaction_event import InteractionEvent
from app.models.goal import Goal
from app.models.achievement import Achievement
from app.models.recommendation import Recommendation

router = APIRouter(prefix="/student", tags=["Student"])

@router.get("/me")
async def me(db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(Student).get(user.student_id) if user.student_id else None
    return {
        "id": user.id,
        "email": user.email,
        "student": {"id": student.id, "name": student.name} if student else None,
    }

@router.get("/dashboard")
async def dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(Student).get(user.student_id) if user.student_id else None
    profile = None
    if student:
        profile = db.query(StudentProfile).filter(StudentProfile.student_id == student.id).first()
    # Compute dynamic engagement/success based on recent interactions
    engagement = (profile.engagement_ma7 if profile else 60)
    success = (profile.success_rate if profile else 75)
    if student:
        from datetime import datetime, timedelta
        cutoff7 = datetime.utcnow() + timedelta(days=-7)
        events7 = db.query(InteractionEvent).filter(InteractionEvent.student_id == student.id, InteractionEvent.created_at >= cutoff7).all()
        # Simple weighting by event type
        weights = {
            'check_in': 3,
            'study_session': 0.2,  # per minute
            'like_recommendation': 1,
            'complete_goal': 5,
            'view_content': 1,
        }
        score = 0.0
        for ev in events7:
            if ev.event_type == 'study_session':
                minutes = ev.value or 0
                score += minutes * weights['study_session']
            else:
                score += weights.get(ev.event_type, 0)
        # Normalize and clamp 0-100
        engagement = max(0, min(100, int(score)))
        # Success: proportion of 'complete_goal' events in last 30 days vs active goals
        cutoff30 = datetime.utcnow() + timedelta(days=-30)
        completed_count = db.query(InteractionEvent).filter(InteractionEvent.student_id == student.id, InteractionEvent.event_type == 'complete_goal', InteractionEvent.created_at >= cutoff30).count()
        active_goals = db.query(Goal).filter(Goal.student_id == student.id, Goal.status == 'ACTIVE').count()
        success = max(0, min(100, int(100 * (completed_count / active_goals))) ) if active_goals > 0 else success
    punctuality = 78
    profile_label = (profile.profile_label if profile else "Assidu Moyen")
    # Weekly study minutes and streak
    study_weekly = []
    streak_days = 0
    if student:
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        # last 7 days study minutes
        for d in range(6, -1, -1):
            day = today - timedelta(days=d)
            day_events = db.query(InteractionEvent).filter(
                InteractionEvent.student_id == student.id,
                InteractionEvent.event_type == 'study_session'
            ).all()
            minutes = sum((ev.value or 0) for ev in day_events if ev.created_at.date() == day)
            study_weekly.append(minutes)
        # streak: consecutive days with a check_in starting today going backwards
        tmp_day = today
        while True:
            has_checkin = db.query(InteractionEvent).filter(
                InteractionEvent.student_id == student.id,
                InteractionEvent.event_type == 'check_in'
            ).all()
            if any(ev.created_at.date() == tmp_day for ev in has_checkin):
                streak_days += 1
                tmp_day = tmp_day - timedelta(days=1)
                if streak_days > 365:
                    break
            else:
                break
    trajectory = [
        {"x": i, "y": v} for i, v in enumerate(study_weekly if study_weekly else [10, 0, 15, 20, 5, 12, 18])
    ]
    goals = db.query(Goal).filter(Goal.student_id == (student.id if student else -1), Goal.status == 'ACTIVE').order_by(Goal.deadline.asc()).limit(5).all()
    recos = db.query(Recommendation).filter(Recommendation.student_id == (student.id if student else -1)).order_by(Recommendation.created_at.desc()).limit(5).all()
    achievements = db.query(Achievement).filter(Achievement.student_id == (student.id if student else -1)).order_by(Achievement.unlocked_at.desc()).limit(3).all()
    return {
        "engagementScore": engagement,
        "successRate": success,
        "punctualityScore": punctuality,
        "profileLabel": profile_label,
        "trajectoryData": trajectory,
        "studyWeekly": study_weekly,
        "streakDays": streak_days,
        "activeGoals": [
            {
                "id": g.id,
                "title": g.title,
                "current_value": g.current_value,
                "target_value": g.target_value,
                "deadline": g.deadline.isoformat(),
            }
            for g in goals
        ],
        "recommendations": [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "url": r.url,
                "kind": r.kind,
            }
            for r in recos
        ],
        "recentAchievements": [
            {"id": a.id, "title": a.title, "icon_url": a.icon_url}
            for a in achievements
        ],
        "motivationalMessage": f"Continue, tu es sur la bonne voie ! ({profile_label})",
    }
