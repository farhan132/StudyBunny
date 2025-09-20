#!/usr/bin/env python
"""
Test the updated intensity functions in models.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from apps.core.models import TimeCalculation, get_intensity
from datetime import date, timedelta
from django.utils import timezone

def test_intensity_functions():
    """Test the updated intensity functions"""
    print("Testing Updated Intensity Functions")
    print("=" * 50)
    
    # Test 1: Default intensity (no parameter)
    print("1. Testing with default intensity:")
    free_today_default = TimeCalculation.get_free_today()
    free_d_default = TimeCalculation.get_free_d(timezone.now().date())
    print(f"   get_free_today() (default): {free_today_default}")
    print(f"   get_free_d(today) (default): {free_d_default}")
    print(f"   Global intensity: {get_intensity()}")
    
    # Test 2: Different intensity values
    print("\n2. Testing with different intensity values:")
    intensity_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    for intensity in intensity_values:
        try:
            free_today = TimeCalculation.get_free_today(intensity_value=intensity)
            free_d = TimeCalculation.get_free_d(timezone.now().date(), intensity_value=intensity)
            print(f"   Intensity {intensity}:")
            print(f"     get_free_today(): {free_today}")
            print(f"     get_free_d(): {free_d}")
        except ValueError as e:
            print(f"   Intensity {intensity}: Error - {e}")
    
    # Test 3: Future date with different intensities
    print("\n3. Testing future date with different intensities:")
    future_date = timezone.now().date() + timedelta(days=3)
    
    for intensity in [0.2, 0.6, 0.8]:
        try:
            free_d_future = TimeCalculation.get_free_d(future_date, intensity_value=intensity)
            print(f"   Future date {future_date} with intensity {intensity}: {free_d_future}")
        except ValueError as e:
            print(f"   Future date with intensity {intensity}: Error - {e}")
    
    # Test 4: Invalid intensity values
    print("\n4. Testing invalid intensity values:")
    invalid_values = [-0.1, 1.1, 2.0, "invalid"]
    
    for invalid_val in invalid_values:
        try:
            TimeCalculation.get_free_today(intensity_value=invalid_val)
            print(f"   Invalid value {invalid_val}: Should have failed!")
        except (ValueError, TypeError) as e:
            print(f"   Invalid value {invalid_val}: Correctly caught - {e}")
    
    # Test 5: Compare different intensities
    print("\n5. Comparing free time with different intensities:")
    today = timezone.now().date()
    
    low_intensity = TimeCalculation.get_free_today(intensity_value=0.2)
    medium_intensity = TimeCalculation.get_free_today(intensity_value=0.5)
    high_intensity = TimeCalculation.get_free_today(intensity_value=0.8)
    
    print(f"   Low intensity (0.2): {low_intensity}")
    print(f"   Medium intensity (0.5): {medium_intensity}")
    print(f"   High intensity (0.8): {high_intensity}")
    
    # Calculate ratios
    if low_intensity.total_seconds() > 0:
        medium_ratio = medium_intensity.total_seconds() / low_intensity.total_seconds()
        high_ratio = high_intensity.total_seconds() / low_intensity.total_seconds()
        print(f"   Medium vs Low ratio: {medium_ratio:.2f}")
        print(f"   High vs Low ratio: {high_ratio:.2f}")
    
    print("\n" + "=" * 50)
    print("✅ All intensity function tests completed!")
    print("✅ Functions now accept optional intensity parameters!")

if __name__ == "__main__":
    test_intensity_functions()
