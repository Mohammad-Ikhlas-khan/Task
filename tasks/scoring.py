from .models import Task
from datetime import date
import numpy as np
import holidays
def score_task(task: Task, strategy="smart_balance", task_list=None):
    
    # Calculate business days (excluding weekends and holidays)
    year1 = date.today().year
    year2=task.due_date.year
    holidays_list= holidays.CountryHoliday('IN', years=range(year1, year2+1))
    print(f"Holidays considered for scoring: {holidays_list}")
    days_to_due = np.busday_count(
        date.today().isoformat(), 
        task.due_date.isoformat(),
        holidays=list(holidays_list)
    )
    
    print(f"Days to due for task {task.id}: {days_to_due} business days")
    importance = task.importance
    effort = task.estimated_hours

    if strategy == "fastest_wins":
        # Lowest effort gets highest score
        score = 100 - effort * 10 + (importance)  # effort dominates
        explanation = f"Strategy: Fastest Wins - Lower effort prioritized. Effort: {effort}h"
    elif strategy == "high_impact":
        # Importance dominates
        score = importance * 10 - effort 
        explanation = f"Strategy: High Impact - Importance prioritized. Importance: {importance}/10"
    elif strategy == "deadline_driven":
        # Urgency/due dominates, overdue tasks get bonus
        if days_to_due < 0:
            score = 200 + abs(days_to_due) * 5  # Overdue boosted
            explanation = f"Strategy: Deadline Driven - Overdue by {abs(days_to_due)} business days [HIGH PRIORITY]"
        else:
            score = 100 - days_to_due + importance
            explanation = f"Strategy: Deadline Driven - Due in {days_to_due} business days"
    else:
        # smart_balance (default): combines all
        block_score = 0
        if task_list:
            # Score higher if other tasks depend on this
            task_id = str(task.id if task.id else "")
            for t in task_list:
                deps = t.dependencies if isinstance(t.dependencies, list) else []
                if task_id and task_id in deps:
                    block_score += 20
        # Blend: overdue, soon due, important, low effort, blocks others
        score = importance*3 - effort + (0 if days_to_due < 0 else max(0, 10-days_to_due)) + block_score
        explanation = f"Strategy: Smart Balance - Importance: {importance}/10, Effort: {effort}h, Due in {days_to_due} business days, Blocks: {block_score//20} tasks"
    return score, explanation