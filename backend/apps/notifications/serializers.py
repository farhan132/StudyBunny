from rest_framework import serializers
from .models import Notification, NotificationSettings


class NotificationSerializer(serializers.ModelSerializer):
    time_ago = serializers.ReadOnlyField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'icon', 'is_read', 
            'created_at', 'time_ago', 'related_task_id', 'action_url'
        ]
        read_only_fields = ['created_at', 'time_ago']


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = [
            'study_reminders', 'break_alerts', 'progress_reports',
            'goal_achievements', 'motivation_messages', 'sound_enabled'
        ]
