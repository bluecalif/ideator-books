"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ideator Books API",
    description="KB-based 1-pager generation service using LangGraph",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Ideator Books API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ideator-books-api"
    }


# TODO: Include routers here
# from backend.api.routes import upload, books, runs, history
# app.include_router(upload.router, prefix="/api", tags=["upload"])
# app.include_router(books.router, prefix="/api", tags=["books"])
# app.include_router(runs.router, prefix="/api", tags=["runs"])
# app.include_router(history.router, prefix="/api", tags=["history"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

