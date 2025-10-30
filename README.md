# Deen-Hidaya

An Islamic knowledge platform providing access to the Quran with audio recitations, translations, and Q&A content.

## Project Structure

This project uses a cross-functional agent model for development. See [docs/AGENTS.md](./docs/AGENTS.md) for the complete guide to project roles and responsibilities.

### Quick Links
- **[Project Agents Overview](./docs/AGENTS.md)** - Team structure and responsibilities
- **[PM Agent](./docs/agents/PM.md)** - Product management and planning
- **[Lead/Architect Agent](./docs/agents/LEAD.md)** - Architecture and code review
- **[Frontend Agent](./docs/agents/FRONTEND.md)** - UI implementation
- **[Backend Agent](./docs/agents/BACKEND.md)** - Server and data services
- **[QA Agent](./docs/agents/QA.md)** - Testing and quality assurance

### Agent Roles

| Agent | Label | Focus |
|-------|-------|-------|
| PM | `role:pm` | Roadmap, milestones, compliance |
| Lead/Architect | `role:lead` | Architecture, review, CI/CD |
| Frontend | `role:frontend` | Reader UI, audio player, a11y |
| Backend | `role:backend` | FastAPI, DB, search, embeddings |
| QA | `role:qa` | Test strategy, acceptance verification |

## Repository Structure

```
.
├── frontend/          # Next.js frontend application
├── backend/           # FastAPI backend service
├── infra/            # Infrastructure configuration and database init scripts
├── data/             # Data files (excluded from version control)
├── docs/             # Project documentation
└── scripts/          # Utility scripts
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- (Optional) OpenAI API key for Q&A features

### 🚨 Known Issues & Quick Fixes

If you encounter missing translations or Q&A not working:

**[→ Quick Fix Guide](./QUICKFIX_GUIDE.md)** - Complete step-by-step guide to fix:
1. Missing English/Telugu translations
2. Q&A functionality not working
3. Embeddings generation

**Time**: 15-30 minutes | **Cost**: ~$0.03 for embeddings

See also: [Detailed Troubleshooting Guide](./backend/FIXES_README.md)

### Quick Start (Automated Setup)

**Recommended:** Use the automated setup script for a complete one-command setup:

```bash
git clone https://github.com/Rafi653/Deen-Hidaya.git
cd Deen-Hidaya
./setup.sh
```

This script will:
- ✅ Create `.env` file from template
- ✅ Start Docker services (PostgreSQL, Backend, Frontend)
- ✅ Run database migrations
- ✅ Ingest Quran data (if not already present)
- ✅ Optionally generate embeddings for Q&A
- ✅ Verify all services are healthy

After setup completes:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

### Quick Start (Manual Setup)

If you prefer manual setup:

1. Clone the repository:
```bash
git clone https://github.com/Rafi653/Deen-Hidaya.git
cd Deen-Hidaya
```

2. Copy the environment example file:
```bash
cp .env.example .env
```

3. Start all services with Docker Compose:
```bash
docker compose up -d
```

4. Run database migrations:
```bash
docker compose exec backend alembic upgrade head
```

5. Ingest data (if not already done):
```bash
docker compose exec backend python ingest_data.py
```

### Health Checks

Verify all services are running:
- Frontend: http://localhost:3000/api/health
- Backend: http://localhost:8000/health

### Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

See individual README files in `frontend/` and `backend/` directories for more details.

## Sharing Your Local App

Want to share your local Deen Hidaya app with friends for testing and feedback? Use Cloudflare Tunnel:

```bash
# Quick start - no configuration needed
./infra/start-tunnel.sh
```

This will generate shareable URLs that allow anyone to access your locally-running app.

📖 **See [Cloudflare Tunnel Setup Guide](./docs/CLOUDFLARE_TUNNEL_SETUP.md)** for:
- Step-by-step setup instructions
- Security best practices
- Persistent tunnel configuration
- Troubleshooting guide

## Troubleshooting

### Common Issues

#### ❌ "Translation not available" in frontend
**Fix**: Run the translation fix script to get correct English and Telugu translations.
```bash
docker compose exec backend python fix_translations.py --force
```
[Full guide →](./QUICKFIX_GUIDE.md#step-2-fix-translations)

#### ❌ Q&A page not working
**Fix**: Generate embeddings with your OpenAI API key.
```bash
# Add OPENAI_API_KEY to .env first
docker compose exec backend python fix_embeddings.py
```
[Full guide →](./QUICKFIX_GUIDE.md#step-3-fix-embeddings-enable-qa)

#### ❌ Services not starting
**Fix**: Check Docker logs and ensure ports are free.
```bash
docker compose logs backend
docker compose logs frontend
docker compose restart
```

### More Help

- **[Quick Fix Guide](./QUICKFIX_GUIDE.md)** - Step-by-step fixes for common issues
- **[Detailed Troubleshooting](./backend/FIXES_README.md)** - In-depth explanations
- **[Backend Docs](./backend/README.md)** - API and backend setup
- **[Frontend Docs](./frontend/README.md)** - UI development guide
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

## Contributing

Please review the [agent documentation](./docs/AGENTS.md) to understand the project structure and workflows before contributing.

## License

*(To be determined)*