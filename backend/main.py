import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.routers import models, chat, auth

app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-Model LangChain Chatbot API powering Google Gemini, OpenAI, and Anthropic Claude.",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Modular API Routers
app.include_router(models.router)
app.include_router(chat.router)
app.include_router(auth.router)

@app.get("/api/health")
async def health_check():
    """Server health check endpoint."""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "database_status": "ready (sqlite placeholder)",
        "auth_status": "ready (jwt placeholder)",
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
