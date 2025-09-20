"""
Serializers for core app
"""
from rest_framework import serializers
from .models import TimeCalculation


class TimeCalculationSerializer(serializers.ModelSerializer):
    """Serializer for TimeCalculation model"""
    
    class Meta:
        model = TimeCalculation
        fields = ['id', 'date', 'time_today', 'free_today', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TimeAnalysisSerializer(serializers.Serializer):
    """Serializer for time analysis data"""
    date = serializers.DateField()
    time_today = serializers.DurationField()
    free_today = serializers.DurationField()
    time_d = serializers.DurationField()
    free_d = serializers.DurationField()
    efficiency_score = serializers.FloatField(required=False)
