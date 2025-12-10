"""FastAPI Main Application"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting up application...")
    try:
        # Validate settings
        settings.validate_required()
        logger.info("✅ Settings validated")
        
        # Initialize Firebase
        from services.firebase_service import FirebaseService
        FirebaseService.initialize()
        logger.info("✅ Firebase initialized")
        
        # Initialize ChromaDB
        from services.vectorstore_service import VectorstoreService
        VectorstoreService.initialize()
        logger.info("✅ ChromaDB initialized")
        
        logger.info("🚀 Application started successfully")
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG Backend API với Firebase và ChromaDB",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix=settings.API_V1_PREFIX, tags=["RAG API"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Backend API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )

