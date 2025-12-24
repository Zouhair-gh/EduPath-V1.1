from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.student import Student
from app.models.student_profile import StudentProfile
from app.models.goal import Goal
from app.models.notification import Notification
from app.models.achievement import Achievement
from app.models.recommendation import Recommendation
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.models.lesson_quiz import LessonQuiz
from app.models.student_lesson_progress import StudentLessonProgress
from app.core.security import get_password_hash
from app.api.routes import auth as auth_routes
from app.api.routes import student as student_routes
from app.api.routes import notifications as notif_routes
from app.api.routes import goals as goals_routes
from app.api.routes import achievements as ach_routes
from app.api.routes import health as health_routes
from app.api.routes import recommendations as reco_routes
from app.api.routes import interactions as interactions_routes
from app.tasks.scheduled_tasks import start_scheduler
from app.api.routes import teacher as teacher_routes
from app.api.routes import courses as courses_routes
from app.api.routes import quizzes as quizzes_routes

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (for dev)
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(student_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(notif_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(goals_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(ach_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(health_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(reco_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(interactions_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(teacher_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(courses_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(quizzes_routes.router, prefix=settings.API_V1_PREFIX)

@app.on_event("startup")
async def _startup():
    # Dev seed: ensure a default user exists for quick login
    db = SessionLocal()
    try:
        email = "student@example.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                password_hash=get_password_hash("password123"),
                is_active=True,
            )
            db.add(user)
            db.commit()
        # Seed student and link to user
        student = db.query(Student).filter(Student.email == email).first()
        if not student:
            student = Student(name="John Doe", email=email)
            db.add(student)
            db.commit()
        if not user.student_id:
            user.student_id = student.id
            db.commit()
        # Seed profile
        profile = db.query(StudentProfile).filter(StudentProfile.student_id == student.id).first()
        if not profile:
            profile = StudentProfile(student_id=student.id, engagement_ma7=72, engagement_ma30=65, success_rate=81, profile_label="Assidu Moyen")
            db.add(profile)
            db.commit()
        # Seed a goal
        if not db.query(Goal).filter(Goal.student_id == student.id).first():
            from datetime import date, timedelta
            g = Goal(student_id=student.id, title="Réviser Chapitre 3", description="Faire les exercices 1 à 10", goal_type="improve_engagement", target_value=10, start_date=date.today(), deadline=date.today()+timedelta(days=7))
            db.add(g)
            db.commit()
        # Seed a notification
        if not db.query(Notification).filter(Notification.student_id == student.id).first():
            n = Notification(student_id=student.id, type="praise", title="Bravo !", message="Tu as bien progressé cette semaine.", priority="NORMAL")
            db.add(n)
            db.commit()
        # Seed an achievement
        if not db.query(Achievement).filter(Achievement.student_id == student.id).first():
            a = Achievement(student_id=student.id, achievement_type="first_login", title="Premier pas", description="Tu t'es connecté !")
            db.add(a)
            db.commit()
        # Seed a recommendation
        if not db.query(Recommendation).filter(Recommendation.student_id == student.id).first():
            r = Recommendation(student_id=student.id, title="Vidéo: Algèbre pour débutants", description="Une introduction rapide à l'algèbre", url="https://example.com/algebre", kind="video")
            db.add(r)
            db.commit()
        # Seed a demo course, lessons, and quiz
        import json
        course = db.query(Course).first()
        if not course:
            course = Course(title="Maths 101", description="Bases d'algèbre et arithmétique", teacher_name="Mme. Dupont")
            db.add(course)
            db.commit()
            lessons = [
                Lesson(course_id=course.id, title="Introduction", content_url="https://example.com/intro", order_index=1),
                Lesson(course_id=course.id, title="Addition et Soustraction", content_url="https://example.com/add-sub", order_index=2),
                Lesson(course_id=course.id, title="Multiplication et Division", content_url="https://example.com/mul-div", order_index=3),
            ]
            db.add_all(lessons)
            db.commit()
            # For each lesson, create a quiz with 10 questions and link via LessonQuiz
            for l in lessons:
                quiz = Quiz(course_id=course.id, title=f"Quiz {l.title}", description=f"Quiz pour {l.title}", pass_threshold=60)
                db.add(quiz)
                db.commit()
                # 10 simple questions
                qs = []
                for i in range(10):
                    prompt = f"Q{i+1}: 1 + 1 = ?"
                    options = json.dumps(["1","2","3","4"])
                    qs.append(QuizQuestion(quiz_id=quiz.id, prompt=prompt, options_json=options, correct_index=1, points=1))
                db.add_all(qs)
                db.commit()
                db.add(LessonQuiz(lesson_id=l.id, quiz_id=quiz.id))
                db.commit()
            # Unlock first lesson for the student
            if student:
                first = lessons[0]
                db.add(StudentLessonProgress(student_id=student.id, course_id=course.id, lesson_id=first.id, is_unlocked=1, quiz_passed=0))
                db.commit()
    finally:
        db.close()
    start_scheduler()

@app.get("/")
async def root():
    return {"status": "ok", "service": "StudentCoach"}
