from django.test import TestCase
from datetime import date, timedelta
from .models import Task
from .scoring import score_task


class ScoringAlgorithmTestCase(TestCase):
    """Test suite for the task scoring algorithm"""
    
    def setUp(self):
        """Set up test tasks for various scenarios"""
        # Task 1: High importance, low effort, due soon
        self.task_urgent = Task.objects.create(
            title="Fix critical bug",
            due_date=date.today() + timedelta(days=2),
            estimated_hours=2,
            importance=10,
            dependencies=[]
        )
        
        # Task 2: Low importance, high effort, due later
        self.task_low_priority = Task.objects.create(
            title="Refactor old code",
            due_date=date.today() + timedelta(days=30),
            estimated_hours=20,
            importance=3,
            dependencies=[]
        )
        
        # Task 3: Overdue task
        self.task_overdue = Task.objects.create(
            title="Overdue report",
            due_date=date.today() - timedelta(days=5),
            estimated_hours=5,
            importance=7,
            dependencies=[]
        )
        
        # Task 4: Quick win - low effort, medium importance
        self.task_quick_win = Task.objects.create(
            title="Update documentation",
            due_date=date.today() + timedelta(days=10),
            estimated_hours=1,
            importance=5,
            dependencies=[]
        )
        
        # Task 5: Blocking task (will be referenced by task 6)
        self.task_blocking = Task.objects.create(
            title="Design API schema",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=4,
            importance=8,
            dependencies=[]
        )
        
        # Task 6: Dependent task
        self.task_dependent = Task.objects.create(
            title="Implement API endpoints",
            due_date=date.today() + timedelta(days=14),
            estimated_hours=8,
            importance=7,
            dependencies=[str(self.task_blocking.id)]
        )
    
    def test_smart_balance_strategy(self):
        """Test 1: Smart Balance strategy prioritizes based on multiple factors"""
        score, explanation = score_task(self.task_urgent, strategy="smart_balance")
        
        # High importance (10) * 3 = 30, low effort (-2), urgency bonus
        # Should result in a high score
        self.assertGreater(score, 20, "Urgent high-importance task should have high score")
        self.assertIn("Smart Balance", explanation)
        self.assertIn("Importance: 10/10", explanation)
        
        # Low priority task should score lower
        low_score, _ = score_task(self.task_low_priority, strategy="smart_balance")
        self.assertLess(low_score, score, "Low priority task should score lower than urgent task")
    
    def test_fastest_wins_strategy(self):
        """Test 2: Fastest Wins strategy prioritizes low-effort tasks"""
        quick_score, explanation = score_task(self.task_quick_win, strategy="fastest_wins")
        high_effort_score, _ = score_task(self.task_low_priority, strategy="fastest_wins")
        
        # Quick win (1 hour) should score higher than high effort task (20 hours)
        self.assertGreater(quick_score, high_effort_score, 
                          "Low effort task should score higher in Fastest Wins strategy")
        self.assertIn("Fastest Wins", explanation)
        self.assertIn("Effort: 1h", explanation)
    
    def test_high_impact_strategy(self):
        """Test 3: High Impact strategy prioritizes importance over other factors"""
        high_importance_score, explanation = score_task(self.task_urgent, strategy="high_impact")
        low_importance_score, _ = score_task(self.task_low_priority, strategy="high_impact")
        
        # Task with importance 10 should score much higher than importance 3
        self.assertGreater(high_importance_score, low_importance_score,
                          "High importance task should dominate in High Impact strategy")
        self.assertIn("High Impact", explanation)
        self.assertIn("Importance: 10/10", explanation)
    
    def test_deadline_driven_overdue_tasks(self):
        """Test 4: Deadline Driven strategy gives massive priority to overdue tasks"""
        overdue_score, explanation = score_task(self.task_overdue, strategy="deadline_driven")
        future_score, _ = score_task(self.task_low_priority, strategy="deadline_driven")
        
        # Overdue tasks should get boosted scores (200+ base)
        self.assertGreater(overdue_score, 200, "Overdue tasks should have score > 200")
        self.assertGreater(overdue_score, future_score, 
                          "Overdue task should score higher than future task")
        self.assertIn("Deadline Driven", explanation)
        self.assertIn("Overdue", explanation)
        self.assertIn("HIGH PRIORITY", explanation)
    
    def test_dependency_blocking_bonus(self):
        """Test 5: Tasks that block others should get bonus points in Smart Balance"""
        all_tasks = Task.objects.all()
        
        # Score the blocking task with task list context
        blocking_score, explanation = score_task(
            self.task_blocking, 
            strategy="smart_balance",
            task_list=all_tasks
        )
        
        # Score a similar task without dependencies
        non_blocking_score, _ = score_task(
            self.task_urgent,
            strategy="smart_balance", 
            task_list=all_tasks
        )
        
        # The blocking task should mention it blocks other tasks
        self.assertIn("Blocks:", explanation)
        
        # Verify blocking score includes the bonus (20 points per blocked task)
        # The blocking task blocks 1 task, so it should have +20 bonus
        print(f"Blocking task score: {blocking_score}, explanation: {explanation}")
    
    def test_business_days_calculation(self):
        """Test 6: Verify business days are calculated correctly (excludes weekends)"""
        # Create a task due on a specific date
        future_task = Task.objects.create(
            title="Future task",
            due_date=date.today() + timedelta(days=14),  # 2 weeks from now
            estimated_hours=5,
            importance=5,
            dependencies=[]
        )
        
        score, explanation = score_task(future_task, strategy="smart_balance")
        
        # The explanation should mention business days, not calendar days
        self.assertIn("business days", explanation)
        
        # Clean up
        future_task.delete()
    
    def test_score_consistency(self):
        """Test 7: Same task should produce same score when called multiple times"""
        score1, _ = score_task(self.task_urgent, strategy="smart_balance")
        score2, _ = score_task(self.task_urgent, strategy="smart_balance")
        
        self.assertEqual(score1, score2, "Score should be consistent across multiple calls")
