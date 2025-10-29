# Deen Hidaya Backend

FastAPI backend service for the Deen Hidaya Islamic knowledge platform.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
uvicorn main:app --reload
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint
- `GET /api/v1/health` - API health check endpoint

## Docker

Build and run with Docker:
```bash
docker build -t deen-hidaya-backend .
docker run -p 8000:8000 deen-hidaya-backend
```
