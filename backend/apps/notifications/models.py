from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class NotificationSettings(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    study_reminders = models.BooleanField(default=True)
    break_alerts = models.BooleanField(default=True)
    progress_reports = models.BooleanField(default=False)
    goal_achievements = models.BooleanField(default=True)
    motivation_messages = models.BooleanField(default=True)
    sound_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification settings for {self.user.username}"


class Notification(models.Model):
    """Individual notifications for users"""
    
    NOTIFICATION_TYPES = [
        ('success', 'Success'),
        ('reminder', 'Reminder'),
        ('achievement', 'Achievement'),
        ('motivation', 'Motivation'),
        ('warning', 'Warning'),
        ('info', 'Information'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    icon = models.CharField(max_length=10, default='🔔')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional fields for specific notification types
    related_task_id = models.IntegerField(null=True, blank=True)
    action_url = models.URLField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def time_ago(self):
        """Calculate human-readable time since creation"""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()


class NotificationTemplate(models.Model):
    """Templates for generating notifications"""
    
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES)
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    icon = models.CharField(max_length=10, default='🔔')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Template: {self.name}"
    
    def generate_notification(self, user, context=None):
        """Generate a notification from this template"""
        context = context or {}
        
        # Simple template variable replacement
        title = self.title_template
        message = self.message_template
        
        for key, value in context.items():
            title = title.replace(f'{{{key}}}', str(value))
            message = message.replace(f'{{{key}}}', str(value))
        
        return Notification.objects.create(
            user=user,
            type=self.type,
            title=title,
            message=message,
            icon=self.icon,
            related_task_id=context.get('task_id'),
        )
