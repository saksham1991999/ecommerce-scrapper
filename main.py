import os
from fastapi import FastAPI
from app.routers import scraper
from app.middleware.auth_middleware import AuthMiddleware
from app.cache.redis_cache import RedisCache

app = FastAPI()

# Add the authentication middleware
API_KEY = os.getenv("API_KEY", "abc")  # Use environment variable, fallback to "abc" if not set
app.add_middleware(AuthMiddleware, api_key=API_KEY)

app.include_router(scraper.router, prefix="/api/v1", tags=["scraper"])

@app.on_event("startup")
async def startup_event():
    os.makedirs("storage", exist_ok=True)
    app.state.redis_cache = RedisCache()
    await app.state.redis_cache.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis_cache.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)