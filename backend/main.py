from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Deen Hidaya API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
