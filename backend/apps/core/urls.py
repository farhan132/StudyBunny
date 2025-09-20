from django.urls import path
from . import views

urlpatterns = [
    # Time calculation CRUD
    path('time-calculations/', views.TimeCalculationListCreateView.as_view(), name='time-calculation-list'),
    path('time-calculations/<int:pk>/', views.TimeCalculationDetailView.as_view(), name='time-calculation-detail'),
    
    # Time utility endpoints
    path('time-today/', views.get_time_today, name='get-time-today'),
    path('free-time-today/', views.get_free_time_today, name='get-free-time-today'),
    path('time-analysis/', views.get_time_analysis, name='get-time-analysis'),
    
    # Intensity endpoints
    path('intensity/', views.get_intensity_value, name='get-intensity'),
    path('intensity/set/', views.set_intensity_value, name='set-intensity'),
]
