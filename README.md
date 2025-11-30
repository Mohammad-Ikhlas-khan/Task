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

### Running Tests
The project includes comprehensive unit tests for the scoring algorithm:

```bash
python run_tests.py
```

**Test Results**: ✅ **10 out of 10 tests passing**

**Test Coverage**: 10 unit tests covering:
1. Smart Balance strategy multi-factor prioritization
2. Fastest Wins strategy low-effort prioritization
3. High Impact strategy importance-based scoring
4. Deadline Driven strategy with overdue task handling
5. Dependency tracking and blocking task bonuses
6. Business days calculation accuracy
7. Score consistency and reproducibility


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

## 📋 Assumptions

### Task Management
1. **Multiple Tasks with Same Title**: The system allows multiple tasks to have the same title, but prevents exact duplicates. A task is considered a duplicate only if it has the same title AND the same importance, due_date, estimated_hours, and strategy.

2. **Task Persistence on Analysis**: When you click "Analyze Tasks", the system:
   - Calculates scores based on the selected strategy
   - Saves tasks to the database along with their score, explanation, and strategy
   - Prevents duplicate entries by checking if an identical task already exists
   - Returns an response if you try to analyze the exact same task with the same parameters

3. **Stored Scoring Information**: Unlike typical scoring systems, this application stores three additional fields with each task:
   - `score`: The calculated priority score
   - `explanation`: Human-readable explanation of the score
   - `strategy`: The strategy used to calculate the score
   
   This allows the system to maintain a history of how tasks were prioritized.

### Suggestion Logic
4. **Intelligent Task Suggestions**: The `/suggest/` endpoint uses a smart fallback hierarchy to provide daily recommendations:
   - **Priority 1**: Tasks due today or overdue (`due_date <= today`)
   - **Priority 2**: High-importance tasks (`importance > 5`)
   - **Priority 3**: Tasks with dependencies (non-empty dependency list)
   - **Priority 4**: Quick tasks (`estimated_hours < 5`)
   - **Priority 5**: All tasks (if none of the above criteria match)

5. **Suggestion Metadata**: Each suggestion includes a `based_on` field indicating which criteria was used to select it (e.g., "due_date_today", "importance", "dependencies", "estimated_hours", or "all").

### Dependency Handling
6. **Dependency Format**: Dependencies are stored as a JSON array of strings (task titles or IDs). The system does not validate whether dependent tasks exist in the database.

7. **Circular Dependencies**: The system does not currently prevent or detect circular dependencies. Users are responsible for ensuring dependency graphs are acyclic.

### Date and Time Calculations
8. **Business Days**: All deadline calculations use business days (Monday-Friday) and exclude Indian national holidays. Weekends and holidays are not counted toward deadline urgency.

9. **Timezone**: The system assumes all dates are in the server's local timezone. No timezone conversion is performed.

### Scoring and Prioritization
10. **Stored Scores**: Scores are stored in the database when tasks are analyzed. This means:
    - The score reflects the strategy used at the time of analysis
    - Changing strategies does not retroactively update existing task scores
    - The `/suggest/` endpoint uses stored scores rather than recalculating them

11. **Strategy Independence**: Each strategy calculates scores independently. The same task analyzed with different strategies will create separate database entries with different scores.

12. **Relative Scoring**: Scores are relative within a task set. A score of 50 in one analysis may represent different priority levels than a score of 50 in another analysis.

---

## 🎯 Design Decisions

### Architecture Choices

**Django Backend + Vanilla JavaScript Frontend**
- **Trade-off**: Chose simplicity over framework complexity
- **Rationale**: For a focused tool like this, a full React/Vue setup would be overkill. Django provides robust API handling and ORM capabilities, while vanilla JS keeps the frontend lightweight and dependency-free
- **Benefit**: Faster development, easier deployment, no build process needed

**Stored Scores with Strategy Tracking**
- **Decision**: Scores, explanations, and strategies are stored in the database alongside task data
- **Trade-off**: Database storage vs. real-time calculation
- **Rationale**: Storing scores creates a historical record of how tasks were prioritized. This allows users to see how the same task might be scored differently under different strategies or at different times
- **Benefit**: Maintains analysis history, enables comparison of different prioritization approaches
- **Limitation**: Scores don't automatically update when deadlines approach; tasks need to be re-analyzed

**Duplicate Prevention with Flexible Matching**
- **Decision**: Prevent exact duplicates by checking title + importance + due_date + estimated_hours + strategy
- **Trade-off**: Prevents database bloat but allows intentional variations
- **Rationale**: Users can have multiple tasks with the same title (e.g., "Team Meeting" every week) but prevents accidental re-submission of identical tasks. Changing any parameter or strategy creates a new entry, enabling "what-if" analysis
- **Benefit**: Clean database without restricting legitimate use cases
- **Implementation**: Uses Django's `filter().exists()` check before saving

**Business Days Calculation**
- **Decision**: Use NumPy's `busday_count` with Indian holidays
- **Trade-off**: Added dependency (NumPy) for accuracy
- **Rationale**: Calendar days are misleading for deadline urgency. A task due "in 3 days" on Friday is actually 5 calendar days away. Business day calculation provides realistic urgency metrics
- **Limitation**: Currently hardcoded to Indian holidays; could be made configurable

### API Design

**Analyze Endpoint with Persistence**
- The `/analyze/` endpoint accepts tasks via POST, calculates scores, and saves everything to the database
- Each task is stored with its score, explanation, and the strategy used
- Duplicate detection prevents accidental re-submission of identical tasks
- Returns sorted task list based on calculated scores

**Intelligent Suggest Endpoint**
- The `/suggest/` endpoint uses a smart fallback hierarchy to provide actionable daily recommendations:
  1. **Today's tasks first**: Prioritizes tasks due today or overdue
  2. **High-impact fallback**: If no tasks are due today, suggests high-importance tasks (>5)
  3. **Dependency-driven**: If no high-importance tasks, suggests tasks with dependencies
  4. **Quick wins**: If no dependent tasks, suggests quick tasks (<5 hours)
  5. **All tasks**: If none of the above, shows all tasks
- Returns top 3 tasks with a `based_on` field indicating which criteria was used
- Uses stored scores from the database rather than recalculating

**Strategy-Aware Task Management**
- Tasks store the strategy used for their score calculation
- The same task can exist multiple times with different strategies, creating a comparison view
- This enables users to see how different prioritization approaches would rank the same work

---

## ⏱️ Time Breakdown

| Section | Time Spent | Details |
|---------|-----------|---------|
| **Backend Development** | ~5 hours | Django models, views, scoring algorithm, API endpoints |
| **Scoring Algorithm** | ~2 hours | Implementing 4 strategies, business day calculation, dependency tracking |
| **Frontend Development** | ~3 hours | HTML/CSS layout, JavaScript API integration, UI/UX polish |
| **Testing & Debugging** | ~4 hours | Fixing duplicate task issue with same attributes, result persistence bug, API validation |
| **Documentation** | ~1 hour | Code comments, this README |
| **Total** | **~15 hours** | |

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

✅ **Comprehensive Unit Tests**
- Implemented 10 unit tests covering all scoring strategies
- Tests include edge cases like overdue tasks and dependency tracking
- Validates business day calculations and score consistency
- Achieves full coverage of the scoring algorithm

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
