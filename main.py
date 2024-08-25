import os
from fastapi import FastAPI
from app.routers import scraper
from app.middleware.auth_middleware import AuthMiddleware

app = FastAPI()

# Add the authentication middleware
API_KEY = "abc"  # In a real application, this should be stored securely, e.g., in environment variables
app.add_middleware(AuthMiddleware, api_key=API_KEY)

app.include_router(scraper.router, prefix="/api/v1", tags=["scraper"])

@app.on_event("startup")
async def startup_event():
    os.makedirs("storage", exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)