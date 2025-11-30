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
    except Exception as e:
       return JsonResponse({"error": str(e)}, status=400)
    
    strategy=request.GET.get('strategy','smart_balance')
    created_tasks = []
    for task in tasks:
            try:
                if task['title']=='' or 'title' not in task:
                    return JsonResponse({'error': 'Title is required field.'}, status=400)
                
                due_date=datetime.strptime(task["due_date"], "%Y-%m-%d").date()
                title=task["title"]
                estimated_hours=int(task["estimated_hours"])
                importance=int(task["importance"])
                dependencies=task.get("dependencies",[])

                if title in [t.title for t in Task.objects.all()]:
                    if Task.objects.filter(importance=importance,due_date=due_date,estimated_hours=estimated_hours,strategy=strategy).exists():
                        return JsonResponse({'error': f'Task with title "{title}" and same parameters already exists.'}, status=400)

                # Assumed multiple tasks can have same title, so not checking for existing titles
                # Also when strategy is changed, it creates new tasks instead of updating existing ones.
                temp_task = Task(
                    title=title,
                    due_date=due_date,
                    estimated_hours=estimated_hours,
                    importance=importance,
                    dependencies=dependencies
                )

                score, explanation = score_task(temp_task, strategy=strategy, task_list=tasks)
                temp_task.score = score
                temp_task.explanation = explanation
                temp_task.strategy = strategy
                temp_task.save()

                created_tasks.append({
                    'id': temp_task.id,
                    'title': title,
                    'due_date': str(due_date),
                    'estimated_hours': estimated_hours,
                    'importance': importance,
                    'dependencies': dependencies,
                    'score': float(score),
                    'explanation': explanation or "",
                })
            
            except Exception as e:
                 return JsonResponse({"error": str(e)}, status=400)

    #Return tasks as sorted list based on score
    sorted_tasks = sorted(created_tasks, key=lambda t: t['score'], reverse=True)
    return JsonResponse({'tasks': sorted_tasks},safe=False)   
        
@csrf_exempt
def suggest_tasks(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    
    # Get today's date
    from datetime import date
    today = date.today()
    tasks=[]
    based_on=""
    # Filter tasks that are due today or overdue
    tasks = Task.objects.filter(due_date__lte=today)
    if not tasks.exists():
        # Fallback logic when no tasks are due today
        if Task.objects.filter(importance__gt=5).exists():
            tasks = Task.objects.filter(importance__gt=5)
            based_on="importance"
        elif Task.objects.exclude(dependencies=[]).exists():
            tasks = Task.objects.exclude(dependencies=[])
            based_on="dependencies"
        elif Task.objects.filter(estimated_hours__lt=5).exists():
            tasks = Task.objects.filter(estimated_hours__lt=5)
            based_on="estimated_hours"
        else:
            tasks = Task.objects.all()
            based_on="all"

    if not tasks:
        return JsonResponse({'error':'No tasks to suggest'},status=400)


    if based_on=="":
        based_on="due_date_today"
    suggestions = []
    for task in tasks:
        # Recalculate score based on the selected strategy
        suggestions.append({
                'id': task.id,
                'title': task.title,
                'due_date': task.due_date,
                'estimated_hours': task.estimated_hours,
                'importance': task.importance,
                'dependencies': task.dependencies,
                'score': task.score,
                'explanation': task.explanation,
                'strategy': task.strategy,
                'based_on': based_on
            })
    top3_suggestions = sorted(suggestions, key=lambda x: x['score'],reverse=True)[:3]
    return JsonResponse({'suggestions': top3_suggestions})

    
    
