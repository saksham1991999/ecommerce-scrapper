import os
from fastapi import FastAPI
from app.routers import scraper
from app.middleware.auth_middleware import AuthMiddleware
from app.cache.redis_cache import RedisCache
from app.models.db_models import Base
from sqlalchemy.ext.asyncio import create_async_engine
from app.utils.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

# Add the authentication middleware
API_KEY = os.getenv("API_KEY", "abc")  # Use environment variable, fallback to "abc" if not set
app.add_middleware(AuthMiddleware, api_key=API_KEY)

app.include_router(scraper.router, prefix="/api/v1", tags=["scraper"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    os.makedirs("storage", exist_ok=True)
    app.state.redis_cache = RedisCache()
    await app.state.redis_cache.initialize()
    logger.info("Redis cache initialized")

    # Initialize database
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@postgres/scraper_db")
    engine = create_async_engine(db_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application")
    await app.state.redis_cache.close()
    logger.info("Redis cache closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)