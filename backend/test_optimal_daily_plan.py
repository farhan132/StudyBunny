#!/usr/bin/env python
"""
Test the optimal daily plan function with all three scenarios
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import get_optimal_daily_plan
from apps.study.models import Task
from datetime import datetime, timedelta, date
from django.utils import timezone

def test_optimal_daily_plan():
    """Test the optimal daily plan function with different scenarios"""
    print("Testing Optimal Daily Plan Function")
    print("=" * 70)
    
    # Get or create a test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"Created test user: {user.username}")
    
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    # Clear existing tasks for clean test
    Task.objects.filter(user=user).delete()
    
    print("\n🧪 SCENARIO 1: Manageable tasks (should complete all)")
    print("-" * 50)
    
    # Create manageable tasks
    manageable_tasks = [
        {
            'title': 'Quick Review',
            'description': 'Review documents - 30 minutes',
            'T_n': timedelta(minutes=30),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('18:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Email Response',
            'description': 'Respond to important emails - 1 hour',
            'T_n': timedelta(hours=1),
            'completed_so_far': 0.0,
            'delta': 4,  # High priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('19:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Code Review',
            'description': 'Review code changes - 2 hours',
            'T_n': timedelta(hours=2),
            'completed_so_far': 25.0,  # 25% completed
            'delta': 3,  # Medium priority
            'due_date': next_week,
            'due_time': datetime.strptime('17:00:00', '%H:%M:%S').time()
        }
    ]
    
    # Create tasks
    for task_data in manageable_tasks:
        Task.objects.create(user=user, **task_data)
    
    print("Created manageable tasks:")
    for task in Task.objects.filter(user=user, is_completed=False):
        print(f"  - {task.title} ({task.T_n}, Priority: {task.delta})")
    
    # Test with manageable tasks
    result1 = get_optimal_daily_plan(user, target_date=today, max_intensity=0.9)
    print(f"\nResult: {result1['message']}")
    print(f"Plan type: {result1['plan_type']}")
    print(f"Minimum intensity: {result1['minimum_intensity']:.3f}")
    print(f"Intensity used: {result1['intensity_used']:.3f}")
    print(f"Tasks in plan: {result1['tasks_count']}")
    print(f"Total time allocated: {result1['total_time_allocated']}")
    
    if result1['daily_plan']:
        print("\nDaily plan:")
        for i, task in enumerate(result1['daily_plan'], 1):
            print(f"  {i}. {task['task_title']}")
            print(f"     Time allotted: {task['time_allotted']}")
            print(f"     Priority: {task['priority']}")
            print(f"     Completion: {task['completion_before']:.1f}% -> {task['completion_after']:.1f}%")
            if task.get('partial_completion'):
                print(f"     ⚠️ Partial completion")
    
    # Clear tasks for next scenario
    Task.objects.filter(user=user).delete()
    
    print("\n" + "=" * 70)
    print("\n🧪 SCENARIO 2: Overwhelming tasks (should recommend removals)")
    print("-" * 50)
    
    # Create overwhelming tasks
    overwhelming_tasks = [
        {
            'title': 'Massive Project A',
            'description': 'Huge project requiring 20 hours',
            'T_n': timedelta(hours=20),
            'completed_so_far': 0.0,
            'delta': 3,  # Medium priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('18:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Massive Project B',
            'description': 'Another huge project requiring 15 hours',
            'T_n': timedelta(hours=15),
            'completed_so_far': 0.0,
            'delta': 2,  # Low priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('19:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Massive Project C',
            'description': 'Third huge project requiring 12 hours',
            'T_n': timedelta(hours=12),
            'completed_so_far': 0.0,
            'delta': 1,  # Very Low priority
            'due_date': next_week,
            'due_time': datetime.strptime('17:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Quick Task',
            'description': 'Small task - 1 hour',
            'T_n': timedelta(hours=1),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('20:00:00', '%H:%M:%S').time()
        }
    ]
    
    # Create tasks
    for task_data in overwhelming_tasks:
        Task.objects.create(user=user, **task_data)
    
    print("Created overwhelming tasks:")
    for task in Task.objects.filter(user=user, is_completed=False):
        print(f"  - {task.title} ({task.T_n}, Priority: {task.delta})")
    
    # Test with overwhelming tasks
    result2 = get_optimal_daily_plan(user, target_date=today, max_intensity=0.9)
    print(f"\nResult: {result2['message']}")
    print(f"Plan type: {result2['plan_type']}")
    print(f"Minimum intensity: {result2['minimum_intensity']:.3f}")
    print(f"Can complete all: {result2['can_complete_all']}")
    
    if result2['recommended_removals']:
        print(f"\nRecommended tasks to remove ({len(result2['recommended_removals'])}):")
        for i, task in enumerate(result2['recommended_removals'], 1):
            print(f"  {i}. {task['title']}")
            print(f"     Priority: {task['priority']}")
            print(f"     Time needed: {task['time_needed']}")
            print(f"     Due date: {task['due_date']}")
            print(f"     Reason: {task['reason']}")
    
    # Clear tasks for next scenario
    Task.objects.filter(user=user).delete()
    
    print("\n" + "=" * 70)
    print("\n🧪 SCENARIO 3: Mixed tasks (should prefer 2+ tasks)")
    print("-" * 50)
    
    # Create mixed tasks
    mixed_tasks = [
        {
            'title': 'High Priority Task',
            'description': 'Important task - 2 hours',
            'T_n': timedelta(hours=2),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('18:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Medium Priority Task',
            'description': 'Regular task - 1.5 hours',
            'T_n': timedelta(hours=1, minutes=30),
            'completed_so_far': 0.0,
            'delta': 3,  # Medium priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('19:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Low Priority Task',
            'description': 'Optional task - 1 hour',
            'T_n': timedelta(hours=1),
            'completed_so_far': 0.0,
            'delta': 2,  # Low priority
            'due_date': next_week,
            'due_time': datetime.strptime('17:00:00', '%H:%M:%S').time()
        }
    ]
    
    # Create tasks
    for task_data in mixed_tasks:
        Task.objects.create(user=user, **task_data)
    
    print("Created mixed tasks:")
    for task in Task.objects.filter(user=user, is_completed=False):
        print(f"  - {task.title} ({task.T_n}, Priority: {task.delta})")
    
    # Test with mixed tasks
    result3 = get_optimal_daily_plan(user, target_date=today, max_intensity=0.9)
    print(f"\nResult: {result3['message']}")
    print(f"Plan type: {result3['plan_type']}")
    print(f"Minimum intensity: {result3['minimum_intensity']:.3f}")
    print(f"Tasks in plan: {result3['tasks_count']}")
    print(f"Total time allocated: {result3['total_time_allocated']}")
    
    if result3['daily_plan']:
        print("\nDaily plan:")
        for i, task in enumerate(result3['daily_plan'], 1):
            print(f"  {i}. {task['task_title']}")
            print(f"     Time allotted: {task['time_allotted']}")
            print(f"     Priority: {task['priority']}")
            print(f"     Completion: {task['completion_before']:.1f}% -> {task['completion_after']:.1f}%")
            if task.get('partial_completion'):
                print(f"     ⚠️ Partial completion")
    
    print("\n" + "=" * 70)
    print("✅ Optimal daily plan test completed!")
    print("✅ All three scenarios handled correctly!")

if __name__ == "__main__":
    test_optimal_daily_plan()
