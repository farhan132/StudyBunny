"""
Notification service for generating and managing notifications
"""
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime, date

from .models import Notification, NotificationSettings, NotificationTemplate
from apps.study.models import Task


class NotificationService:
    """Service for managing notifications"""
    
    @staticmethod
    def get_user_settings(user):
        """Get notification settings for user"""
        settings, created = NotificationSettings.objects.get_or_create(user=user)
        return settings
    
    @staticmethod
    def create_notification(user, notification_type, title, message, icon='🔔', task_id=None):
        """Create a new notification"""
        return Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            icon=icon,
            related_task_id=task_id
        )
    
    @staticmethod
    def notify_task_completed(user, task):
        """Notify when a task is completed"""
        settings = NotificationService.get_user_settings(user)
        if not settings.goal_achievements:
            return None
            
        return NotificationService.create_notification(
            user=user,
            notification_type='success',
            title='Task Completed! 🎉',
            message=f'Great job! You completed "{task.title}".',
            icon='✅',
            task_id=task.id
        )
    
    @staticmethod
    def notify_task_due_soon(user, task, days_until_due):
        """Notify when a task is due soon"""
        settings = NotificationService.get_user_settings(user)
        if not settings.study_reminders:
            return None
            
        if days_until_due == 0:
            title = 'Task Due Today! 🔥'
            message = f'"{task.title}" is due today. Don\'t forget to complete it!'
            icon = '🚨'
        elif days_until_due == 1:
            title = 'Task Due Tomorrow ⏰'
            message = f'"{task.title}" is due tomorrow. Better start working on it!'
            icon = '⏰'
        else:
            title = f'Task Due in {days_until_due} Days 📅'
            message = f'"{task.title}" is due in {days_until_due} days. Plan your time accordingly.'
            icon = '📅'
            
        return NotificationService.create_notification(
            user=user,
            notification_type='reminder',
            title=title,
            message=message,
            icon=icon,
            task_id=task.id
        )
    
    @staticmethod
    def notify_study_streak(user, streak_days):
        """Notify about study streaks"""
        settings = NotificationService.get_user_settings(user)
        if not settings.motivation_messages:
            return None
            
        if streak_days >= 7:
            title = 'Amazing Streak! 🔥'
            message = f'Incredible! You\'ve maintained a {streak_days}-day study streak!'
            icon = '🔥'
        elif streak_days >= 3:
            title = 'Great Streak! ⚡'
            message = f'Keep it up! You\'re on a {streak_days}-day study streak.'
            icon = '⚡'
        else:
            return None
            
        return NotificationService.create_notification(
            user=user,
            notification_type='achievement',
            title=title,
            message=message,
            icon=icon
        )
    
    @staticmethod
    def notify_daily_progress(user, completed_today, total_today):
        """Notify about daily progress"""
        settings = NotificationService.get_user_settings(user)
        if not settings.progress_reports:
            return None
            
        if completed_today == 0:
            return None
            
        completion_rate = (completed_today / total_today * 100) if total_today > 0 else 0
        
        if completion_rate >= 100:
            title = 'Perfect Day! 🌟'
            message = f'Outstanding! You completed all {completed_today} tasks scheduled for today.'
            icon = '🌟'
        elif completion_rate >= 75:
            title = 'Excellent Progress! 💪'
            message = f'Great work! You completed {completed_today} out of {total_today} tasks today.'
            icon = '💪'
        elif completion_rate >= 50:
            title = 'Good Progress 👍'
            message = f'Nice job! You completed {completed_today} out of {total_today} tasks today.'
            icon = '👍'
        else:
            return None
            
        return NotificationService.create_notification(
            user=user,
            notification_type='info',
            title=title,
            message=message,
            icon=icon
        )
    
    @staticmethod
    def notify_break_reminder(user):
        """Notify about taking breaks"""
        settings = NotificationService.get_user_settings(user)
        if not settings.break_alerts:
            return None
            
        return NotificationService.create_notification(
            user=user,
            notification_type='reminder',
            title='Break Time! 🧘',
            message='You\'ve been studying for a while. Take a 10-15 minute break to recharge!',
            icon='☕'
        )
    
    @staticmethod
    def check_and_generate_notifications(user):
        """Check tasks and generate relevant notifications"""
        notifications_created = []
        
        # Get user's incomplete tasks
        tasks = Task.objects.filter(user=user, is_completed=False)
        today = date.today()
        
        for task in tasks:
            if task.due_date:
                days_until_due = (task.due_date - today).days
                
                # Check if we should notify about due dates
                if days_until_due <= 3 and days_until_due >= 0:
                    # Check if we already sent this notification recently
                    recent_notification = Notification.objects.filter(
                        user=user,
                        related_task_id=task.id,
                        type='reminder',
                        created_at__gte=timezone.now() - timedelta(hours=24)
                    ).exists()
                    
                    if not recent_notification:
                        notif = NotificationService.notify_task_due_soon(user, task, days_until_due)
                        if notif:
                            notifications_created.append(notif)
        
        # Check for achievements and streaks
        completed_tasks = Task.objects.filter(user=user, is_completed=True)
        if completed_tasks.exists():
            # Calculate streak
            streak = 0
            current_date = today
            while True:
                day_completed = completed_tasks.filter(updated_at__date=current_date).exists()
                if day_completed:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            # Notify about streaks (but not too frequently)
            if streak >= 3:
                recent_streak_notification = Notification.objects.filter(
                    user=user,
                    type='achievement',
                    title__icontains='streak',
                    created_at__gte=timezone.now() - timedelta(days=1)
                ).exists()
                
                if not recent_streak_notification:
                    notif = NotificationService.notify_study_streak(user, streak)
                    if notif:
                        notifications_created.append(notif)
        
        return notifications_created
