# StudentCoach Backend

FastAPI service providing student mobile API with JWT authentication, goals, notifications, achievements, and scheduled motivation messages.

## Run locally

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8090
```

Default envs in `.env`. Ensure PostgreSQL is running and accessible (see docker-compose at repo root if provided).

## Key endpoints
- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- GET  /api/v1/student/me
- GET  /api/v1/notifications
- GET  /api/v1/goals
- POST /api/v1/goals
- PATCH/DELETE /api/v1/goals/{id}
- GET  /api/v1/achievements
