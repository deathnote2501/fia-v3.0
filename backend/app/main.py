"""
FIA v3.0 - AI-powered e-learning platform
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.settings import settings

# Create FastAPI application
app = FastAPI(
    title="FIA v3.0 API",
    description="AI-powered e-learning platform backend",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "FIA v3.0 API is running", "status": "healthy"}


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "fia-v3-backend",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)