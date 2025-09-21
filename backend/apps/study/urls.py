from django.urls import path
from . import views

urlpatterns = [
    # Task management endpoints
    path('tasks/', views.list_user_tasks, name='list-user-tasks'),
    path('tasks/create/', views.create_task, name='create-task'),
    path('tasks/update-by-name/', views.update_task_by_name_api, name='update-task-by-name'),
    path('tasks/get-by-name/', views.get_task_by_name_api, name='get-task-by-name'),
    
    # Daily schedule endpoints
    path('daily-schedules/', views.list_daily_schedules, name='list-daily-schedules'),
    path('daily-schedules/create/', views.create_daily_schedule, name='create-daily-schedule'),
    path('daily-schedules/<int:pk>/', views.get_daily_schedule, name='get-daily-schedule'),
    
    # Planning endpoints
    path('generate-daily-plan/', views.generate_daily_plan, name='generate-daily-plan'),
    path('get-14-day-schedule/', views.get_14_day_schedule, name='get-14-day-schedule'),
    
    # Statistics endpoints
    path('statistics/', views.get_statistics, name='get-statistics'),
]