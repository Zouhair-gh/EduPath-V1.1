from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db, get_current_user
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.student_lesson_progress import StudentLessonProgress
from app.models.lesson_quiz import LessonQuiz
from app.models.enrollment import Enrollment
from app.models.student import Student

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("")
async def list_courses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    courses: List[Course] = db.query(Course).all()
    student = db.query(Student).get(user.student_id) if user.student_id else None
    enrolled_ids = set(
        e.course_id for e in db.query(Enrollment).filter(Enrollment.student_id == (student.id if student else -1)).all()
    )
    return [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "teacher": c.teacher_name,
            "enrolled": c.id in enrolled_ids,
        }
        for c in courses
    ]

@router.post("/{course_id}/enroll")
async def enroll_course(course_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(Student).get(user.student_id) if user.student_id else None
    if not student:
        return {"ok": False, "error": "student_not_found"}
    exists = db.query(Enrollment).filter(Enrollment.student_id == student.id, Enrollment.course_id == course_id).first()
    if not exists:
        db.add(Enrollment(student_id=student.id, course_id=course_id))
        db.commit()
    return {"ok": True}

@router.get("/{course_id}/lessons")
async def list_lessons(course_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    lessons = db.query(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order_index.asc()).all()
    student = db.query(Student).get(user.student_id) if user.student_id else None
    progresses = {}
    if student:
        rows = db.query(StudentLessonProgress).filter(StudentLessonProgress.student_id == student.id, StudentLessonProgress.course_id == course_id).all()
        progresses = {r.lesson_id: r for r in rows}
    # map quiz ids
    quiz_map = {x.lesson_id: x.quiz_id for x in db.query(LessonQuiz).join(Lesson, Lesson.id == LessonQuiz.lesson_id).filter(Lesson.course_id == course_id).all()}
    return [
        {
            "id": l.id,
            "title": l.title,
            "content_url": l.content_url,
            "order": l.order_index,
            "locked": 0 == (progresses.get(l.id).is_unlocked if progresses.get(l.id) else (1 if l.order_index == 1 else 0)),
            "quiz_id": quiz_map.get(l.id),
            "quiz_passed": 1 == (progresses.get(l.id).quiz_passed if progresses.get(l.id) else 0),
        }
        for l in lessons
    ]

@router.get("/{course_id}/progress")
async def my_course_progress(course_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(Student).get(user.student_id) if user.student_id else None
    if not student:
        return {"ok": False, "error": "student_not_found"}
    rows = db.query(StudentLessonProgress).filter(StudentLessonProgress.student_id == student.id, StudentLessonProgress.course_id == course_id).all()
    return [
        {"lesson_id": r.lesson_id, "is_unlocked": 1 == r.is_unlocked, "quiz_passed": 1 == r.quiz_passed}
        for r in rows
    ]

@router.get("/{course_id}/quizzes")
async def list_course_quizzes(course_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.models.quiz import Quiz
    quizzes = db.query(Quiz).filter(Quiz.course_id == course_id).all()
    return [
        {
            "id": q.id,
            "title": q.title,
            "pass_threshold": q.pass_threshold,
        }
        for q in quizzes
    ]
