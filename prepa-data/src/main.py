import uvicorn
from fastapi import FastAPI
from .config.database import ensure_analytics_schema
from .api.routes import router
from .utils.logger import logger

app = FastAPI(title="PrepaData API", version="0.1.0")
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    try:
        ensure_analytics_schema()
        logger.info("Analytics schema ensured")
    except Exception as e:
        # Do not crash startup if DB isn't ready; logs help diagnose
        logger.error(f"Failed to ensure analytics schema: {e}")

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8001, reload=True)