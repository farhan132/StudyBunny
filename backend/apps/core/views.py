from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import date, timedelta
from .models import TimeCalculation
from .serializers import TimeCalculationSerializer, TimeAnalysisSerializer
from .time_utils import TimeManager, TaskScheduler, TimeAnalytics
from .intensity import get_intensity, set_intensity


class TimeCalculationListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating time calculations"""
    queryset = TimeCalculation.objects.all()
    serializer_class = TimeCalculationSerializer


class TimeCalculationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting time calculations"""
    queryset = TimeCalculation.objects.all()
    serializer_class = TimeCalculationSerializer


@api_view(['GET'])
def get_time_today(request):
    """Get time remaining until midnight for today"""
    target_date = request.query_params.get('date')
    if target_date:
        try:
            target_date = date.fromisoformat(target_date)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        target_date = None
    
    time_today = TimeManager.get_time_today(target_date)
    
    return Response({
        'date': target_date or timezone.now().date(),
        'time_today': time_today,
        'time_today_hours': time_today.total_seconds() / 3600
    })


@api_view(['GET'])
def get_free_time_today(request):
    """Get free time available today"""
    target_date = request.query_params.get('date')
    if target_date:
        try:
            target_date = date.fromisoformat(target_date)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        target_date = None
    
    free_today = TimeManager.calculate_free_today(target_date)
    time_today = TimeManager.get_time_today(target_date)
    
    return Response({
        'date': target_date or timezone.now().date(),
        'time_today': time_today,
        'free_today': free_today,
        'free_today_hours': free_today.total_seconds() / 3600,
        'utilization_percentage': (free_today.total_seconds() / time_today.total_seconds() * 100) if time_today.total_seconds() > 0 else 0
    })


@api_view(['GET'])
def get_time_analysis(request):
    """Get comprehensive time analysis for a date range"""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date or not end_date:
        return Response(
            {'error': 'Both start_date and end_date are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    analysis = TimeAnalytics.get_time_analysis(request.user, start_date, end_date)
    
    return Response(analysis)


@api_view(['GET'])
def get_intensity_value(request):
    """Get current intensity value"""
    return Response({
        'intensity': get_intensity(),
        'description': 'Global intensity value (0.0 = low, 1.0 = high)'
    })


@api_view(['POST'])
def set_intensity_value(request):
    """Set intensity value"""
    intensity = request.data.get('intensity')
    
    if intensity is None:
        return Response(
            {'error': 'intensity value is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        intensity = float(intensity)
        if not 0.0 <= intensity <= 1.0:
            return Response(
                {'error': 'intensity must be between 0.0 and 1.0'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        set_intensity(intensity)
        return Response({
            'intensity': get_intensity(),
            'message': 'Intensity updated successfully'
        })
        
    except (ValueError, TypeError):
        return Response(
            {'error': 'intensity must be a number'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
