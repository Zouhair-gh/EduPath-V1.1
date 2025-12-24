from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from datetime import datetime
from app.api.dependencies import get_db, get_current_user
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_answer import QuizAnswer
from app.models.student import Student
from app.models.lesson_quiz import LessonQuiz
from app.models.lesson import Lesson
from app.models.student_lesson_progress import StudentLessonProgress
from app.schemas.quiz import QuizSubmit

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

@router.get("/{quiz_id}")
async def get_quiz(quiz_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    quiz = db.query(Quiz).get(quiz_id)
    if not quiz:
        return {"ok": False, "error": "quiz_not_found"}
    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).all()
    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "pass_threshold": quiz.pass_threshold,
        "questions": [
            {
                "id": q.id,
                "prompt": q.prompt,
                "options": json.loads(q.options_json),
                "points": q.points,
            }
            for q in questions
        ],
    }

@router.post("/{quiz_id}/attempts")
async def submit_quiz(quiz_id: int, payload: QuizSubmit, db: Session = Depends(get_db), user=Depends(get_current_user)):
    quiz = db.query(Quiz).get(quiz_id)
    if not quiz:
        return {"ok": False, "error": "quiz_not_found"}
    student = db.query(Student).get(user.student_id) if user.student_id else None
    if not student:
        return {"ok": False, "error": "student_not_found"}
    qs_list = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).all()
    if len(qs_list) != 10:
        return {"ok": False, "error": "quiz_incomplete", "message": "Quiz must have exactly 10 questions"}
    questions = {q.id: q for q in qs_list}
    total_points = sum(q.points for q in questions.values())
    score = 0
    attempt = QuizAttempt(quiz_id=quiz.id, student_id=student.id, total_points=total_points, started_at=datetime.utcnow())
    db.add(attempt)
    db.commit()
    for ans in payload.answers:
        q = questions.get(ans.question_id)
        if not q:
            continue
        is_correct = 1 if ans.selected_index == q.correct_index else 0
        if is_correct:
            score += q.points
        qa = QuizAnswer(attempt_id=attempt.id, question_id=q.id, selected_index=ans.selected_index, is_correct=is_correct)
        db.add(qa)
    attempt.score = score
    attempt.completed_at = datetime.utcnow()
    db.commit()
    percent = int((score / total_points) * 100) if total_points > 0 else 0
    # enforce at least 60% pass threshold even if quiz has lower configured threshold
    min_thresh = max(60, quiz.pass_threshold)
    passed = percent >= min_thresh
    # Update progression: if this quiz is mapped to a lesson and passed, unlock next lesson
    mapping = db.query(LessonQuiz).filter(LessonQuiz.quiz_id == quiz.id).first()
    if mapping and passed:
        # mark current lesson quiz_passed and ensure unlocked
        prog = db.query(StudentLessonProgress).filter(
            StudentLessonProgress.student_id == student.id,
            StudentLessonProgress.lesson_id == mapping.lesson_id
        ).first()
        if not prog:
            prog = StudentLessonProgress(student_id=student.id, course_id=quiz.course_id, lesson_id=mapping.lesson_id, is_unlocked=1, quiz_passed=1)
            db.add(prog)
        else:
            prog.quiz_passed = 1
            prog.is_unlocked = 1
        db.commit()
        # unlock next lesson by order
        cur_lesson = db.query(Lesson).get(mapping.lesson_id)
        if cur_lesson:
            next_lesson = db.query(Lesson).filter(Lesson.course_id == cur_lesson.course_id, Lesson.order_index == (cur_lesson.order_index + 1)).first()
            if next_lesson:
                next_prog = db.query(StudentLessonProgress).filter(StudentLessonProgress.student_id == student.id, StudentLessonProgress.lesson_id == next_lesson.id).first()
                if not next_prog:
                    db.add(StudentLessonProgress(student_id=student.id, course_id=cur_lesson.course_id, lesson_id=next_lesson.id, is_unlocked=1, quiz_passed=0))
                else:
                    next_prog.is_unlocked = 1
                db.commit()
    return {"ok": True, "attempt_id": attempt.id, "score": score, "total_points": total_points, "percent": percent, "passed": passed}
