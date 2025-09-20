from django.urls import path
from . import views

urlpatterns = [
    # Task CRUD
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/user/', views.get_user_tasks, name='get-user-tasks'),
    path('tasks/<int:task_id>/progress/', views.update_task_progress, name='update-task-progress'),
    path('tasks/statistics/', views.get_task_statistics, name='get-task-statistics'),
    
    # Daily schedule CRUD
    path('daily-schedules/', views.DailyScheduleListCreateView.as_view(), name='daily-schedule-list'),
    path('daily-schedules/<int:pk>/', views.DailyScheduleDetailView.as_view(), name='daily-schedule-detail'),
    
    # Planning endpoints
    path('generate-daily-plan/', views.generate_daily_plan, name='generate-daily-plan'),
]
