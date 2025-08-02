"""
FIA v3.0 - AI-powered e-learning platform
Main FastAPI application entry point
"""

import logging
# 🔍 FORCER LA CONFIGURATION DE LOGGING POUR VOIR NOS LOGS
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    force=True  # Force override de la config existante
)

# 🔍 DÉSACTIVER TOUS LES LOGS POSTGRESQL/SQLALCHEMY POUR ÉVITER LA POLLUTION
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.pool').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.orm').setLevel(logging.CRITICAL)
logging.getLogger('asyncpg').setLevel(logging.CRITICAL)
logging.getLogger('asyncio').setLevel(logging.ERROR)
logging.getLogger('aiopg').setLevel(logging.CRITICAL)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
from app.adapters.inbound.slide_controller import router as slide_router
from app.adapters.inbound.conversation_controller import router as conversation_router
from app.adapters.inbound.live_session_controller import router as live_session_router
from app.adapters.inbound.tts_controller import router as tts_router
from app.adapters.inbound.image_generation_controller import router as image_generation_router
from app.adapters.inbound.chart_generation_controller import router as chart_generation_router
from app.adapters.inbound.config_controller import router as config_router
from app.adapters.inbound.admin_controller import router as admin_router

# Import working controllers only (skip broken ones for now)
logger = logging.getLogger(__name__)

# Initialize GeminiCallLogger at startup
try:
    from app.infrastructure.gemini_call_logger import gemini_call_logger
    logger.info("✅ MAIN [INIT] GeminiCallLogger initialized")
except ImportError as e:
    logger.error(f"❌ MAIN [INIT] Failed to import GeminiCallLogger: {e}")

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
    try:
        await init_database()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization failed: {e}")
        logger.info("🚀 Application starting without database (will use fallback)")
    
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

# Include slide router
app.include_router(slide_router)

# Include conversation router
app.include_router(conversation_router)

# Include live session router
app.include_router(live_session_router)

# Include TTS router
app.include_router(tts_router)

# Include image generation router
app.include_router(image_generation_router)

# Include chart generation router
app.include_router(chart_generation_router)

# Include config router
app.include_router(config_router)

# Include admin router
app.include_router(admin_router)

# Include unified plan generation router if available
if PLAN_GENERATION_AVAILABLE:
    app.include_router(plan_generation_router)


@app.get("/")
async def root():
    """Root endpoint - simple health check"""
    return {
        "message": "FIA v3.0 API is running", 
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.environment
    }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon.ico"""
    return FileResponse("../frontend/public/favicon.ico")


@app.get("/api/health")
async def health_check():
    """Basic health check - always returns healthy for Railway deployment"""
    try:
        # Try to test database connection if available
        from app.infrastructure.database import engine
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "service": "fia-v3-backend",
            "version": "0.1.0",
            "database": "connected"
        }
    except Exception as e:
        # Return healthy even if DB is not available (for initial deployment)
        return {
            "status": "healthy",
            "service": "fia-v3-backend",
            "version": "0.1.0",
            "database": "disconnected",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)