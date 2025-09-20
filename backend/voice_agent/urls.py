from django.urls import path
from . import views

urlpatterns = [
    path('command/', views.voice_command_api, name='voice_command_api'),
    path('input/', views.voice_input_api, name='voice_input_api'),
    path('', views.voice_agent_page, name='voice_agent_page'),
]
