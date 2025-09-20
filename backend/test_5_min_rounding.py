#!/usr/bin/env python
"""
Test the 5-minute rounding function
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from apps.study.task_utils import round_to_5_min_blocks
from datetime import timedelta

def test_5_min_rounding():
    """Test the 5-minute rounding function with various time durations"""
    print("⏰ TESTING 5-MINUTE ROUNDING FUNCTION")
    print("=" * 60)
    
    # Test cases with various time durations
    test_cases = [
        # Original example from the 100-task test
        timedelta(hours=13, minutes=49, seconds=14, microseconds=907432),
        
        # Various time durations to test rounding
        timedelta(minutes=2, seconds=30),      # 2:30 -> 5:00 (round up) or 0:00 (round down)
        timedelta(minutes=7, seconds=15),      # 7:15 -> 10:00 (round up) or 5:00 (round down)
        timedelta(minutes=12, seconds=45),     # 12:45 -> 15:00 (round up) or 10:00 (round down)
        timedelta(minutes=23, seconds=7),      # 23:07 -> 25:00 (round up) or 20:00 (round down)
        timedelta(hours=1, minutes=33, seconds=22),  # 1:33:22 -> 1:35:00 (round up) or 1:30:00 (round down)
        timedelta(hours=2, minutes=47, seconds=8),   # 2:47:08 -> 2:50:00 (round up) or 2:45:00 (round down)
        timedelta(minutes=5),                  # 5:00 -> 5:00 (already on 5-min boundary)
        timedelta(minutes=10),                 # 10:00 -> 10:00 (already on 5-min boundary)
        timedelta(minutes=0, seconds=30),      # 0:30 -> 5:00 (round up) or 0:00 (round down)
        timedelta(minutes=1, seconds=1),       # 1:01 -> 5:00 (round up) or 0:00 (round down)
    ]
    
    print("📊 ROUNDING TEST RESULTS:")
    print("-" * 60)
    print(f"{'Original Time':<20} {'Round Up':<15} {'Round Down':<15}")
    print("-" * 60)
    
    for original_time in test_cases:
        rounded_up = round_to_5_min_blocks(original_time, round_up=True)
        rounded_down = round_to_5_min_blocks(original_time, round_up=False)
        
        print(f"{str(original_time):<20} {str(rounded_up):<15} {str(rounded_down):<15}")
    
    print("\n" + "=" * 60)
    print("🎯 SPECIFIC EXAMPLE FROM 100-TASK TEST:")
    print("=" * 60)
    
    # The specific example from the 100-task test
    original_time = timedelta(hours=13, minutes=49, seconds=14, microseconds=907432)
    rounded_up = round_to_5_min_blocks(original_time, round_up=True)
    rounded_down = round_to_5_min_blocks(original_time, round_up=False)
    
    print(f"Original time: {original_time}")
    print(f"Rounded up:   {rounded_up}")
    print(f"Rounded down: {rounded_down}")
    
    # Calculate the difference
    diff_up = rounded_up - original_time
    diff_down = original_time - rounded_down
    
    print(f"\nDifference when rounding up:   {diff_up}")
    print(f"Difference when rounding down: {diff_down}")
    
    # Show in different formats
    print(f"\nFormatted times:")
    print(f"Original: {original_time}")
    print(f"Rounded up: {rounded_up} ({rounded_up.total_seconds()/60:.0f} minutes)")
    print(f"Rounded down: {rounded_down} ({rounded_down.total_seconds()/60:.0f} minutes)")
    
    print("\n" + "=" * 60)
    print("✅ 5-MINUTE ROUNDING TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    test_5_min_rounding()
