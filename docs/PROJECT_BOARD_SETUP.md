# Project Board Setup Guide

This guide explains how to create and configure a GitHub Project Board for the Deen Hidaya project to visualize work across all agents.

## Quick Setup

### Option 1: Using GitHub Web Interface

1. **Navigate to Projects**
   - Go to https://github.com/Rafi653/Deen-Hidaya
   - Click the **Projects** tab
   - Click **New project**

2. **Choose Template**
   - Select **Board** view
   - Name: "Deen Hidaya MVP"
   - Description: "Cross-functional workflow tracking for MVP development"

3. **Configure Columns**
   
   Create the following columns (in order):
   
   | Column | Description | Automation |
   |--------|-------------|------------|
   | 📋 Backlog | Issues not yet started | - |
   | 🏗️ In Progress | Active development work | Auto-move when issue assigned |
   | 👀 Review | Code review by Lead | Auto-move when PR opened |
   | ✅ Testing | QA verification | Auto-move when PR approved |
   | ✨ Done | Completed and merged | Auto-move when issue closed |

4. **Add Custom Fields** (Optional)
   
   Click **+** to add fields:
   - **Agent**: Single select (PM, Lead, Frontend, Backend, QA)
   - **Priority**: Single select (Critical, High, Medium, Low)
   - **Sprint**: Text (e.g., "Sprint 1", "Sprint 2")
   - **Effort**: Number (story points or hours)

### Option 2: Using GitHub Projects (Beta)

GitHub Projects (beta) offers more advanced features:

1. **Create New Project**
   - Go to https://github.com/orgs/Rafi653/projects (or user projects)
   - Click **New project**
   - Choose **Table** or **Board** view

2. **Configure Views**
   
   **Board View** - Default kanban board:
   - Group by: Status
   - Columns: Backlog → In Progress → Review → Testing → Done
   
   **Agent View** - Filter by role:
   - Group by: Labels (role:pm, role:lead, etc.)
   - Shows work assigned to each agent
   
   **Sprint View** - Track iterations:
   - Filter by: Sprint field
   - Group by: Status
   
   **Priority View** - Focus on critical work:
   - Sort by: Priority (Critical first)
   - Filter: Show only High and Critical

3. **Set Up Workflows** (Automation)
   
   Configure automated workflows:
   
   ```yaml
   # Auto-add items
   - When: Issue created with label role:*
     Then: Add to project in "Backlog" column
   
   # Track progress
   - When: Issue assigned
     Then: Move to "In Progress"
   
   - When: PR opened
     Then: Move to "Review"
   
   - When: PR approved
     Then: Move to "Testing"
   
   - When: Issue closed
     Then: Move to "Done"
   ```

## Manual Setup Instructions

If you prefer to set up the board manually:

### Step 1: Create Columns

```
Backlog
├── New issues awaiting triage
├── Refined issues ready to start
└── Prioritized by PM

In Progress
├── Issues currently being worked on
├── Should have assignee
└── Should have role label

Review
├── PRs awaiting Lead review
├── Code quality checks in progress
└── Architecture validation

Testing
├── QA verification in progress
├── Acceptance testing
└── Bug fixes needed

Done
├── Merged to main
├── Deployed to environment
└── Acceptance criteria met
```

### Step 2: Add Existing Issues

1. Click **Add item** in the Backlog column
2. Search for issues #1–#11
3. Add them to the board
4. Drag to appropriate columns based on current status

### Step 3: Configure Filters

Create saved filters for quick access:

**By Agent**:
- PM Work: `is:issue label:role:pm`
- Lead Work: `is:issue label:role:lead`
- Frontend Work: `is:issue label:role:frontend`
- Backend Work: `is:issue label:role:backend`
- QA Work: `is:issue label:role:qa`

**By Status**:
- Open Issues: `is:open is:issue`
- Open PRs: `is:open is:pr`
- Blocked: `is:open label:blocked`

**By Priority** (after adding priority labels):
- Critical: `is:open label:priority:critical`
- High Priority: `is:open label:priority:high`

## Recommended Workflow

### Daily Use

1. **Morning**:
   - Each agent reviews their filtered view
   - Moves cards from Backlog to In Progress
   - Updates card status

2. **During Development**:
   - Move card to Review when PR is ready
   - Lead reviews and approves or requests changes
   - Move to Testing when approved

3. **End of Day**:
   - Update card comments with progress
   - Flag blockers with `blocked` label
   - Move completed items to Done

### Weekly Planning

1. **PM** leads planning session:
   - Review Done column (celebrate wins!)
   - Groom Backlog (add/refine issues)
   - Prioritize for next sprint
   - Assign to agents

2. **Team** reviews board:
   - Discuss blockers
   - Re-estimate if needed
   - Identify dependencies

### Sprint Boundaries

At the end of each sprint:
1. Archive Done items (optional)
2. Move incomplete items back to Backlog
3. Review velocity and adjust estimates
4. Plan next sprint

## Integration with Labels

Ensure all cards have appropriate labels for filtering:

**Role Labels** (who owns it):
- `role:pm`
- `role:lead`
- `role:frontend`
- `role:backend`
- `role:qa`

**Type Labels**:
- `enhancement` - New feature
- `bug` - Bug fix
- `documentation` - Documentation update
- `infrastructure` - DevOps/tooling

**Status Labels** (optional, if not using columns):
- `status:backlog`
- `status:in-progress`
- `status:review`
- `status:testing`
- `status:blocked`

**Priority Labels**:
- `priority:critical` - Drop everything
- `priority:high` - Next in queue
- `priority:medium` - Normal priority
- `priority:low` - Nice to have

## Tips for Success

### DO:
✅ Keep cards up to date
✅ Add comments with blockers or questions
✅ Use labels consistently
✅ Review board daily
✅ Link related issues and PRs
✅ Celebrate moving cards to Done!

### DON'T:
❌ Let cards sit in Review for days
❌ Skip Testing column
❌ Move incomplete work to Done
❌ Create duplicate cards
❌ Forget to assign cards to people

## Metrics to Track

Use GitHub Insights or manual tracking:

1. **Cycle Time**: Time from In Progress → Done
2. **Lead Time**: Time from Backlog → Done
3. **Work in Progress**: Number of items in In Progress
4. **Throughput**: Items completed per week
5. **Blocked Time**: Time spent blocked

## Example Board States

### Early Sprint
```
Backlog: 20 items
In Progress: 5 items
Review: 1 item
Testing: 0 items
Done: 0 items
```

### Mid Sprint
```
Backlog: 15 items
In Progress: 8 items
Review: 3 items
Testing: 2 items
Done: 5 items
```

### End Sprint
```
Backlog: 10 items
In Progress: 2 items
Review: 1 item
Testing: 1 item
Done: 18 items
```

## Resources

- [GitHub Projects Docs](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Project Automation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project)
- [Best Practices](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects)

## Next Steps

After setting up the board:

1. ✅ Create GitHub labels using `scripts/create-labels.sh`
2. ✅ Set up the project board following this guide
3. ✅ Add existing issues #1–#11 to the board
4. ✅ Apply role labels to all issues
5. ✅ Configure automation workflows
6. ✅ Train team on using the board
7. ✅ Schedule weekly board review meetings

---

Need help? Contact the PM agent or refer to [docs/AGENTS.md](./AGENTS.md) for team structure.
