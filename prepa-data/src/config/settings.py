import os
from pydantic import BaseModel

class Settings(BaseModel):
    # Source (LMSConnector) DB
    SOURCE_DB_HOST: str = os.getenv("SOURCE_DB_HOST", "localhost")
    SOURCE_DB_PORT: int = int(os.getenv("SOURCE_DB_PORT", "5432"))
    SOURCE_DB_NAME: str = os.getenv("SOURCE_DB_NAME", "edupath")
    SOURCE_DB_USER: str = os.getenv("SOURCE_DB_USER", "postgres")
    SOURCE_DB_PASSWORD: str = os.getenv("SOURCE_DB_PASSWORD", "postgres")

    # Analytics DB
    ANALYTICS_DB_HOST: str = os.getenv("ANALYTICS_DB_HOST", "localhost")
    ANALYTICS_DB_PORT: int = int(os.getenv("ANALYTICS_DB_PORT", "5432"))
    ANALYTICS_DB_NAME: str = os.getenv("ANALYTICS_DB_NAME", "analytics_db")
    ANALYTICS_DB_USER: str = os.getenv("ANALYTICS_DB_USER", "postgres")
    ANALYTICS_DB_PASSWORD: str = os.getenv("ANALYTICS_DB_PASSWORD", "postgres")

    # FastAPI
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")

    # Pipeline
    PIPELINE_SCHEDULE: str = os.getenv("PIPELINE_SCHEDULE", "0 2 * * *")
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "1000"))
    OUTLIER_THRESHOLD: float = float(os.getenv("OUTLIER_THRESHOLD", "3"))
    ENGAGEMENT_WEIGHTS: str = os.getenv("ENGAGEMENT_WEIGHTS", "0.3,0.3,0.2,0.2")

    # Celery broker
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    def weights(self):
        parts = [float(x) for x in self.ENGAGEMENT_WEIGHTS.split(",")]
        if len(parts) != 4:
            parts = [0.3,0.3,0.2,0.2]
        return parts

settings = Settings()