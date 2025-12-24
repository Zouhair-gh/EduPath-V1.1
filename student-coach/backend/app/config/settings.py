from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5435/student_coach_db"

    # JWT
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "StudentCoach API"

    # External services (optional)
    RECO_BUILDER_URL: str = "http://localhost:8004"
    STUDENT_PROFILER_URL: str = "http://localhost:8002"
    PATH_PREDICTOR_URL: str = "http://localhost:8003"

    # Notifications
    NOTIFICATION_CHECK_INTERVAL: int = 3600  # seconds

    # Gamification
    XP_PER_ACTIVITY: int = 10
    XP_PER_GOAL_COMPLETED: int = 50

    class Config:
        env_file = ".env"

settings = Settings()
