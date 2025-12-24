from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db, get_current_user
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.quiz_attempt import QuizAttempt
from app.models.lesson import Lesson
from app.models.lesson_quiz import LessonQuiz

router = APIRouter(prefix="/teacher", tags=["Teacher"])

@router.get("/courses")
async def list_courses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    courses: List[Course] = db.query(Course).all()
    return [
        {"id": c.id, "title": c.title, "description": c.description, "teacher": c.teacher_name}
        for c in courses
    ]

@router.get("/courses/{course_id}/enrollments")
async def course_enrollments(course_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    result = []
    for e in rows:
        s = db.query(Student).get(e.student_id)
        result.append({"student_id": s.id if s else e.student_id, "student_name": s.name if s else "-", "status": e.status})
    return result

@router.get("/courses/{course_id}/progress")
async def course_progress(course_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # For each enrolled student, compute average percent over attempts for quizzes in this course
    enrolls = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    out = []
    for e in enrolls:
        attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == e.student_id).all()
        percents = [int((a.score / a.total_points) * 100) for a in attempts if a.total_points > 0]
        avg = int(sum(percents) / len(percents)) if percents else 0
        s = db.query(Student).get(e.student_id)
        out.append({"student_id": e.student_id, "student_name": s.name if s else "-", "avg_percent": avg})
    # overall average
    overall = int(sum(r["avg_percent"] for r in out) / len(out)) if out else 0
    # Per-lesson pass rates
    lessons = db.query(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order_index.asc()).all()
    lesson_quizzes = {x.lesson_id: x.quiz_id for x in db.query(LessonQuiz).join(Lesson, Lesson.id == LessonQuiz.lesson_id).filter(Lesson.course_id == course_id).all()}
    lesson_pass = []
    for l in lessons:
        qid = lesson_quizzes.get(l.id)
        if not qid:
            continue
        attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == qid).all()
        if not attempts:
            rate = 0
        else:
            passed = 0
            for a in attempts:
                percent = int((a.score / a.total_points) * 100) if a.total_points > 0 else 0
                if percent >= 60:
                    passed += 1
            rate = int(100 * (passed / len(attempts)))
        lesson_pass.append({"lesson_id": l.id, "lesson_title": l.title, "pass_rate": rate})
    return {"overall_avg": overall, "students": out, "lessonPassRates": lesson_pass}
