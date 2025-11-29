from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.task_list, name='task_list'),
    path('suggest/', views.suggest_tasks, name='suggest_tasks'),
]