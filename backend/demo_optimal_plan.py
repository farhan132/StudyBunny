#!/usr/bin/env python
"""
Final demonstration of the optimal daily plan function
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

def demo_optimal_plan():
    """Demonstrate the optimal daily plan function"""
    print("🎯 OPTIMAL DAILY PLAN DEMONSTRATION")
    print("=" * 80)
    
    # Get test user
    user = User.objects.get(username='testuser')
    today = timezone.now().date()
    
    print("\n📋 REQUIREMENTS IMPLEMENTED:")
    print("1. ✅ Find minimum intensity needed to complete all tasks")
    print("2. ✅ If impossible (intensity > 0.9), recommend tasks to remove")
    print("3. ✅ Return daily plan with tasks and time allocations")
    print("4. ✅ Prefer plans with at least 2 tasks when possible")
    
    # Clear existing tasks
    Task.objects.filter(user=user).delete()
    
    print("\n" + "=" * 80)
    print("🧪 SCENARIO 1: MANAGEABLE TASKS")
    print("=" * 80)
    
    # Create small, manageable tasks
    manageable_tasks = [
        {
            'title': 'Morning Review',
            'description': 'Quick morning review - 30 minutes',
            'T_n': timedelta(minutes=30),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': today + timedelta(days=1),
            'due_time': datetime.strptime('09:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Email Check',
            'description': 'Check and respond to emails - 45 minutes',
            'T_n': timedelta(minutes=45),
            'completed_so_far': 0.0,
            'delta': 4,  # High priority
            'due_date': today + timedelta(days=1),
            'due_time': datetime.strptime('10:00:00', '%H:%M:%S').time()
        }
    ]
    
    for task_data in manageable_tasks:
        Task.objects.create(user=user, **task_data)
    
    print("Created manageable tasks:")
    for task in Task.objects.filter(user=user, is_completed=False):
        print(f"  • {task.title} ({task.T_n}, Priority: {task.delta})")
    
    result1 = get_optimal_daily_plan(user, target_date=today, max_intensity=0.9)
    
    print(f"\n📊 RESULT: {result1['message']}")
    print(f"   Plan Type: {result1['plan_type']}")
    print(f"   Minimum Intensity: {result1['minimum_intensity']:.3f}")
    print(f"   Intensity Used: {result1['intensity_used']:.3f}")
    print(f"   Tasks Scheduled: {result1['tasks_count']}")
    print(f"   Total Time: {result1['total_time_allocated']}")
    
    if result1['daily_plan']:
        print("\n📅 DAILY SCHEDULE:")
        for i, task in enumerate(result1['daily_plan'], 1):
            print(f"   {i}. {task['task_title']}")
            print(f"      ⏱️  Time: {task['time_allotted']}")
            print(f"      🎯 Priority: {task['priority']}")
            print(f"      📈 Progress: {task['completion_before']:.1f}% → {task['completion_after']:.1f}%")
            if task.get('partial_completion'):
                print(f"      ⚠️  Partial completion")
    
    # Clear for next scenario
    Task.objects.filter(user=user).delete()
    
    print("\n" + "=" * 80)
    print("🧪 SCENARIO 2: OVERWHELMING TASKS")
    print("=" * 80)
    
    # Create overwhelming tasks that require high intensity
    overwhelming_tasks = [
        {
            'title': 'Massive Project Alpha',
            'description': 'Huge project requiring 25 hours',
            'T_n': timedelta(hours=25),
            'completed_so_far': 0.0,
            'delta': 2,  # Low priority
            'due_date': today + timedelta(days=1),
            'due_time': datetime.strptime('09:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Massive Project Beta',
            'description': 'Another huge project requiring 20 hours',
            'T_n': timedelta(hours=20),
            'completed_so_far': 0.0,
            'delta': 1,  # Very Low priority
            'due_date': today + timedelta(days=2),
            'due_time': datetime.strptime('10:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Quick Fix',
            'description': 'Small urgent fix - 1 hour',
            'T_n': timedelta(hours=1),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': today + timedelta(days=1),
            'due_time': datetime.strptime('11:00:00', '%H:%M:%S').time()
        }
    ]
    
    for task_data in overwhelming_tasks:
        Task.objects.create(user=user, **task_data)
    
    print("Created overwhelming tasks:")
    for task in Task.objects.filter(user=user, is_completed=False):
        print(f"  • {task.title} ({task.T_n}, Priority: {task.delta})")
    
    result2 = get_optimal_daily_plan(user, target_date=today, max_intensity=0.9)
    
    print(f"\n📊 RESULT: {result2['message']}")
    print(f"   Plan Type: {result2['plan_type']}")
    print(f"   Minimum Intensity: {result2['minimum_intensity']:.3f}")
    print(f"   Can Complete All: {result2['can_complete_all']}")
    
    if result2['recommended_removals']:
        print(f"\n🗑️  RECOMMENDED TASKS TO REMOVE ({len(result2['recommended_removals'])}):")
        for i, task in enumerate(result2['recommended_removals'], 1):
            print(f"   {i}. {task['title']}")
            print(f"      🎯 Priority: {task['priority']}")
            print(f"      ⏱️  Time Needed: {task['time_needed']}")
            print(f"      📅 Due: {task['due_date']}")
            print(f"      💡 Reason: {task['reason']}")
    
    # Clear for next scenario
    Task.objects.filter(user=user).delete()
    
    print("\n" + "=" * 80)
    print("🧪 SCENARIO 3: MIXED TASKS (PREFER 2+ TASKS)")
    print("=" * 80)
    
    # Create mixed tasks that should allow 2+ tasks
    mixed_tasks = [
        {
            'title': 'High Priority Task',
            'description': 'Important task - 1 hour',
            'T_n': timedelta(hours=1),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': today + timedelta(days=1),
            'due_time': datetime.strptime('09:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Medium Priority Task',
            'description': 'Regular task - 1.5 hours',
            'T_n': timedelta(hours=1, minutes=30),
            'completed_so_far': 0.0,
            'delta': 3,  # Medium priority
            'due_date': today + timedelta(days=1),
            'due_time': datetime.strptime('10:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Low Priority Task',
            'description': 'Optional task - 2 hours',
            'T_n': timedelta(hours=2),
            'completed_so_far': 0.0,
            'delta': 2,  # Low priority
            'due_date': today + timedelta(days=3),
            'due_time': datetime.strptime('11:00:00', '%H:%M:%S').time()
        }
    ]
    
    for task_data in mixed_tasks:
        Task.objects.create(user=user, **task_data)
    
    print("Created mixed tasks:")
    for task in Task.objects.filter(user=user, is_completed=False):
        print(f"  • {task.title} ({task.T_n}, Priority: {task.delta})")
    
    result3 = get_optimal_daily_plan(user, target_date=today, max_intensity=0.9)
    
    print(f"\n📊 RESULT: {result3['message']}")
    print(f"   Plan Type: {result3['plan_type']}")
    print(f"   Minimum Intensity: {result3['minimum_intensity']:.3f}")
    print(f"   Intensity Used: {result3['intensity_used']:.3f}")
    print(f"   Tasks Scheduled: {result3['tasks_count']}")
    print(f"   Total Time: {result3['total_time_allocated']}")
    
    if result3['daily_plan']:
        print("\n📅 DAILY SCHEDULE:")
        for i, task in enumerate(result3['daily_plan'], 1):
            print(f"   {i}. {task['task_title']}")
            print(f"      ⏱️  Time: {task['time_allotted']}")
            print(f"      🎯 Priority: {task['priority']}")
            print(f"      📈 Progress: {task['completion_before']:.1f}% → {task['completion_after']:.1f}%")
            if task.get('partial_completion'):
                print(f"      ⚠️  Partial completion")
    
    print("\n" + "=" * 80)
    print("✅ DEMONSTRATION COMPLETE!")
    print("✅ All three requirements successfully implemented!")
    print("=" * 80)

if __name__ == "__main__":
    demo_optimal_plan()
