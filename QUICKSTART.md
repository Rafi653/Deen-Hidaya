# Quick Start Guide

This guide helps you get started with Deen Hidaya development.

## Prerequisites

- Docker and Docker Compose (for containerized setup)
- OR Python 3.11+ and Node.js 18+ (for local development)
- Git

## Option 1: Docker Setup (Recommended)

### 1. Clone and Configure

```bash
git clone https://github.com/Rafi653/Deen-Hidaya.git
cd Deen-Hidaya
cp .env.example .env
```

### 2. Start All Services

```bash
docker compose up
```

This starts:
- **PostgreSQL** with pgvector and pg_trgm extensions on port 5432
- **Backend API** on http://localhost:8000
- **Frontend** on http://localhost:3000

### 3. Verify Services

Open these URLs in your browser:
- Frontend: http://localhost:3000
- Frontend Health: http://localhost:3000/api/health
- Backend Health: http://localhost:8000/health
- Backend API Docs: http://localhost:8000/docs

### 4. Stop Services

```bash
docker compose down
```

To also remove volumes (database data):
```bash
docker compose down -v
```

## Option 2: Local Development

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:3000

### Database Setup (Local)

Install PostgreSQL 16 with pgvector extension, then run:

```bash
psql -U postgres -f infra/init-db.sql
```

## Health Checks

All services expose health check endpoints:

### Backend
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "backend",
  "version": "1.0.0"
}
```

### Frontend
```bash
curl http://localhost:3000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "frontend",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## Project Structure

```
.
├── frontend/          # Next.js frontend application
├── backend/           # FastAPI backend service
├── infra/            # Infrastructure configuration
│   └── init-db.sql   # PostgreSQL initialization (pgvector, pg_trgm)
├── data/             # Data files (excluded from git)
├── docs/             # Project documentation
└── scripts/          # Utility scripts
```

## Next Steps

1. Review the [Project Documentation](docs/AGENTS.md)
2. Check individual README files in `frontend/` and `backend/`
3. Review the [Implementation Checklist](docs/IMPLEMENTATION_CHECKLIST.md)

## Troubleshooting

### Port Conflicts

If ports 3000, 8000, or 5432 are already in use, you can modify them in `.env`:

```env
FRONTEND_PORT=3001
BACKEND_PORT=8001
POSTGRES_PORT=5433
```

Then update the docker-compose.yml port mappings accordingly.

### Database Connection Issues

Ensure PostgreSQL is running and accessible. Check logs:

```bash
docker compose logs postgres
```

### Build Issues

If you encounter build issues, try rebuilding without cache:

```bash
docker compose build --no-cache
```

## Development Workflow

1. Make changes to code
2. Changes are automatically reflected (hot reload in both frontend and backend)
3. Test your changes using the health endpoints
4. Commit your changes following the project guidelines

## Getting Help

- Check the [docs/](docs/) directory for detailed documentation
- Review agent-specific guides in [docs/agents/](docs/agents/)
- Open an issue on GitHub for bugs or questions
