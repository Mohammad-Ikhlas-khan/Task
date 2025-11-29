from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Task
from .scoring import score_task
from datetime import datetime
# Create your views here.

@csrf_exempt
@csrf_exempt
def task_list(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    try:
        tasks =  json.loads(request.body.decode('utf-8'))
        if not isinstance(tasks, list):
            return JsonResponse({'error': 'Expected a list of tasks.'}, status=400)
        if not tasks:
            return JsonResponse({'error': 'No tasks provided.'}, status=400)
        strategy=request.GET.get('strategy','smart_balance')
        created_tasks = []
        for task in tasks:
                if task['title']=='' or task['due_date']=='' or task['due_date'] is None:
                    return JsonResponse({'error': 'Title and due_date are required fields.'}, status=400)
                
                if task["importance"] <1 or task["importance"]>10:
                    return JsonResponse({'error': 'Importance must be between 1 and 10.'}, status=400)
                
                if task["estimated_hours"] <1:
                    return JsonResponse({'error': 'Estimated hours must be at least 1.'}, status=400)
                
                obj, created = Task.objects.update_or_create(
                    title=task["title"],
                    defaults={
                        'due_date': datetime.strptime(task["due_date"], "%Y-%m-%d").date(),
                        'estimated_hours': task["estimated_hours"],
                        'importance': task["importance"],
                        'dependencies': task.get("dependencies", []),
                    }
                )
                created_tasks.append(obj)
    except Exception as e:
       return JsonResponse({"error": str(e)}, status=400)
    
    for task in created_tasks:
        score, explanation = score_task(task, strategy=strategy, task_list=created_tasks)
        task.score= score 
        task.explanation = explanation
    #Return tasks as sorted list based on score
    sorted_tasks = sorted(created_tasks, key=lambda t: t.score, reverse=True)
    tasks_data = [
        {
            'id': task.id,
            'title': task.title,
            'due_date': str(task.due_date) if task.due_date else None,
            'estimated_hours': task.estimated_hours,
            'importance': task.importance,
            'dependencies': task.dependencies,
            'score': float(task.score) if task.score is not None else 0.0,
            'explanation': task.explanation or "",
        }
        for task in sorted_tasks
    ]
    return JsonResponse({'tasks': tasks_data},safe=False)
    
        
@csrf_exempt
def suggest_tasks(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    
    tasks = Task.objects.all()
    if not tasks.exists():
        return JsonResponse({'error': 'No tasks available to suggest.'}, status=400)
    strategy = request.GET.get('strategy', 'smart_balance')
    suggestions = []
    for task in tasks:
        task_score,explanation= score_task(task, strategy=strategy, task_list=tasks)
        suggestions.append({
                'id': task.id,
                'title': task.title,
                'due_date': task.due_date,
                'estimated_hours': task.estimated_hours,
                'importance': task.importance,
                'dependencies': task.dependencies,
                'score': float(task_score),
                'explanation': explanation,
            })
    top3_suggestions = sorted(suggestions, key=lambda x: x['score'],reverse=True)[:3]
    return JsonResponse({'suggestions': top3_suggestions})

    
    
