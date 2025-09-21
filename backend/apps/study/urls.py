from django.urls import path
from . import views

urlpatterns = [
    # Task management endpoints
    path('tasks/', views.list_user_tasks, name='list-user-tasks'),
    path('tasks/create/', views.create_task, name='create-task'),
    path('tasks/update-by-name/', views.update_task_by_name_api, name='update-task-by-name'),
    path('tasks/get-by-name/', views.get_task_by_name_api, name='get-task-by-name'),
    path('tasks/<int:task_id>/progress/', views.update_task_progress_api, name='update-task-progress'),
    path('test-free-time/', views.test_free_time, name='test-free-time'),
    
    # Daily schedule endpoints
    path('daily-schedules/', views.list_daily_schedules, name='list-daily-schedules'),
    path('daily-schedules/create/', views.create_daily_schedule, name='create-daily-schedule'),
    path('daily-schedules/<int:pk>/', views.get_daily_schedule, name='get-daily-schedule'),
    
    # Planning endpoints
    path('generate-daily-plan/', views.generate_daily_plan, name='generate-daily-plan'),
    path('get-14-day-schedule/', views.get_14_day_schedule, name='get-14-day-schedule'),
    
    # Statistics endpoints
    path('statistics/', views.get_statistics, name='get-statistics'),
    
    # Dashboard endpoints
    path('dashboard-stats/', views.get_dashboard_stats, name='get-dashboard-stats'),
    
    # Canvas integration endpoints
    path('canvas/sync/', views.sync_canvas_tasks, name='sync-canvas-tasks'),
    path('canvas/courses/', views.get_canvas_courses, name='get-canvas-courses'),
    path('canvas/assignments/', views.get_canvas_assignments, name='get-canvas-assignments'),
    path('canvas/config/', views.get_canvas_config, name='get-canvas-config'),
    path('canvas/set-token/', views.set_canvas_token, name='set-canvas-token'),
]