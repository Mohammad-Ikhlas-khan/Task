from .models import Task
from datetime import date
import numpy as np
import holidays
def score_task(task: Task, strategy="smart_balance", task_list=None):
    
    count_days_past_due=(task.due_date-date.today()).days
    if  count_days_past_due < -30:
        raise ValueError("Due date is too far in the past.")
    # Calculate business days (excluding weekends and holidays)
    if task.importance < 1 or task.importance > 10:
        raise ValueError("Importance must be between 1 and 10.")
    if task.estimated_hours < 1:
        raise ValueError("Estimated hours must be at least 1.")
    
    year1 = date.today().year
    year2=task.due_date.year
    holidays_list= holidays.CountryHoliday('IN', years=range(year1, year2+1))
    if count_days_past_due >= 0 :
        days_to_due = np.busday_count(
            date.today().isoformat(), 
            task.due_date.isoformat(),
            holidays=list(holidays_list)
        )
    else:
        days_to_due = -np.busday_count(
            task.due_date.isoformat(),
            date.today().isoformat(),
            holidays=list(holidays_list)
        )
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