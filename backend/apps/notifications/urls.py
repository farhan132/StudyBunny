from django.urls import path
from . import views

urlpatterns = [
    # Notification management
    path('', views.get_notifications, name='get-notifications'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('clear-all/', views.clear_all_notifications, name='clear-all-notifications'),
    
    # Settings
    path('settings/', views.notification_settings, name='notification-settings'),
    
    # Development/testing
    path('generate-test/', views.generate_test_notifications, name='generate-test-notifications'),
]
