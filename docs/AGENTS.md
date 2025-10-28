# Deen Hidaya Project Agents

This document provides an overview of the cross-functional agents for the Deen Hidaya MVP project. Each agent has clearly defined roles, responsibilities, and areas of ownership to ensure accountability and efficient collaboration.

## Overview

The Deen Hidaya project uses 5 specialized agents to manage different aspects of the MVP development:

| Agent | Label | Focus Area | Primary Issues |
|-------|-------|------------|----------------|
| **PM** | `role:pm` | Product Management | #1 (Roadmap) |
| **Lead/Architect** | `role:lead` | Architecture & Code Review | All technical decisions |
| **Frontend** | `role:frontend` | User Interface | #8 (Reader UI), #10 (Audio Player) |
| **Backend** | `role:backend` | Server & Data | #3, #4, #5, #6, #7 |
| **QA** | `role:qa` | Quality & Testing | #11 (Testing), Verifies #2–#10 |

## Agent Details

### 1. PM (Product Manager)
**Location**: [docs/agents/PM.md](./agents/PM.md)

**Key Responsibilities**:
- Maintain master roadmap (#1)
- Track milestones and deliverables
- Manage risks and compliance
- Coordinate across all agents
- Define and verify acceptance criteria

**When to Engage**: Scope questions, priority conflicts, timeline concerns, licensing/compliance issues

---

### 2. Lead/Reviewer/Architect
**Location**: [docs/agents/LEAD.md](./agents/LEAD.md)

**Key Responsibilities**:
- Define system architecture
- Review all pull requests
- Maintain CI/CD pipelines
- Enforce code quality standards
- Approve major technical decisions

**When to Engage**: Architectural decisions, code review questions, CI/CD issues, new technology adoption

---

### 3. Frontend
**Location**: [docs/agents/FRONTEND.md](./agents/FRONTEND.md)

**Key Responsibilities**:
- Implement Quran reader UI (#8)
- Build audio player interface (#10)
- Ensure WCAG 2.1 AA accessibility
- Implement theme support
- Optimize frontend performance

**When to Engage**: UI/UX questions, accessibility requirements, component design, frontend performance

---

### 4. Backend
**Location**: [docs/agents/BACKEND.md](./agents/BACKEND.md)

**Key Responsibilities**:
- Design database schema (#3)
- Implement data scraping/ingestion (#4)
- Build search functionality (#5)
- Create semantic search with embeddings (#6)
- Manage audio files (#7)
- Develop FastAPI endpoints

**When to Engage**: API design, database decisions, data pipeline questions, search optimization, performance tuning

---

### 5. QA/Tester
**Location**: [docs/agents/QA.md](./agents/QA.md)

**Key Responsibilities**:
- Define test strategy (#11)
- Verify acceptance criteria for all features
- Execute manual and automated tests
- Ensure demo reproducibility
- Report and track bugs
- Validate accessibility and performance

**When to Engage**: Acceptance criteria review, test strategy, bug prioritization, demo preparation

---

## Issue Mapping

### Issue Ownership Matrix

| Issue | PM | Lead | Frontend | Backend | QA |
|-------|----|----|----------|---------|-----|
| #1 - Master Roadmap | **Owner** | Review | - | - | - |
| #2 - Basic Quran Display | Define | Review | Support | Support | **Verify** |
| #3 - Database Schema | Define | **Approve** | - | **Owner** | **Verify** |
| #4 - Data Scraping | Define | Review | - | **Owner** | **Verify** |
| #5 - Search | Define | Review | - | **Owner** | **Verify** |
| #6 - Embeddings | Define | **Approve** | - | **Owner** | **Verify** |
| #7 - Audio Management | Define | Review | - | **Owner** | **Verify** |
| #8 - Reader UI | Define | Review | **Owner** | Support | **Verify** |
| #9 - (Future) | Define | Review | TBD | TBD | **Verify** |
| #10 - Audio Player UI | Define | Review | **Owner** | Support | **Verify** |
| #11 - Demo/Testing | Define | Review | Support | Support | **Owner** |

**Legend**:
- **Owner**: Primary responsibility for implementation
- **Approve**: Must approve architectural/technical decisions
- **Review**: Reviews PRs and provides feedback
- **Support**: Provides assistance as needed
- **Verify**: Tests and validates acceptance criteria
- **Define**: Defines requirements and acceptance criteria

---

## GitHub Labels

The following labels should be created in the GitHub repository to tag issues and PRs by responsible agent:

### Role Labels
- `role:pm` - Product Management issues
- `role:lead` - Architecture and technical leadership
- `role:frontend` - Frontend implementation
- `role:backend` - Backend implementation  
- `role:qa` - Testing and quality assurance

### Creating Labels
To create these labels in GitHub:
1. Navigate to the repository: https://github.com/Rafi653/Deen-Hidaya
2. Go to **Issues** → **Labels**
3. Click **New label** for each role label
4. Use the following configurations:

| Label | Color | Description |
|-------|-------|-------------|
| `role:pm` | `#7057ff` | Product management and planning |
| `role:lead` | `#d73a4a` | Architecture and code review |
| `role:frontend` | `#0075ca` | Frontend development |
| `role:backend` | `#008672` | Backend development |
| `role:qa` | `#e99695` | Quality assurance and testing |

Alternatively, use the GitHub CLI:
```bash
gh label create "role:pm" --color "7057ff" --description "Product management and planning"
gh label create "role:lead" --color "d73a4a" --description "Architecture and code review"
gh label create "role:frontend" --color "0075ca" --description "Frontend development"
gh label create "role:backend" --color "008672" --description "Backend development"
gh label create "role:qa" --color "e99695" --description "Quality assurance and testing"
```

---

## Collaboration Workflow

### Issue Creation Flow
1. **PM** creates issue with requirements and acceptance criteria
2. **Lead** reviews technical feasibility and architecture impact
3. **Frontend/Backend** (as applicable) estimates effort and identifies dependencies
4. **QA** reviews acceptance criteria and adds test scenarios
5. **PM** prioritizes and assigns to appropriate agent(s)

### Development Flow
1. **Frontend/Backend** implements feature following acceptance criteria
2. **Lead** reviews PR for code quality, architecture, and standards
3. **QA** tests the implementation against acceptance criteria
4. **PM** validates business requirements are met
5. **Lead** merges if all gates pass

### Code Review Standards
All PRs must be reviewed by **Lead** and should:
- Pass all CI/CD checks (linting, tests, build)
- Meet code quality standards
- Include appropriate tests
- Update documentation as needed
- Address security concerns

### Definition of Done
A feature is considered complete when:
- [ ] Implementation meets acceptance criteria
- [ ] Code reviewed and approved by **Lead**
- [ ] All tests pass (unit, integration, E2E)
- [ ] **QA** has verified and signed off
- [ ] Documentation updated
- [ ] **PM** approves business requirements met
- [ ] Demo scenario is reproducible

---

## Project Board (Optional)

Consider creating a GitHub Project Board to visualize work across agents:

### Recommended Columns
1. **Backlog** - Issues not yet started
2. **In Progress** - Active development
3. **Review** - Code review by Lead
4. **Testing** - QA verification
5. **Done** - Completed and merged

### Board Views
- **By Agent**: Group issues by role label
- **By Sprint**: Track weekly/bi-weekly progress
- **By Priority**: Focus on critical path items

To create the project board:
1. Go to the repository's **Projects** tab
2. Click **New project**
3. Choose **Board** template
4. Add custom columns as listed above
5. Link issues using role labels for filtering

---

## Communication Guidelines

### Daily Standup Template
Each agent reports:
- **Yesterday**: What was completed
- **Today**: What will be worked on
- **Blockers**: Any impediments or help needed

### Weekly Sync Template
- **PM**: Roadmap updates, priority changes, risks
- **Lead**: Architecture decisions, technical debt, PR review stats
- **Frontend**: UI progress, accessibility status, design questions
- **Backend**: API development, data pipeline status, performance metrics
- **QA**: Test coverage, bug trends, quality metrics

### Escalation Path
1. **Agent-to-Agent**: Direct collaboration for routine issues
2. **To Lead**: Technical decisions, code quality concerns
3. **To PM**: Scope changes, timeline risks, resource needs

---

## Success Metrics

### PM Metrics
- On-time delivery of milestones
- Scope creep (target: <10%)
- Stakeholder satisfaction
- Risk mitigation effectiveness

### Lead Metrics
- PR review turnaround time (target: <24h)
- Code quality scores (SonarQube, CodeClimate)
- CI/CD pipeline reliability (target: >99%)
- Technical debt trend (should decrease)

### Frontend Metrics
- Lighthouse scores (target: >90)
- Accessibility compliance (WCAG AA)
- Load time (target: <3s on 3G)
- Cross-browser compatibility

### Backend Metrics
- API response time p95 (target: <100ms)
- Test coverage (target: >80%)
- Uptime (target: >99.9%)
- Database query performance

### QA Metrics
- Test coverage (target: >90% for critical paths)
- Bug escape rate (target: <1%)
- Time to find bugs (earlier is better)
- Acceptance criteria completeness

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-28 | 1.0 | Initial agent definitions | System |

---

## Next Steps

1. **Create GitHub Labels**: Use the commands above to create role labels
2. **Assign Issues**: Review existing issues #1–#11 and assign appropriate role labels
3. **Create Project Board**: Set up visualization for cross-agent workflow (optional)
4. **Onboard Team**: Share agent documentation with all team members
5. **First Sprint Planning**: PM to schedule initial planning session with all agents

---

For detailed information about each agent, refer to their individual documentation in the `docs/agents/` directory.
