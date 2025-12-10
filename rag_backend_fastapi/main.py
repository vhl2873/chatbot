"""FastAPI Main Application"""
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
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

# Mount frontend static files (CSS, JS, images)
frontend_dir = settings.BASE_DIR.parent / "frontend"
if frontend_dir.exists():
    # Mount CSS
    css_dir = frontend_dir / "css"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    # Mount JS
    js_dir = frontend_dir / "js"
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
    # Mount other static files
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Setup upload.html from frontend
upload_html_path = frontend_dir / "upload.html" if frontend_dir.exists() else None


@app.get("/", response_class=HTMLResponse)
@app.get("/upload", response_class=HTMLResponse)
async def root():
    """Root endpoint - Serve upload interface from frontend"""
    if upload_html_path and upload_html_path.exists():
        with open(upload_html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("""
    <html>
        <head><title>RAG Backend API</title></head>
        <body>
            <h1>RAG Backend API</h1>
            <p>Version: {}</p>
            <p>Status: running</p>
            <p><a href="/docs">API Documentation</a></p>
            <p><a href="{}/health">Health Check</a></p>
            <p><a href="/upload">Upload Interface</a></p>
        </body>
    </html>
    """.format(settings.APP_VERSION, settings.API_V1_PREFIX))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )

