from ..config.database import get_engine
from sqlalchemy import text

def main():
    engine = get_engine()
    sample = [
        {
            "title": "Algebra Basics",
            "description": "Introductory video on linear equations",
            "resource_type": "video",
            "subject": "math",
            "difficulty_level": "beginner",
            "duration_minutes": 12,
            "url": "https://example.com/algebra-basics",
            "minio_key": None,
            "tags": ["algebra","equations","basics"],
        },
        {
            "title": "Quadratic Exercises",
            "description": "Practice problems on quadratic equations",
            "resource_type": "exercise",
            "subject": "math",
            "difficulty_level": "intermediate",
            "duration_minutes": 20,
            "url": "https://example.com/quadratic-exercises",
            "minio_key": None,
            "tags": ["algebra","quadratic","practice"],
        },
        {
            "title": "Study Tips",
            "description": "Article on effective learning strategies",
            "resource_type": "article",
            "subject": "study skills",
            "difficulty_level": "beginner",
            "duration_minutes": 8,
            "url": "https://example.com/study-tips",
            "minio_key": None,
            "tags": ["learning","fundamentals"],
        },
    ]
    with engine.begin() as conn:
        for r in sample:
            conn.execute(text(
                """
                INSERT INTO resources (title, description, resource_type, subject, difficulty_level, duration_minutes, url, minio_key, tags)
                VALUES (:title, :description, :resource_type, :subject, :difficulty_level, :duration_minutes, :url, :minio_key, :tags::jsonb)
                """
            ), {**r, "tags": __import__("json").dumps(r["tags"])})
    print(f"Seeded {len(sample)} resources.")

if __name__ == "__main__":
    main()
