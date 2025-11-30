# Task Analyzer

A smart task prioritization system that helps you decide what to work on next by analyzing multiple factors including deadlines, importance, effort, and task dependencies.

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone and  navigate to the project directory**
   ```bash
   git clone https://github.com/Mohammad-Ikhlas-khan/Task.git
   cd task-analyzer
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:8000`
   - The frontend is served from the `frontend` directory
   - API endpoints are available at: `http://127.0.0.1:8000/api/tasks/`

### Quick Start
- **Analyze Tasks**: Fill in the task form or paste JSON data, then click "Analyze Tasks"
- **Get Suggestions**: Click "Get Suggestions" to see prioritized tasks from your database
- **Switch Strategies**: Use the dropdown to change prioritization strategies

---

## 🧠 Algorithm Explanation

### Overview
The Task Analyzer uses a sophisticated multi-factor scoring algorithm to prioritize tasks. The system considers four key dimensions: **urgency** (time to deadline), **importance** (user-defined priority), **effort** (estimated hours), and **dependencies** (blocking relationships).

### Core Mechanism

The algorithm calculates **business days to deadline** using NumPy's `busday_count` function, which excludes weekends and Indian national holidays. This ensures realistic time calculations that account for actual working days rather than calendar days.

Each task receives a numerical score based on the selected strategy, and tasks are ranked in descending order of priority. The system supports four distinct prioritization strategies:

### Prioritization Strategies

**1. Smart Balance (Default)**
This is the most sophisticated strategy that balances all factors:
- **Formula**: `score = importance × 3 - effort + urgency_factor + blocking_score`
- **Urgency Factor**: Tasks due within 10 business days get bonus points (10 - days_to_due)
- **Blocking Score**: Tasks that other tasks depend on receive +20 points per dependent task
- **Rationale**: This strategy prevents tunnel vision on any single metric. High-importance tasks get weighted heavily (3x multiplier), but quick wins (low effort) and urgent deadlines also influence the score. The dependency tracking ensures critical path tasks rise to the top.

**2. Fastest Wins**
Optimized for momentum and quick completions:
- **Formula**: `score = 100 - effort × 10 + importance`
- **Behavior**: Heavily penalizes high-effort tasks while giving slight weight to importance
- **Use Case**: When you need to clear your backlog quickly or build momentum through small victories

**3. High Impact**
Focuses purely on maximizing value:
- **Formula**: `score = importance × 10 - effort`
- **Behavior**: Importance dominates the score with a 10x multiplier, effort acts as a minor tiebreaker
- **Use Case**: When you need to focus on strategic, high-value work regardless of time constraints

**4. Deadline Driven**
Urgency-first approach with special handling for overdue tasks:
- **Formula (Overdue)**: `score = 200 + |days_overdue| × 5`
- **Formula (Upcoming)**: `score = 100 - days_to_due + importance`
- **Behavior**: Overdue tasks receive massive priority boosts, while upcoming deadlines create urgency
- **Use Case**: When you're in crisis mode or have hard external deadlines

### Technical Implementation

The scoring system leverages Python's `holidays` library to fetch Indian national holidays dynamically based on the current year and task due date year. This ensures accuracy across year boundaries. The dependency analysis performs a graph traversal to identify blocking tasks, enabling critical path prioritization in the Smart Balance strategy.

All strategies return both a numerical score and a human-readable explanation that shows which factors influenced the prioritization, providing transparency into the decision-making process.

---

## 🎯 Design Decisions

### Architecture Choices

**Django Backend + Vanilla JavaScript Frontend**
- **Trade-off**: Chose simplicity over framework complexity
- **Rationale**: For a focused tool like this, a full React/Vue setup would be overkill. Django provides robust API handling and ORM capabilities, while vanilla JS keeps the frontend lightweight and dependency-free
- **Benefit**: Faster development, easier deployment, no build process needed

**In-Memory Scoring vs. Database Storage**
- **Decision**: Scores are calculated on-demand, not stored in the database
- **Trade-off**: Slight performance cost vs. data consistency
- **Rationale**: Task priorities change as deadlines approach and dependencies shift. Storing scores would require complex cache invalidation logic. Real-time calculation ensures scores are always accurate
- **Optimization**: For large task lists (>1000 tasks), this could be optimized with caching

**Business Days Calculation**
- **Decision**: Use NumPy's `busday_count` with Indian holidays
- **Trade-off**: Added dependency (NumPy) for accuracy
- **Rationale**: Calendar days are misleading for deadline urgency. A task due "in 3 days" on Friday is actually 5 calendar days away. Business day calculation provides realistic urgency metrics
- **Limitation**: Currently hardcoded to Indian holidays; could be made configurable

**Update-or-Create Pattern**
- **Decision**: Tasks are identified by title using `update_or_create`
- **Trade-off**: Prevents duplicates but limits title flexibility
- **Rationale**: Avoids database bloat from repeated analysis of the same tasks. Users can re-analyze tasks with updated parameters without creating duplicates
- **Limitation**: Two genuinely different tasks can't have the same title

### API Design

**Stateless Analysis Endpoint**
- The `/analyze/` endpoint accepts tasks via POST and returns scored results without requiring prior database storage
- This allows users to experiment with different task sets without polluting their database
- Tasks are stored for future suggestions, creating a persistent task library

**Separate Suggest Endpoint**
- The `/suggest/` endpoint works only with stored tasks, providing top-3 recommendations
- This separation allows users to maintain a task database and get quick recommendations without re-entering data

---

## ⏱️ Time Breakdown

| Section | Time Spent | Details |
|---------|-----------|---------|
| **Backend Development** | ~3 hours | Django models, views, scoring algorithm, API endpoints |
| **Scoring Algorithm** | ~2 hours | Implementing 4 strategies, business day calculation, dependency tracking |
| **Frontend Development** | ~2 hours | HTML/CSS layout, JavaScript API integration, UI/UX polish |
| **Testing & Debugging** | ~2 hours | Fixing duplicate task issue, result persistence bug, API validation |
| **Documentation** | ~1 hour | Code comments, this README |
| **Total** | **~10 hours** | |

### Key Milestones
- Initial Django setup and models: 30 minutes
- Scoring algorithm core logic: 1.5 hours
- Business day calculation integration: 1 hour
- Frontend UI design: 1.5 hours
- API integration and testing: 2 hours
- Bug fixes (duplicates, disappearing results): 1.5 hours
- Strategy implementation and refinement: 1 hour
- Final polish and documentation: 1 hour

---

## 🎁 Bonus Challenges

### Attempted Challenges

✅ **Data Intelligence**
- Integrated NumPy's `busday_count` for accurate deadline urgency
- Excludes weekends and Indian national holidays
- Provides realistic time-to-deadline metrics

---

## 🚧 Future Improvements

### High Priority
1. **Configurable Holidays**: Allow users to select their country/region for holiday calculations
2. **Task Completion**: Add ability to mark tasks as complete and track completion history
3. **Better Duplicate Handling**: Use UUIDs instead of titles for task identification
4. **Dependency Validation**: Prevent circular dependencies and validate task IDs exist
5. **Performance Optimization**: Add caching for large task lists (100+ tasks)

### Medium Priority
6. **Export Functionality**: Export prioritized task lists as CSV/PDF
7. **Recurring Tasks**: Support for daily/weekly/monthly recurring tasks
8. **Time Tracking**: Integrate actual time spent vs. estimated hours
9. **Mobile Responsiveness**: Optimize UI for mobile devices
10. **Dark Mode**: Add theme toggle for better UX

### Nice to Have
11. **Dependency Graph Visualization**: Interactive graph showing task relationships using D3.js or similar
12. **AI-Powered Estimates**: Use historical data to suggest realistic effort estimates
13. **Team Collaboration**: Multi-user support with shared task pools
14. **Calendar Integration**: Sync with Google Calendar/Outlook
15. **Analytics Dashboard**: Visualize productivity trends, completion rates, and time allocation

### Technical Debt
- Add comprehensive unit tests for scoring algorithm
- Implement proper error logging and monitoring
- Add API rate limiting for production deployment
- Migrate to PostgreSQL for production use
- Add input sanitization and security hardening

---

## 📝 API Reference

### Analyze Tasks
**Endpoint**: `POST /api/tasks/analyze/?strategy=<strategy_name>`

**Request Body**:
```json
[
  {
    "title": "Task name",
    "due_date": "2025-12-15",
    "estimated_hours": 5,
    "importance": 8,
    "dependencies": ["task-id-1", "task-id-2"]
  }
]
```

**Response**:
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Task name",
      "due_date": "2025-12-15",
      "estimated_hours": 5,
      "importance": 8,
      "dependencies": [],
      "score": 45.5,
      "explanation": "Strategy: Smart Balance - Importance: 8/10, Effort: 5h, Due in 10 business days, Blocks: 0 tasks"
    }
  ]
}
```

### Get Suggestions
**Endpoint**: `GET /api/tasks/suggest/?strategy=<strategy_name>`

**Response**: Returns top 3 prioritized tasks from database

---

## 🛠️ Technology Stack

- **Backend**: Django 5.2.8
- **Database**: SQLite (development), PostgreSQL recommended for production
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Libraries**: 
  - NumPy (business day calculations)
  - python-holidays (holiday tracking)
  - django-cors-headers (CORS support)

---

## 📄 License

This project is open source and available for educational and personal use.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

**Built with ❤️ for better productivity**
