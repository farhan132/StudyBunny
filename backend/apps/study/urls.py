from django.urls import path
from . import views

urlpatterns = [
    # Task management endpoints
    path('tasks/', views.list_user_tasks, name='list-user-tasks'),
    path('tasks/create/', views.create_task, name='create-task'),
    path('tasks/update-by-name/', views.update_task_by_name_api, name='update-task-by-name'),
    path('tasks/get-by-name/', views.get_task_by_name_api, name='get-task-by-name'),
]