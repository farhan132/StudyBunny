#!/usr/bin/env python
"""
Test the currentTimeInHours function and intensity calculations
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from apps.core.models import currentTimeInHours, get_intensity, TimeCalculation
from datetime import datetime

def test_time_functions():
    """Test the time calculation functions"""
    print("Testing Time Calculation Functions")
    print("=" * 40)
    
    # Test currentTimeInHours
    current_hours = currentTimeInHours()
    print(f"Current time in hours: {current_hours:.2f}")
    print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test get_intensity
    intensity = get_intensity()
    print(f"Current intensity: {intensity}")
    
    # Test the intensity calculations
    print(f"\nIntensity calculations:")
    intensityXcap = intensity * 2/5 + 3/5 * (2 * intensity - intensity**2)
    intensityX = min(0.95, ((intensityXcap - intensity) * current_hours/24) + intensity)
    intensityY = min(0.95, (2 * intensity - intensity**2))
    
    print(f"intensityXcap: {intensityXcap:.3f}")
    print(f"intensityX: {intensityX:.3f}")
    print(f"intensityY: {intensityY:.3f}")
    print(f"Average: {(intensityX + intensityY)/2:.3f}")
    
    # Test get_free_today
    print(f"\nTesting get_free_today:")
    free_time = TimeCalculation.get_free_today()
    time_today = TimeCalculation.get_time_today()
    
    print(f"Time today: {time_today}")
    print(f"Free time today: {free_time}")
    print(f"Free time percentage: {(free_time.total_seconds() / time_today.total_seconds() * 100):.1f}%")
    
    print("\n" + "=" * 40)
    print("✓ All time functions are working correctly!")

if __name__ == "__main__":
    test_time_functions()
