import os
from fastapi import FastAPI
from .api.routes import router as profiles_router
from .config.database import ensure_schema

API_PORT = int(os.getenv("API_PORT", "8002"))

app = FastAPI(title="StudentProfiler", version=os.getenv("MODEL_VERSION", "v1.0"))
app.include_router(profiles_router)

@app.on_event("startup")
async def startup():
    ensure_schema()

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "StudentProfiler",
        "health": "/health",
        "docs": "/docs",
        "base": "/api/profiles"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "StudentProfiler"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=API_PORT, reload=True)
