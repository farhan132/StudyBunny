from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

# Create your models here.

class Task(models.Model):
    """Model representing a task with time tracking and priority"""
    
    PRIORITY_CHOICES = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Medium'),
        (4, 'High'),
        (5, 'Very High'),
    ]
    
    # Basic task information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    
    # Time tracking
    T_n = models.DurationField(
        help_text="Expected time needed to complete the task (hr/min/sec)"
    )
    completed_so_far = models.FloatField(
        default=0.0,
        help_text="Completion percentage (0-100%)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Priority and scheduling
    delta = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=3,
        help_text="Priority for the task"
    )
    due_date = models.DateField(help_text="Due date for the task")
    due_time = models.TimeField(help_text="Due time for the task")
    
    # Status tracking
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date', 'due_time', '-delta']
    
    def __str__(self):
        return f"{self.title} ({self.completed_so_far}%)"
    
    def save(self, *args, **kwargs):
        # Auto-complete task if 100% done
        if self.completed_so_far >= 100.0:
            self.is_completed = True
        else:
            self.is_completed = False
        super().save(*args, **kwargs)
    
    @property
    def due_datetime(self):
        """Return the full due datetime"""
        return timezone.make_aware(
            datetime.combine(self.due_date, self.due_time)
        )
    
    @property
    def time_remaining(self):
        """Calculate time remaining based on completion percentage"""
        if self.completed_so_far >= 100.0:
            return timedelta(0)
        
        remaining_percentage = (100.0 - self.completed_so_far) / 100.0
        return self.T_n * remaining_percentage
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        return not self.is_completed and self.due_datetime < timezone.now()
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        today = timezone.now().date()
        return (self.due_date - today).days


class DailySchedule(models.Model):
    """Model to store daily task scheduling"""
    
    date = models.DateField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Schedule for {self.date}"
    
    @classmethod
    def generate_daily_plan(cls, user, target_date=None):
        """
        Generate daily task plan for a user
        This is a skeleton function - implement your scheduling logic here
        
        Args:
            user: User instance
            target_date: Date to generate plan for (defaults to today)
        
        Returns:
            List of dictionaries with task assignments for the day
            Format: [{'task': Task, 'time_allotted': timedelta, 'start_time': time}, ...]
        """
        if target_date is None:
            target_date = timezone.now().date()
        
        # TODO: Implement your task scheduling algorithm here
        # This should consider:
        # - Available free time for the day
        # - Task priorities (delta)
        # - Due dates
        # - Task completion percentages
        # - Time needed (T_n)
        
        # Get all incomplete tasks for the user
        incomplete_tasks = Task.objects.filter(
            user=user,
            is_completed=False
        ).order_by('due_date', '-delta')
        
        # Placeholder implementation
        daily_plan = []
        for task in incomplete_tasks[:5]:  # Limit to 5 tasks for now
            daily_plan.append({
                'task': task,
                'time_allotted': task.T_n * 0.2,  # 20% of task time per day
                'start_time': timezone.now().time(),
            })
        
        return daily_plan


class TaskAssignment(models.Model):
    """Model to store specific task assignments for a day"""
    
    daily_schedule = models.ForeignKey(
        DailySchedule, 
        on_delete=models.CASCADE, 
        related_name='task_assignments'
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    time_allotted = models.DurationField(help_text="Time allocated for this task today")
    start_time = models.TimeField(help_text="Scheduled start time")
    end_time = models.TimeField(help_text="Scheduled end time")
    completed_time = models.DurationField(
        null=True, 
        blank=True, 
        help_text="Actual time spent on task"
    )
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.task.title} at {self.start_time}"
    
    def save(self, *args, **kwargs):
        # Calculate end time based on start time and allotted time
        if not self.end_time:
            start_datetime = datetime.combine(self.daily_schedule.date, self.start_time)
            end_datetime = start_datetime + self.time_allotted
            self.end_time = end_datetime.time()
        super().save(*args, **kwargs)
