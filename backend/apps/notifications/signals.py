"""
Django signals for automatic notification generation
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from apps.study.models import Task
from .services import NotificationService


@receiver(post_save, sender=Task)
def task_completion_notification(sender, instance, created, **kwargs):
    """Generate notification when a task is completed"""
    if not created and instance.is_completed:
        # Check if this is a new completion (not just an update)
        if hasattr(instance, '_previous_completion_status'):
            if not instance._previous_completion_status and instance.is_completed:
                # Task was just completed
                NotificationService.notify_task_completed(instance.user, instance)


@receiver(pre_save, sender=Task)
def track_task_completion_changes(sender, instance, **kwargs):
    """Track changes in task completion status"""
    if instance.pk:
        try:
            previous = Task.objects.get(pk=instance.pk)
            instance._previous_completion_status = previous.is_completed
        except Task.DoesNotExist:
            instance._previous_completion_status = False
    else:
        instance._previous_completion_status = False
