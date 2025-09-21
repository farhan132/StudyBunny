from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from datetime import date, timedelta
from .models import Task, DailySchedule, TaskAssignment
from .task_utils import update_task_by_name, get_task_by_name, generate_daily_plan, get_14_day_schedule as generate_14_day_schedule
from django.contrib.auth import get_user_model
from apps.core.intensity import get_intensity, set_intensity

User = get_user_model()


@api_view(['PATCH'])
@permission_classes([permissions.AllowAny])
def update_task_by_name_api(request):
    """
    Update a task by its name with partial parameters
    
    Body parameters:
    - task_name (str): Name of the task to update
    - title (str, optional): New title
    - description (str, optional): New description
    - T_n (str, optional): Expected time needed (HH:MM:SS format)
    - completed_so_far (float, optional): Completion percentage (0-100)
    - delta (int, optional): Priority level (1-5)
    - due_date (str, optional): Due date (YYYY-MM-DD format)
    - due_time (str, optional): Due time (HH:MM:SS format)
    """
    task_name = request.data.get('task_name')
    
    if not task_name:
        return Response(
            {'error': 'task_name is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Extract update parameters (exclude task_name)
    update_params = {k: v for k, v in request.data.items() if k != 'task_name'}
    
    # Call the utility function
    result = update_task_by_name(request.user, task_name, **update_params)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_task_by_name_api(request):
    """
    Get a task by its name
    
    Query parameters:
    - task_name (str): Name of the task to retrieve
    """
    task_name = request.query_params.get('task_name')
    
    if not task_name:
        return Response(
            {'error': 'task_name query parameter is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Call the utility function
    result = get_task_by_name(request.user, task_name)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def list_user_tasks(request):
    """
    List all tasks for the authenticated user with optional filtering
    """
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
    )
    queryset = Task.objects.filter(user=user)
    
    # Filter by completion status
    is_completed = request.query_params.get('is_completed')
    if is_completed is not None:
        queryset = queryset.filter(is_completed=is_completed.lower() == 'true')
    
    # Filter by priority
    priority = request.query_params.get('priority')
    if priority is not None:
        try:
            priority = int(priority)
            queryset = queryset.filter(delta=priority)
        except ValueError:
            return Response(
                {'error': 'Invalid priority value'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Filter by due date range
    due_after = request.query_params.get('due_after')
    due_before = request.query_params.get('due_before')
    
    if due_after:
        try:
            due_after = date.fromisoformat(due_after)
            queryset = queryset.filter(due_date__gte=due_after)
        except ValueError:
            return Response(
                {'error': 'Invalid due_after date format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if due_before:
        try:
            due_before = date.fromisoformat(due_before)
            queryset = queryset.filter(due_date__lte=due_before)
        except ValueError:
            return Response(
                {'error': 'Invalid due_before date format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Order by due date and priority
    queryset = queryset.order_by('due_date', '-delta')
    
    # Convert to list of dictionaries
    tasks = []
    for task in queryset:
        tasks.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'T_n': str(task.T_n),
            'completed_so_far': task.completed_so_far,
            'delta': task.delta,
            'due_date': task.due_date.isoformat(),
            'due_time': task.due_time.isoformat(),
            'is_completed': task.is_completed,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        })
    
    return Response({
        'success': True,
        'tasks': tasks,
        'count': len(tasks)
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_task(request):
    """
    Create a new task
    
    Required fields:
    - title (str): Task title
    - T_n (str): Expected time needed (HH:MM:SS format)
    - delta (int): Priority level (1-5)
    - due_date (str): Due date (YYYY-MM-DD format)
    - due_time (str): Due time (HH:MM:SS format)
    
    Optional fields:
    - description (str): Task description
    - completed_so_far (float): Initial completion percentage (default: 0.0)
    """
    required_fields = ['title', 'T_n', 'delta', 'due_date', 'due_time']
    
    for field in required_fields:
        if field not in request.data:
            return Response(
                {'error': f'{field} is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        # Parse T_n duration
        time_parts = request.data['T_n'].split(':')
        if len(time_parts) != 3:
            return Response(
                {'error': 'T_n must be in HH:MM:SS format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        hours, minutes, seconds = map(int, time_parts)
        T_n = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        
        # Parse due_date
        due_date = date.fromisoformat(request.data['due_date'])
        
        # Parse due_time
        due_time = timezone.datetime.strptime(request.data['due_time'], '%H:%M:%S').time()
        
        # Validate delta
        delta = int(request.data['delta'])
        if not 1 <= delta <= 5:
            return Response(
                {'error': 'delta must be between 1 and 5'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create demo user
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        # Create the task
        task = Task.objects.create(
            user=user,
            title=request.data['title'],
            description=request.data.get('description', ''),
            T_n=T_n,
            completed_so_far=float(request.data.get('completed_so_far', 0.0)),
            delta=delta,
            due_date=due_date,
            due_time=due_time
        )
        
        return Response({
            'success': True,
            'message': 'Task created successfully',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'T_n': str(task.T_n),
                'completed_so_far': task.completed_so_far,
                'delta': task.delta,
                'due_date': task.due_date.isoformat(),
                'due_time': task.due_time.isoformat(),
                'is_completed': task.is_completed,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
        
    except (ValueError, TypeError) as e:
        return Response(
            {'error': f'Invalid data format: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred while creating task: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def list_daily_schedules(request):
    """List daily schedules for the user"""
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
    )
    
    schedules = DailySchedule.objects.filter(user=user).order_by('-date')
    schedules_data = []
    
    for schedule in schedules:
        schedules_data.append({
            'id': schedule.id,
            'date': schedule.date.isoformat(),
            'created_at': schedule.created_at.isoformat(),
            'updated_at': schedule.updated_at.isoformat()
        })
    
    return Response({
        'success': True,
        'schedules': schedules_data,
        'count': len(schedules_data)
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_daily_schedule(request):
    """Create a new daily schedule"""
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
    )
    
    try:
        schedule_date = date.fromisoformat(request.data.get('date', timezone.now().date().isoformat()))
        
        schedule = DailySchedule.objects.create(
            user=user,
            date=schedule_date
        )
        
        return Response({
            'success': True,
            'schedule': {
                'id': schedule.id,
                'date': schedule.date.isoformat(),
                'created_at': schedule.created_at.isoformat(),
                'updated_at': schedule.updated_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Error creating schedule: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_daily_schedule(request, pk):
    """Get a specific daily schedule"""
    try:
        schedule = DailySchedule.objects.get(pk=pk)
        return Response({
            'success': True,
            'schedule': {
                'id': schedule.id,
                'date': schedule.date.isoformat(),
                'created_at': schedule.created_at.isoformat(),
                'updated_at': schedule.updated_at.isoformat()
            }
        })
    except DailySchedule.DoesNotExist:
        return Response(
            {'error': 'Schedule not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def generate_daily_plan(request):
    """Generate daily task plan"""
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
    )
    
    try:
        target_date = date.fromisoformat(request.data.get('date', timezone.now().date().isoformat()))
        intensity = get_intensity()
        
        plan = generate_daily_plan(user, target_date, intensity)
        
        return Response({
            'success': True,
            'plan': plan,
            'date': target_date.isoformat(),
            'intensity': intensity
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error generating plan: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_14_day_schedule(request):
    """Get 14-day schedule"""
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
    )
    
    try:
        start_date = request.query_params.get('start_date')
        if start_date:
            start_date = date.fromisoformat(start_date)
        else:
            # Let the function handle timezone-aware default start date
            start_date = None
        
        schedule_result = generate_14_day_schedule(user, start_date)
        
        return Response(schedule_result)
        
    except Exception as e:
        return Response(
            {'error': f'Error generating 14-day schedule: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_statistics(request):
    """Get task statistics"""
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
    )
    
    try:
        # Get all tasks
        all_tasks = Task.objects.filter(user=user)
        completed_tasks = all_tasks.filter(is_completed=True)
        
        # Calculate statistics
        total_tasks = all_tasks.count()
        completed_count = completed_tasks.count()
        completion_rate = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate total study hours
        total_hours = 0
        for task in all_tasks:
            hours = task.T_n.total_seconds() / 3600
            total_hours += hours
        
        # Get intensity-based score
        intensity = get_intensity()
        intensity_score = int(intensity * 100)  # Convert to 0-100 scale
        
        # Calculate assignments done today
        today = timezone.now().date()
        today_completed = completed_tasks.filter(updated_at__date=today).count()
        
        return Response({
            'success': True,
            'statistics': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_count,
                'completion_rate': round(completion_rate, 1),
                'total_study_hours': round(total_hours, 1),
                'intensity_score': intensity_score,
                'assignments_done_today': today_completed,
                'current_intensity': intensity
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error getting statistics: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )