from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class Task(models.Model):
    title=models.CharField(max_length=200)
    due_date=models.DateField()
    estimated_hours=models.IntegerField(default=1)
    # Importance on a scale from 1 (least important) to 10 (most important)
    importance=models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    dependencies=models.JSONField(default=list, blank=True)
    
    score=models.FloatField(null=True, blank=True)
    explanation=models.TextField(null=True, blank=True)
    strategy=models.CharField(max_length=50, default='smart_balance')
    def __str__(self):
        return self.title
