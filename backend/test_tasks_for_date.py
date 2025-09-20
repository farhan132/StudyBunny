#!/usr/bin/env python
"""
Test the get_tasks_for_date functions
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import get_tasks_for_date, get_tasks_for_date_with_rounding
from apps.study.models import Task
from datetime import datetime, timedelta, date
from django.utils import timezone

def test_tasks_for_date():
    """Test the get_tasks_for_date functions"""
    print("📅 TESTING GET TASKS FOR DATE FUNCTIONS")
    print("=" * 80)
    
    # Get test user
    user = User.objects.get(username='testuser')
    today = timezone.now().date()
    
    # Clear existing tasks
    Task.objects.filter(user=user).delete()
    
    print("🏗️ Creating sample tasks...")
    
    # Create some sample tasks
    sample_tasks = [
        {
            'title': 'Morning Code Review',
            'description': 'Review team member code changes',
            'T_n': timedelta(hours=2, minutes=15),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': today,
            'due_time': datetime.strptime('09:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Bug Fix Implementation',
            'description': 'Fix critical bug in authentication system',
            'T_n': timedelta(hours=3, minutes=47),
            'completed_so_far': 25.0,  # 25% completed
            'delta': 5,  # Very High priority
            'due_date': today,
            'due_time': datetime.strptime('11:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Documentation Update',
            'description': 'Update API documentation',
            'T_n': timedelta(hours=1, minutes=33),
            'completed_so_far': 0.0,
            'delta': 3,  # Medium priority
            'due_date': today,
            'due_time': datetime.strptime('14:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Team Meeting Prep',
            'description': 'Prepare for weekly team meeting',
            'T_n': timedelta(minutes=45),
            'completed_so_far': 0.0,
            'delta': 4,  # High priority
            'due_date': today,
            'due_time': datetime.strptime('15:30:00', '%H:%M:%S').time()
        },
        {
            'title': 'Database Optimization',
            'description': 'Optimize slow database queries',
            'T_n': timedelta(hours=4, minutes=22),
            'completed_so_far': 0.0,
            'delta': 2,  # Low priority
            'due_date': today + timedelta(days=1),
            'due_time': datetime.strptime('10:00:00', '%H:%M:%S').time()
        }
    ]
    
    # Create tasks
    for task_data in sample_tasks:
        Task.objects.create(user=user, **task_data)
    
    print(f"✅ Created {len(sample_tasks)} sample tasks")
    
    print("\n" + "=" * 80)
    print("🧪 TEST 1: Basic get_tasks_for_date (no rounding)")
    print("=" * 80)
    
    # Test basic function
    result1 = get_tasks_for_date(user, target_date=today, max_intensity=0.9)
    
    if result1['success']:
        print(f"✅ {result1['message']}")
        print(f"📊 Summary:")
        print(f"   Target Date: {result1['target_date']}")
        print(f"   Total Tasks: {result1['total_tasks']}")
        print(f"   Total Time: {result1['total_time']}")
        print(f"   Intensity Used: {result1['intensity_used']:.3f}")
        print(f"   Schedule Info: {result1['schedule_info']['total_tasks_scheduled']} tasks in 14-day schedule")
        
        if result1['tasks']:
            print(f"\n📋 Tasks for {result1['target_date']}:")
            for i, task in enumerate(result1['tasks'], 1):
                print(f"  {i}. {task['task_title']}")
                print(f"     ⏱️  Time: {task['time_allotted']}")
                print(f"     🎯 Priority: {task['priority']}")
                print(f"     📈 Progress: {task['completion_before']:.1f}% → {task['completion_after']:.1f}%")
                if task.get('partial_completion'):
                    print(f"     ⚠️  Partial completion")
    else:
        print(f"❌ Error: {result1['error']}")
    
    print("\n" + "=" * 80)
    print("🧪 TEST 2: get_tasks_for_date_with_rounding (5-minute blocks)")
    print("=" * 80)
    
    # Test function with rounding
    result2 = get_tasks_for_date_with_rounding(user, target_date=today, max_intensity=0.9, round_to_5min=True)
    
    if result2['success']:
        print(f"✅ {result2['message']}")
        print(f"📊 Summary:")
        print(f"   Target Date: {result2['target_date']}")
        print(f"   Total Tasks: {result2['total_tasks']}")
        print(f"   Total Time (Rounded): {result2['total_time']}")
        if 'total_time_original' in result2:
            print(f"   Total Time (Original): {result2['total_time_original']}")
        print(f"   Intensity Used: {result2['intensity_used']:.3f}")
        
        if result2['tasks']:
            print(f"\n📋 Tasks for {result2['target_date']} (with 5-minute rounding):")
            for i, task in enumerate(result2['tasks'], 1):
                print(f"  {i}. {task['task_title']}")
                print(f"     ⏱️  Time (Rounded): {task['time_allotted']}")
                if 'time_allotted_original' in task:
                    print(f"     ⏱️  Time (Original): {task['time_allotted_original']}")
                print(f"     🎯 Priority: {task['priority']}")
                print(f"     📈 Progress: {task['completion_before']:.1f}% → {task['completion_after']:.1f}%")
                if task.get('partial_completion'):
                    print(f"     ⚠️  Partial completion")
    else:
        print(f"❌ Error: {result2['error']}")
    
    print("\n" + "=" * 80)
    print("🧪 TEST 3: get_tasks_for_date_with_rounding (no rounding)")
    print("=" * 80)
    
    # Test function without rounding
    result3 = get_tasks_for_date_with_rounding(user, target_date=today, max_intensity=0.9, round_to_5min=False)
    
    if result3['success']:
        print(f"✅ {result3['message']}")
        print(f"📊 Summary:")
        print(f"   Target Date: {result3['target_date']}")
        print(f"   Total Tasks: {result3['total_tasks']}")
        print(f"   Total Time: {result3['total_time']}")
        print(f"   Intensity Used: {result3['intensity_used']:.3f}")
        
        if result3['tasks']:
            print(f"\n📋 Tasks for {result3['target_date']} (no rounding):")
            for i, task in enumerate(result3['tasks'], 1):
                print(f"  {i}. {task['task_title']}")
                print(f"     ⏱️  Time: {task['time_allotted']}")
                print(f"     🎯 Priority: {task['priority']}")
                print(f"     📈 Progress: {task['completion_before']:.1f}% → {task['completion_after']:.1f}%")
    else:
        print(f"❌ Error: {result3['error']}")
    
    print("\n" + "=" * 80)
    print("🧪 TEST 4: Different dates")
    print("=" * 80)
    
    # Test with different dates
    test_dates = [
        today + timedelta(days=1),  # Tomorrow
        today + timedelta(days=7),  # Next week
        today + timedelta(days=14), # Two weeks from now
    ]
    
    for test_date in test_dates:
        print(f"\n📅 Testing date: {test_date}")
        result = get_tasks_for_date_with_rounding(user, target_date=test_date, max_intensity=0.9, round_to_5min=True)
        
        if result['success']:
            print(f"   {result['message']}")
            if result['tasks']:
                print(f"   Total time: {result['total_time']}")
        else:
            print(f"   ❌ Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print("✅ GET TASKS FOR DATE TEST COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    test_tasks_for_date()
