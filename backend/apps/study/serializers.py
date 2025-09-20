"""
Serializers for study app
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, DailySchedule, TaskAssignment


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    
    due_datetime = serializers.DateTimeField(read_only=True)
    time_remaining = serializers.DurationField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'user', 'T_n', 'completed_so_far',
            'delta', 'due_date', 'due_time', 'is_completed', 'created_at',
            'updated_at', 'due_datetime', 'time_remaining', 'is_overdue',
            'days_until_due'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'is_completed']


class TaskAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for TaskAssignment model"""
    
    task = TaskSerializer(read_only=True)
    task_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = TaskAssignment
        fields = [
            'id', 'task', 'task_id', 'time_allotted', 'start_time',
            'end_time', 'completed_time', 'is_completed'
        ]


class DailyScheduleSerializer(serializers.ModelSerializer):
    """Serializer for DailySchedule model"""
    
    task_assignments = TaskAssignmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = DailySchedule
        fields = [
            'id', 'date', 'user', 'created_at', 'updated_at',
            'task_assignments'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class DailyPlanSerializer(serializers.Serializer):
    """Serializer for daily plan generation"""
    date = serializers.DateField()
    free_time_available = serializers.DurationField()
    tasks_scheduled = serializers.IntegerField()
    total_time_allocated = serializers.DurationField()
    plan_efficiency = serializers.FloatField(required=False)
    task_assignments = TaskAssignmentSerializer(many=True)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
