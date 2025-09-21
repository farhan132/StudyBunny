"""
URL configuration for study_bunny project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/study/', include('apps.study.urls')),
    path('api/core/', include('apps.core.urls')),
    # Voice agent temporarily disabled due to Python 3.13 compatibility issues
    # path('api/voice/', include('voice_agent.urls')),
]
