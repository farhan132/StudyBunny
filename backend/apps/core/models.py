from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import math

# Create your models here.

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
    def get_free_today(cls, target_date=None):
        """
        Calculate free time available today
        This is a skeleton function - implement your logic here
        Returns: timedelta object
        """
        # TODO: Implement your free time calculation logic
        # This could involve checking scheduled events, work hours, etc.
        time_today = cls.get_time_today(target_date)
        # Placeholder: assume 50% of remaining time is free
        return time_today * 0.5
    
    @classmethod
    def get_time_d(cls, target_date):
        """
        Calculate total time available on date d
        Returns: timedelta object (24 hours for now, can be modified)
        """
        return timedelta(hours=24)
    
    @classmethod
    def get_free_d(cls, target_date):
        """
        Calculate free time available on date d
        This is a skeleton function - implement your logic here
        Returns: timedelta object
        """
        # TODO: Implement your free time calculation logic for future dates
        time_d = cls.get_time_d(target_date)
        # Placeholder: assume 50% of the day is free
        return time_d * 0.5
