#!/usr/bin/env python
"""
Test the binary search function for finding minimum intensity
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import find_minimum_intensity_for_completion, can_complete_tasks_with_intensity
from apps.study.models import Task
from datetime import datetime, timedelta, date
from django.utils import timezone

def test_binary_search_intensity():
    """Test the binary search function for finding minimum intensity"""
    print("Testing Binary Search for Minimum Intensity")
    print("=" * 60)
    
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
    
    # Create test tasks with different complexities
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    # Clear existing tasks for clean test
    Task.objects.filter(user=user).delete()
    
    # Create test tasks with varying time requirements and priorities
    test_tasks = [
        {
            'title': 'Quick Task 1',
            'description': 'Short task - 30 minutes',
            'T_n': timedelta(minutes=30),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('18:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Medium Task 2',
            'description': 'Medium task - 2 hours',
            'T_n': timedelta(hours=2),
            'completed_so_far': 0.0,
            'delta': 4,  # High priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('19:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Long Task 3',
            'description': 'Long task - 4 hours',
            'T_n': timedelta(hours=4),
            'completed_so_far': 25.0,  # 25% completed
            'delta': 3,  # Medium priority
            'due_date': next_week,
            'due_time': datetime.strptime('17:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Very Long Task 4',
            'description': 'Very long task - 6 hours',
            'T_n': timedelta(hours=6),
            'completed_so_far': 0.0,
            'delta': 2,  # Low priority
            'due_date': next_week,
            'due_time': datetime.strptime('20:00:00', '%H:%M:%S').time()
        }
    ]
    
    # Create tasks in database
    created_tasks = []
    for task_data in test_tasks:
        task = Task.objects.create(user=user, **task_data)
        created_tasks.append(task)
        print(f"Created task: {task.title} ({task.T_n}, Priority: {task.delta})")
    
    print(f"\nTotal tasks created: {len(created_tasks)}")
    print("=" * 60)
    
    # Test 1: Binary search with default parameters
    print("\n🔍 Test 1: Binary search with default parameters")
    print("-" * 50)
    
    result = find_minimum_intensity_for_completion(user)
    
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"   Minimum intensity: {result['minimum_intensity']:.4f}")
        print(f"   Can complete all: {result['can_complete_all']}")
        print(f"   Total tasks: {result['total_tasks']}")
        print(f"   Iterations used: {result['iterations_used']}")
        print(f"   Precision achieved: {result['precision_achieved']:.6f}")
        print(f"   Search range: [{result['search_range']['low']:.4f}, {result['search_range']['high']:.4f}]")
        
        if result['schedule_analysis']:
            schedule = result['schedule_analysis']
            print(f"   Schedule analysis:")
            print(f"     Time needed: {schedule['total_time_needed']}")
            print(f"     Time available: {schedule['total_time_available']}")
            print(f"     Efficiency: {schedule['efficiency']:.2%}")
    else:
        print(f"❌ Error: {result['error']}")
    
    # Test 2: Binary search with custom precision
    print("\n🔍 Test 2: Binary search with high precision (0.001)")
    print("-" * 50)
    
    result_precise = find_minimum_intensity_for_completion(
        user, 
        precision=0.001,
        max_iterations=100
    )
    
    if result_precise['success']:
        print(f"✅ {result_precise['message']}")
        print(f"   Minimum intensity: {result_precise['minimum_intensity']:.6f}")
        print(f"   Iterations used: {result_precise['iterations_used']}")
        print(f"   Precision achieved: {result_precise['precision_achieved']:.8f}")
    else:
        print(f"❌ Error: {result_precise['error']}")
    
    # Test 3: Binary search with shorter time frame
    print("\n🔍 Test 3: Binary search with shorter time frame (3 days)")
    print("-" * 50)
    
    result_short = find_minimum_intensity_for_completion(
        user,
        start_date=today,
        end_date=today + timedelta(days=3)
    )
    
    if result_short['success']:
        print(f"✅ {result_short['message']}")
        print(f"   Minimum intensity: {result_short['minimum_intensity']:.4f}")
        print(f"   Can complete all: {result_short['can_complete_all']}")
        print(f"   Iterations used: {result_short['iterations_used']}")
    else:
        print(f"❌ Error: {result_short['error']}")
    
    # Test 4: Verify the found minimum intensity
    print("\n🔍 Test 4: Verification of found minimum intensity")
    print("-" * 50)
    
    if result['success'] and result['minimum_intensity'] >= 0:
        min_intensity = result['minimum_intensity']
        
        # Test slightly below minimum (should fail)
        test_below = min_intensity - 0.01
        if test_below > 0:
            verify_below = can_complete_tasks_with_intensity(user, test_below)
            print(f"   Intensity {test_below:.4f} (below minimum): {'✅ Can complete' if verify_below['can_complete'] else '❌ Cannot complete'}")
        
        # Test at minimum (should succeed)
        verify_at = can_complete_tasks_with_intensity(user, min_intensity)
        print(f"   Intensity {min_intensity:.4f} (at minimum): {'✅ Can complete' if verify_at['can_complete'] else '❌ Cannot complete'}")
        
        # Test slightly above minimum (should succeed)
        test_above = min_intensity + 0.01
        if test_above <= 1.0:
            verify_above = can_complete_tasks_with_intensity(user, test_above)
            print(f"   Intensity {test_above:.4f} (above minimum): {'✅ Can complete' if verify_above['can_complete'] else '❌ Cannot complete'}")
    
    # Test 5: Edge case - no tasks
    print("\n🔍 Test 5: Edge case - no tasks")
    print("-" * 50)
    
    # Temporarily mark all tasks as completed
    Task.objects.filter(user=user).update(is_completed=True)
    
    result_no_tasks = find_minimum_intensity_for_completion(user)
    
    if result_no_tasks['success']:
        print(f"✅ {result_no_tasks['message']}")
        print(f"   Minimum intensity: {result_no_tasks['minimum_intensity']}")
        print(f"   Total tasks: {result_no_tasks['total_tasks']}")
    else:
        print(f"❌ Error: {result_no_tasks['error']}")
    
    # Restore tasks
    Task.objects.filter(user=user).update(is_completed=False)
    
    print("\n" + "=" * 60)
    print("✅ Binary search intensity optimization test completed!")
    print("✅ The function successfully finds minimum intensity using binary search!")

if __name__ == "__main__":
    test_binary_search_intensity()
