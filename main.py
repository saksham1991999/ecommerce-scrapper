import os
from fastapi import FastAPI, HTTPException
from app.routers import scraper
from app.middleware.auth_middleware import AuthMiddleware
from app.cache.redis_cache import RedisCache
from app.models.db_models import Base
from sqlalchemy.ext.asyncio import create_async_engine
from app.utils.logging_config import setup_logging
import logging
from app.exceptions.authentication_exceptions import AuthenticationException
from app.exceptions.caching_exceptions import CacheException
from app.exceptions.storage_exceptions import StorageException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_503_SERVICE_UNAVAILABLE, HTTP_500_INTERNAL_SERVER_ERROR
from app.constants import API_KEY, DATABASE_URL, PORT, HOST

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

# Add the authentication middleware
app.add_middleware(AuthMiddleware, api_key=API_KEY)

app.include_router(scraper.router, prefix="/api/v1", tags=["scraper"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    try:
        os.makedirs("storage", exist_ok=True)
        app.state.redis_cache = RedisCache()
        await app.state.redis_cache.initialize()
        logger.info("Redis cache initialized")

        # Initialize database
        engine = create_async_engine(DATABASE_URL, echo=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")
    except AuthenticationException as e:
        logger.error(f"Authentication error during startup: {str(e)}")
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Authentication failed during startup")
    except CacheException as e:
        logger.error(f"Failed to initialize Redis cache: {str(e)}")
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Service Unavailable: Cache initialization failed")
    except StorageException as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Service Unavailable: Database initialization failed")
    except Exception as e:
        logger.error(f"Unexpected error during startup: {str(e)}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error: Unexpected error during startup")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application")
    try:
        await app.state.redis_cache.close()
        logger.info("Redis cache closed")
    except CacheException as e:
        logger.error(f"Error closing Redis cache: {str(e)}")
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Service Unavailable: Error closing Redis cache")
    except Exception as e:
        logger.error(f"Unexpected error during shutdown: {str(e)}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error: Unexpected error during shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)