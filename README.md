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

## Future Scope

Deen-Hidaya aims to evolve beyond the MVP into a comprehensive Islamic knowledge platform. The following features and enhancements are planned for future releases:

### Phase 2: Enhanced Learning Features
- **Tafsir (Commentary) Integration**: Add classical and contemporary Quranic commentaries from various scholars
- **Hadith Database**: Comprehensive collection of authentic Hadith with search and cross-referencing
- **Translation Comparison**: Side-by-side view of multiple translations for deeper understanding
- **Word-by-Word Analysis**: Interactive word-level breakdown with Arabic grammar and root words
- **Personalized Learning Paths**: AI-driven recommendations based on user interests and reading history

### Phase 3: Community & Interaction
- **Discussion Forums**: Moderated Q&A platform for Islamic scholarship and learning
- **Study Groups**: Virtual study circles with scheduling and video integration
- **Scholar Verification System**: Verified accounts for Islamic scholars and institutions
- **User Notes & Bookmarks**: Personal annotation system with cloud sync
- **Social Sharing**: Share verses, insights, and reflections (with privacy controls)

### Phase 4: Advanced Features
- **Mobile Applications**: Native iOS and Android apps with offline capabilities
- **Multilingual Support**: Interface and content in 20+ languages including Arabic, Urdu, Turkish, Indonesian
- **Advanced Audio Features**: Adjustable playback speed, repeat modes, memorization tools
- **Smart Search**: Context-aware semantic search with AI understanding
- **Educational Content**: Structured courses, quizzes, and certification programs
- **Prayer Times & Qibla**: Location-based prayer reminders and direction finder
- **Islamic Calendar**: Hijri calendar with important dates and reminders

### Phase 5: Institutional Features
- **Madrasa Management**: Tools for Islamic schools and educational institutions
- **API for Developers**: Public API for third-party applications
- **White-Label Solutions**: Customizable platform for mosques and organizations
- **Analytics Dashboard**: Insights for administrators and content creators
- **Content Management System**: Tools for scholars to contribute and manage content

### Long-term Vision
- **Accessibility First**: Full WCAG AAA compliance and support for assistive technologies
- **Offline-First Architecture**: Complete functionality without internet connectivity
- **Open Source Contributions**: Release core components to benefit the wider community
- **Research Integration**: Partner with Islamic research institutions for authentic content
- **Global Reach**: Serve Muslims worldwide with culturally appropriate content

## Rollout Plan

The Deen-Hidaya project follows a phased rollout approach to ensure quality, gather feedback, and iterate based on user needs.

### Phase 0: Foundation (Current - Weeks 1-2)
**Goal**: Establish project structure and development workflows

- ✅ Define agent roles and responsibilities
- ✅ Create project documentation
- ✅ Set up GitHub labels and project board
- 🔄 Configure CI/CD pipelines
- 🔄 Set up development environments

**Deliverable**: Development infrastructure ready for feature implementation

### Phase 1: MVP Development (Weeks 3-8)
**Goal**: Build core features for initial release

**Weeks 3-4: Backend Foundation**
- Database schema design and implementation (#3)
- Data scraping and ingestion pipeline (#4)
- Basic API endpoints with FastAPI
- Initial data loading (Quran text, translations)

**Weeks 5-6: Core Features**
- Basic search functionality (#5)
- Semantic search with embeddings (#6)
- Audio file management (#7)
- API documentation with OpenAPI

**Weeks 7-8: Frontend Development**
- Quran reader interface (#8)
- Audio player component (#10)
- Responsive design implementation
- Accessibility compliance (WCAG 2.1 AA)

**Deliverable**: Functional MVP with core reading and search features

### Phase 2: Testing & Refinement (Weeks 9-10)
**Goal**: Ensure quality and reliability

- Comprehensive testing strategy implementation (#11)
- Bug fixing and performance optimization
- Security audit and vulnerability remediation
- User acceptance testing with focus group
- Documentation completion

**Deliverable**: Production-ready MVP

### Phase 3: Beta Launch (Weeks 11-12)
**Goal**: Soft launch to limited audience

- Deploy to staging environment
- Beta user onboarding (100-500 users)
- Collect feedback through surveys and analytics
- Monitor performance and error rates
- Iterate based on user feedback

**Deliverable**: Beta version with real user validation

### Phase 4: Public Launch (Week 13)
**Goal**: Official release to public

- Marketing and announcement preparation
- Deploy to production with monitoring
- Community building on social media
- Create user onboarding materials
- Establish support channels

**Deliverable**: Publicly available Deen-Hidaya MVP

### Phase 5: Post-Launch Iteration (Weeks 14-16)
**Goal**: Stabilize and enhance based on feedback

- Address high-priority user feedback
- Performance optimization based on real usage
- Content expansion (more translations, reciters)
- Bug fixes and stability improvements
- Prepare roadmap for Phase 2 features

**Deliverable**: Stable v1.0 with satisfied user base

### Success Metrics

Each phase will be measured against specific KPIs:

**MVP Phase:**
- All core features (#2-#11) completed and tested
- 0 critical bugs, <5 high-priority bugs
- Page load time <3s on 3G connection
- Lighthouse score >90 for accessibility

**Beta Phase:**
- 100+ active beta users
- User satisfaction score >4.0/5.0
- <2% error rate in critical user flows
- 90%+ feature completion rate

**Launch Phase:**
- 1,000+ users in first month
- 70%+ user retention after first week
- <1% crash rate
- Positive community feedback

### Risk Mitigation

**Technical Risks:**
- **Database performance**: Early load testing and optimization
- **Audio streaming**: CDN implementation and caching strategy
- **Search quality**: Iterative refinement with user feedback

**Content Risks:**
- **Data accuracy**: Multiple source verification and review process
- **Copyright compliance**: Legal review of all scraped content
- **Translation quality**: Collaborate with verified Islamic scholars

**Timeline Risks:**
- **Scope creep**: PM agent strictly enforces MVP boundaries
- **Resource constraints**: Focus on must-have features only
- **Integration delays**: Weekly dependency review meetings

### Next Steps

1. **Immediate (This Week)**: Complete GitHub setup, create labels, assign initial issues
2. **Short-term (Next 2 Weeks)**: Begin backend development, finalize database schema
3. **Medium-term (4-6 Weeks)**: Complete API and frontend implementation
4. **Long-term (8+ Weeks)**: Testing, beta launch, and public release

## Contributing

Please review the [agent documentation](./docs/AGENTS.md) to understand the project structure and workflows before contributing.

## License

*(To be determined)*