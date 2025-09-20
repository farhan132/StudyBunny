from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import math

# Create your models here.

def currentTimeInHours():
    """
    Get current time in hours (0-24)
    Returns: float representing current hour of the day
    """
    now = timezone.now()
    return now.hour + now.minute / 60.0 + now.second / 3600.0

def get_intensity():
    """
    Get the current global intensity value
    Returns: float between 0.0 and 1.0
    """
    from django.conf import settings
    return getattr(settings, 'STUDYBUNNY_INTENSITY', 0.7)

class TimeCalculation(models.Model):
    """Model to store time calculations for different dates"""
    date = models.DateField(unique=True)
    time_today = models.DurationField(help_text="Time left until midnight")
    free_today = models.DurationField(help_text="Free time available today")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Time calculation for {self.date}"
    
    @classmethod
    def get_time_today(cls, target_date=None):
        """
        Calculate how much time is left until midnight for a given date
        Returns: timedelta object
        """
        if target_date is None:
            target_date = timezone.now().date()
        
        now = timezone.now()
        midnight = timezone.make_aware(
            datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        )
        
        time_left = midnight - now
        return max(timedelta(0), time_left)  # Don't return negative time
    
    @classmethod
    def get_free_today(cls, target_date=None, intensity_value=None):
        """
        Calculate free time available today
        This is a skeleton function - implement your logic here
        Returns: timedelta object
        
        Args:
            target_date: Date to calculate for (defaults to today)
            intensity_value: Optional intensity value (0.0-1.0). If None, uses global intensity
        """
        # TODO: Implement your free time calculation logic
        # This could involve checking scheduled events, work hours, etc.
        time_today = cls.get_time_today(target_date)
        
        # Use provided intensity or get global intensity
        if intensity_value is not None:
            if not 0.0 <= intensity_value <= 1.0:
                raise ValueError("Intensity value must be between 0.0 and 1.0")
            intensity = intensity_value
        else:
            intensity = get_intensity()
        
        intensityXcap = intensity * 2/5 + 3/5 * (2 * intensity - intensity**2)
        intensityX = min(0.95, ((intensityXcap - intensity) * currentTimeInHours()/24)  + (intensity) )
        intensityY = min(0.95, (2 * intensity - intensity**2))

        return time_today * ((intensityX + intensityY)/2)
    
    @classmethod
    def get_time_d(cls, target_date):
        """
        Calculate total time available on date d
        Returns: timedelta object (24 hours for now, can be modified)
        """
        return timedelta(hours=18)
    
    @classmethod
    def get_free_d(cls, target_date, intensity_value=None):
        """
        Calculate free time available on date d
        Uses the same intensity-based logic as get_free_today but for any date
        Returns: timedelta object
        
        Args:
            target_date: Date to calculate free time for
            intensity_value: Optional intensity value (0.0-1.0). If None, uses global intensity
        """
        time_d = cls.get_time_d(target_date)
        
        # Use provided intensity or get global intensity
        if intensity_value is not None:
            if not 0.0 <= intensity_value <= 1.0:
                raise ValueError("Intensity value must be between 0.0 and 1.0")
            intensityX = intensity_value
        else:
            intensityX = get_intensity()
        
        # For future dates, we can't use currentTimeInHours(), so we'll use a default
        # or calculate based on the target date's time characteristics
        if target_date == timezone.now().date():
            # If it's today, use current time
            current_hours = cls.get_time_d(target_date)
        else:
            # For future dates, assume a reasonable time (e.g., 12:00 PM = 12.0 hours)
            # This can be customized based on your scheduling preferences
            current_hours = 18.0  # Midday assumption for future dates
        intensityY = min(0.95, (2 * intensityX - intensityX**2))
        
        return time_d * ((intensityX + intensityY)/2)
