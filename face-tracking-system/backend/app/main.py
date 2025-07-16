from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from routers import streaming, embeddings, employees, attendance, auth
from tasks.camera_tasks import start_background_tasks, stop_background_tasks
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enhanced logging setup
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FaceTrackingSystem")

# CORS origins configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

# Add custom origins from environment
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    ALLOWED_ORIGINS.append(frontend_url)

custom_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
for origin in custom_origins:
    if origin.strip():
        ALLOWED_ORIGINS.append(origin.strip())

# Background tasks storage
background_tasks = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Face Tracking System API")
    
    # Start background tasks
    try:
        global background_tasks
        background_tasks = await start_background_tasks()
        logger.info("✅ Background tasks started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start background tasks: {e}")
    
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Shutting down Face Tracking System API")
    try:
        stop_background_tasks()
        
        # Cancel background tasks
        for task in background_tasks:
            task.cancel()
        
        logger.info("✅ Background tasks stopped successfully")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


app = FastAPI(
    title="Face Tracking System API",
    description="Enterprise face detection, recognition, and attendance tracking system.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "true").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("ENABLE_DOCS", "true").lower() == "true" else None,
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this for production
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ],
    expose_headers=["Content-Range", "X-Content-Range"],
)

# Include routers
app.include_router(auth.router)
app.include_router(streaming.router)
app.include_router(embeddings.router)
app.include_router(employees.router)
app.include_router(attendance.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Face Tracking System API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "authentication": "/auth",
            "employees": "/employees",
            "attendance": "/attendance", 
            "embeddings": "/embeddings",
            "streaming": "/stream",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    from utils.video_stream import camera_manager
    
    try:
        # Check database connection
        db_status = "healthy"
        # Add actual DB health check here
        
        # Check camera status
        active_cameras = camera_manager.get_active_cameras()
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Use actual timestamp
            "services": {
                "database": db_status,
                "cameras": {
                    "active_count": len(active_cameras),
                    "cameras": active_cameras
                },
                "background_tasks": "running"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }
