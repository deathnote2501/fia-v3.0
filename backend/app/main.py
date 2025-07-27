"""
FIA v3.0 - AI-powered e-learning platform
Main FastAPI application entry point
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.infrastructure.settings import settings
from app.infrastructure.database import init_database
from app.infrastructure.auth import fastapi_users, auth_backend
from app.domain.schemas.user import UserRead, UserCreate, UserUpdate
from app.adapters.inbound.training_controller import router as training_router
from app.adapters.inbound.session_controller import router as session_router
from app.adapters.inbound.rate_limit_controller import router as rate_limit_router
from app.adapters.inbound.security_test_controller import router as security_test_router
from app.adapters.inbound.dashboard_controller import router as dashboard_router

# Import working controllers only (skip broken ones for now)
logger = logging.getLogger(__name__)

# Import unified plan generation controller
try:
    from app.controllers.plan_generation_controller import router as plan_generation_router
    PLAN_GENERATION_AVAILABLE = True
    logger.info("✅ Unified plan generation controller loaded successfully")
except ImportError as e:
    logger.warning(f"Unified plan generation controller not available: {e}")
    PLAN_GENERATION_AVAILABLE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    await init_database()
    yield
    # Shutdown (if needed)


# Create FastAPI application
app = FastAPI(
    title="FIA v3.0 API",
    description="AI-powered e-learning platform backend",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")

# Include FastAPI-Users routers
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Include training router
app.include_router(training_router)

# Include session router
app.include_router(session_router)

# Include rate limit router
app.include_router(rate_limit_router)

# Include security test router  
app.include_router(security_test_router)

# Include dashboard router
app.include_router(dashboard_router)

# Include unified plan generation router if available
if PLAN_GENERATION_AVAILABLE:
    app.include_router(plan_generation_router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "FIA v3.0 API is running", "status": "healthy"}


@app.get("/api/health")
async def health_check():
    """Detailed health check with database connection"""
    from app.infrastructure.database import engine
    from sqlalchemy import text
    
    try:
        # Test database connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "service": "fia-v3-backend",
            "version": "0.1.0",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "fia-v3-backend",
            "version": "0.1.0",
            "database": "disconnected",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)