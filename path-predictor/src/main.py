import os
from fastapi import FastAPI
from .api.routes import router as api_router
from .config.database import ensure_schema

API_PORT = int(os.getenv("API_PORT", "8003"))

app = FastAPI(title="PathPredictor", version=os.getenv("MODEL_VERSION", "v1.0"))
app.include_router(api_router)

@app.on_event("startup")
async def startup():
    ensure_schema()

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "PathPredictor",
        "health": "/health",
        "docs": "/docs",
        "base": "/api"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "PathPredictor"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=API_PORT, reload=True)
