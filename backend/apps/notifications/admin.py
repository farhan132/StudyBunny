from django.contrib import admin
from .models import Notification, NotificationSettings, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'study_reminders', 'break_alerts', 'goal_achievements', 'updated_at']
    list_filter = ['study_reminders', 'break_alerts', 'goal_achievements']
    search_fields = ['user__username']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_active', 'created_at']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'title_template']
