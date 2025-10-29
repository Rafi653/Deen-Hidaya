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

### Quick Start

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
docker-compose up
```

This will start:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432

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

## Contributing

Please review the [agent documentation](./docs/AGENTS.md) to understand the project structure and workflows before contributing.

## License

*(To be determined)*