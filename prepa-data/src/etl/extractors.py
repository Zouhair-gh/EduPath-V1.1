import pandas as pd
from sqlalchemy import text
from ..config.database import get_source_engine
from ..utils.logger import logger

# Assumes LMSConnector tables: students, courses, enrollments, grades, activity_logs

def extract_raw_data(batch_size: int = 1000):
    eng = get_source_engine()
    logger.info("Extracting raw data from source DB")
    with eng.connect() as conn:
        try:
            students = pd.read_sql("SELECT * FROM students", conn)
        except Exception:
            students = pd.DataFrame()
        try:
            courses = pd.read_sql("SELECT * FROM courses", conn)
        except Exception:
            courses = pd.DataFrame()
        try:
            enrollments = pd.read_sql("SELECT * FROM enrollments", conn)
        except Exception:
            enrollments = pd.DataFrame()
        try:
            grades = pd.read_sql("SELECT * FROM grades", conn)
        except Exception:
            grades = pd.DataFrame()
        try:
            activity = pd.read_sql("SELECT * FROM activity_logs", conn)
        except Exception:
            activity = pd.DataFrame()
    return {
        'students': students,
        'courses': courses,
        'enrollments': enrollments,
        'grades': grades,
        'activity': activity,
    }