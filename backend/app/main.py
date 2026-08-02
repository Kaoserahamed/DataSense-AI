from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

# Updated: 2026-08-02 - Added visualization support in chat
from app.core.config import settings
from app.api import projects, datasets
from app.database.connection import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting DataSense AI API...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down DataSense AI API...")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS
allowed_origins = settings.get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler — ensures CORS headers are present even on unhandled 500s
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    origin = request.headers.get("origin", "")
    import re
    is_allowed = origin in allowed_origins or bool(re.match(r"https://.*\.vercel\.app", origin))
    headers = {}
    if is_allowed:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=headers,
    )

# Include routers
app.include_router(projects.router)
app.include_router(datasets.router)

# Import and include analysis router
from app.api import analysis, cleaning, chat, visualization
app.include_router(analysis.router)
app.include_router(cleaning.router)
app.include_router(chat.router)
app.include_router(visualization.router)


@app.get("/")
def root():
    return {
        "message": "DataSense AI API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    try:
        from app.database.connection import engine
        from app.ai.llm_provider import llm_provider
        
        # Check database
        with engine.connect() as conn:
            db_status = "connected"
        
        # Check AI availability
        ai_status = "available" if llm_provider.is_available() else "unavailable"
        
        return {
            "status": "healthy",
            "database": db_status,
            "ai_provider": ai_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e)
        }
