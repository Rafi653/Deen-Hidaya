from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from routes import router as quran_router

app = FastAPI(
    title="Deen Hidaya API",
    description="API for accessing Quran text, translations, transliterations, and audio",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(quran_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Deen Hidaya API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "backend",
        "version": "1.0.0"
    }


@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "backend-api",
        "version": "1.0.0"
    }
