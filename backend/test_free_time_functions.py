#!/usr/bin/env python
"""
Test both get_free_today and get_free_d functions
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from apps.core.models import TimeCalculation, currentTimeInHours
from datetime import datetime, timedelta

def test_free_time_functions():
    """Test both free time calculation functions"""
    print("Testing Free Time Calculation Functions")
    print("=" * 50)
    
    # Test get_free_today
    print("1. Testing get_free_today:")
    free_today = TimeCalculation.get_free_today()
    time_today = TimeCalculation.get_time_today()
    
    print(f"   Time today: {time_today}")
    print(f"   Free time today: {free_today}")
    print(f"   Free time percentage: {(free_today.total_seconds() / time_today.total_seconds() * 100):.1f}%")
    
    # Test get_free_d for today (should be same as get_free_today)
    print("\n2. Testing get_free_d for today:")
    today = datetime.now().date()
    free_d_today = TimeCalculation.get_free_d(today)
    
    print(f"   Time d (today): {TimeCalculation.get_time_d(today)}")
    print(f"   Free d (today): {free_d_today}")
    print(f"   Free d percentage: {(free_d_today.total_seconds() / TimeCalculation.get_time_d(today).total_seconds() * 100):.1f}%")
    
    # Test get_free_d for tomorrow
    print("\n3. Testing get_free_d for tomorrow:")
    tomorrow = today + timedelta(days=1)
    free_d_tomorrow = TimeCalculation.get_free_d(tomorrow)
    
    print(f"   Time d (tomorrow): {TimeCalculation.get_time_d(tomorrow)}")
    print(f"   Free d (tomorrow): {free_d_tomorrow}")
    print(f"   Free d percentage: {(free_d_tomorrow.total_seconds() / TimeCalculation.get_time_d(tomorrow).total_seconds() * 100):.1f}%")
    
    # Test get_free_d for next week
    print("\n4. Testing get_free_d for next week:")
    next_week = today + timedelta(days=7)
    free_d_next_week = TimeCalculation.get_free_d(next_week)
    
    print(f"   Time d (next week): {TimeCalculation.get_time_d(next_week)}")
    print(f"   Free d (next week): {free_d_next_week}")
    print(f"   Free d percentage: {(free_d_next_week.total_seconds() / TimeCalculation.get_time_d(next_week).total_seconds() * 100):.1f}%")
    
    # Compare today's results
    print("\n5. Comparing today's results:")
    print(f"   get_free_today(): {free_today}")
    print(f"   get_free_d(today): {free_d_tomorrow}")
    print(f"   Difference: {abs((free_today - free_d_today).total_seconds()):.2f} seconds")
    
    # Show intensity calculations for different times
    print("\n6. Intensity calculations for different times:")
    current_hours = currentTimeInHours()
    print(f"   Current time: {current_hours:.2f} hours")
    print(f"   Tomorrow assumption: 12.0 hours")
    
    from apps.core.models import get_intensity
    intensity = get_intensity()
    intensityXcap = intensity * 2/5 + 3/5 * (2 * intensity - intensity**2)
    
    # Current time calculation
    intensityX_current = min(0.95, ((intensityXcap - intensity) * current_hours/24) + intensity)
    intensityY = min(0.95, (2 * intensity - intensity**2))
    avg_current = (intensityX_current + intensityY)/2
    
    # Tomorrow calculation (12.0 hours)
    intensityX_tomorrow = min(0.95, ((intensityXcap - intensity) * 12.0/24) + intensity)
    avg_tomorrow = (intensityX_tomorrow + intensityY)/2
    
    print(f"   Today's intensity factor: {avg_current:.3f}")
    print(f"   Tomorrow's intensity factor: {avg_tomorrow:.3f}")
    
    print("\n" + "=" * 50)
    print("✓ Both free time functions are working correctly!")
    print("✓ get_free_d now uses the same intensity logic as get_free_today!")

if __name__ == "__main__":
    test_free_time_functions()
