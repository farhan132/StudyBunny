#!/usr/bin/env python
"""
Debug the daily plan generation
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import get_optimal_daily_plan, generate_daily_plan
from apps.study.models import Task
from apps.core.models import TimeCalculation
from datetime import datetime, timedelta, date
from django.utils import timezone

def debug_daily_plan():
    """Debug the daily plan generation"""
    print("Debugging Daily Plan Generation")
    print("=" * 50)
    
    # Get test user
    user = User.objects.get(username='testuser')
    today = timezone.now().date()
    
    # Clear and create test tasks
    Task.objects.filter(user=user).delete()
    
    test_tasks = [
        {
            'title': 'Quick Task',
            'description': '30 minute task',
            'T_n': timedelta(minutes=30),
            'completed_so_far': 0.0,
            'delta': 5,
            'due_date': today + timedelta(days=1),
            'due_time': datetime.strptime('18:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Medium Task',
            'description': '2 hour task',
            'T_n': timedelta(hours=2),
            'completed_so_far': 0.0,
            'delta': 3,
            'due_date': today + timedelta(days=1),
            'due_time': datetime.strptime('19:00:00', '%H:%M:%S').time()
        }
    ]
    
    for task_data in test_tasks:
        Task.objects.create(user=user, **task_data)
    
    print("Created test tasks:")
    for task in Task.objects.filter(user=user, is_completed=False):
        print(f"  - {task.title} ({task.T_n}, Priority: {task.delta})")
    
    # Check free time for today
    print(f"\nFree time calculations for today ({today}):")
    free_today_default = TimeCalculation.get_free_today()
    free_today_low = TimeCalculation.get_free_today(intensity_value=0.1)
    free_today_high = TimeCalculation.get_free_today(intensity_value=0.9)
    
    print(f"  Default intensity: {free_today_default}")
    print(f"  Low intensity (0.1): {free_today_low}")
    print(f"  High intensity (0.9): {free_today_high}")
    
    # Test daily plan generation directly
    print(f"\nTesting daily plan generation:")
    daily_plan = generate_daily_plan(user, today, 0.1, min_tasks=1)
    print(f"  Daily plan length: {len(daily_plan)}")
    
    if daily_plan:
        print("  Daily plan details:")
        for i, task in enumerate(daily_plan, 1):
            print(f"    {i}. {task['task_title']} - {task['time_allotted']} (type: {type(task['time_allotted'])})")
    else:
        print("  No tasks in daily plan")
    
    # Test with different intensities
    print(f"\nTesting different intensities:")
    for intensity in [0.1, 0.3, 0.5, 0.7, 0.9]:
        plan = generate_daily_plan(user, today, intensity, min_tasks=1)
        print(f"  Intensity {intensity}: {len(plan)} tasks")
        if plan:
            total_time = timedelta()
            for task in plan:
                if isinstance(task['time_allotted'], timedelta):
                    total_time += task['time_allotted']
            print(f"    Total time: {total_time}")
    
    # Test the full optimal daily plan
    print(f"\nTesting full optimal daily plan:")
    result = get_optimal_daily_plan(user, target_date=today, max_intensity=0.9)
    print(f"  Success: {result['success']}")
    print(f"  Plan type: {result['plan_type']}")
    print(f"  Tasks count: {result['tasks_count']}")
    print(f"  Message: {result['message']}")
    
    if result['daily_plan']:
        print("  Daily plan:")
        for i, task in enumerate(result['daily_plan'], 1):
            print(f"    {i}. {task['task_title']} - {task['time_allotted']}")

if __name__ == "__main__":
    debug_daily_plan()
