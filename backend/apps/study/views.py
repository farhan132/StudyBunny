from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from datetime import date, timedelta
from .models import Task, DailySchedule, TaskAssignment
from .serializers import (
    TaskSerializer, DailyScheduleSerializer, TaskAssignmentSerializer,
    DailyPlanSerializer, UserSerializer
)
from apps.core.time_utils import TaskScheduler, TimeManager


class TaskListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating tasks"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting tasks"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class DailyScheduleListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating daily schedules"""
    serializer_class = DailyScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DailySchedule.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DailyScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting daily schedules"""
    serializer_class = DailyScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DailySchedule.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_daily_plan(request):
    """Generate daily task plan for the authenticated user"""
    target_date = request.data.get('date')
    
    if target_date:
        try:
            target_date = date.fromisoformat(target_date)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        target_date = None
    
    # Generate the daily plan using the skeleton function
    daily_plan = TaskScheduler.generate_daily_plan(request.user, target_date)
    
    # Get free time for the day
    free_time = TimeManager.calculate_free_d(target_date or timezone.now().date())
    
    # Calculate total time allocated
    total_time_allocated = sum(
        assignment['time_allotted'] for assignment in daily_plan
    )
    
    response_data = {
        'date': target_date or timezone.now().date(),
        'free_time_available': free_time,
        'tasks_scheduled': len(daily_plan),
        'total_time_allocated': total_time_allocated,
        'plan_efficiency': (total_time_allocated.total_seconds() / free_time.total_seconds() * 100) if free_time.total_seconds() > 0 else 0,
        'task_assignments': daily_plan
    }
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_tasks(request):
    """Get all tasks for the authenticated user with filtering options"""
    queryset = Task.objects.filter(user=request.user)
    
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
    
    serializer = TaskSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_task_progress(request, task_id):
    """Update task completion progress"""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        return Response(
            {'error': 'Task not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    completed_so_far = request.data.get('completed_so_far')
    
    if completed_so_far is None:
        return Response(
            {'error': 'completed_so_far is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        completed_so_far = float(completed_so_far)
        if not 0 <= completed_so_far <= 100:
            return Response(
                {'error': 'completed_so_far must be between 0 and 100'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except (ValueError, TypeError):
        return Response(
            {'error': 'completed_so_far must be a number'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    task.completed_so_far = completed_so_far
    task.save()
    
    serializer = TaskSerializer(task)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_task_statistics(request):
    """Get task statistics for the authenticated user"""
    user_tasks = Task.objects.filter(user=request.user)
    
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(is_completed=True).count()
    overdue_tasks = user_tasks.filter(
        is_completed=False,
        due_date__lt=timezone.now().date()
    ).count()
    
    # Calculate average completion percentage
    avg_completion = user_tasks.aggregate(
        avg_completion=models.Avg('completed_so_far')
    )['avg_completion'] or 0
    
    # Priority distribution
    priority_distribution = {}
    for priority, _ in Task.PRIORITY_CHOICES:
        count = user_tasks.filter(delta=priority).count()
        priority_distribution[f'priority_{priority}'] = count
    
    return Response({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        'average_completion_percentage': avg_completion,
        'priority_distribution': priority_distribution
    })
