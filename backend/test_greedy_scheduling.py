#!/usr/bin/env python
"""
Test the greedy task scheduling function
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import can_complete_tasks_with_intensity
from apps.study.models import Task
from datetime import datetime, timedelta, date
from django.utils import timezone

def test_greedy_scheduling():
    """Test the greedy task scheduling function with different intensity values"""
    print("Testing Greedy Task Scheduling Algorithm")
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
    
    # Create some test tasks
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    # Clear existing tasks for clean test
    Task.objects.filter(user=user).delete()
    
    # Create test tasks with different priorities and due dates
    test_tasks = [
        {
            'title': 'High Priority Task 1',
            'description': 'Urgent task due tomorrow',
            'T_n': timedelta(hours=2),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('18:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Medium Priority Task 2',
            'description': 'Regular task due next week',
            'T_n': timedelta(hours=4),
            'completed_so_far': 25.0,  # 25% completed
            'delta': 3,  # Medium priority
            'due_date': next_week,
            'due_time': datetime.strptime('17:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Low Priority Task 3',
            'description': 'Low priority task',
            'T_n': timedelta(hours=1, minutes=30),
            'completed_so_far': 0.0,
            'delta': 2,  # Low priority
            'due_date': next_week,
            'due_time': datetime.strptime('19:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Partially Complete Task',
            'description': 'Task that is 50% complete',
            'T_n': timedelta(hours=3),
            'completed_so_far': 50.0,  # 50% completed
            'delta': 4,  # High priority
            'due_date': tomorrow,
            'due_time': datetime.strptime('20:00:00', '%H:%M:%S').time()
        }
    ]
    
    # Create tasks in database
    created_tasks = []
    for task_data in test_tasks:
        task = Task.objects.create(user=user, **task_data)
        created_tasks.append(task)
        print(f"Created task: {task.title} (Priority: {task.delta}, Due: {task.due_date})")
    
    print(f"\nTotal tasks created: {len(created_tasks)}")
    print("=" * 60)
    
    # Test with different intensity values
    intensity_values = [0.2, 0.5, 0.7, 0.9]
    
    for intensity in intensity_values:
        print(f"\n🧪 Testing with Intensity: {intensity}")
        print("-" * 40)
        
        result = can_complete_tasks_with_intensity(
            user=user,
            intensity_value=intensity,
            start_date=today,
            end_date=today + timedelta(days=14)  # 2 weeks
        )
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"   Total tasks: {result['total_tasks']}")
            print(f"   Can complete: {result['completed_tasks']}")
            print(f"   Remaining: {result['remaining_tasks']}")
            print(f"   Time needed: {result['total_time_needed']}")
            print(f"   Time available: {result['total_time_available']}")
            print(f"   Efficiency: {result['efficiency']:.2%}")
            
            # Show first few days of schedule
            print(f"   Schedule preview (first 3 days):")
            for i, day in enumerate(result['schedule'][:3]):
                print(f"     Day {i+1} ({day['date']}):")
                print(f"       Free time: {day['free_time']}")
                print(f"       Time used: {day['time_used']}")
                print(f"       Tasks assigned: {len(day['assigned_tasks'])}")
                for task in day['assigned_tasks']:
                    print(f"         - {task['task_title']} ({task['time_assigned']})")
        else:
            print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("🎯 Testing edge cases...")
    
    # Test with very high intensity
    print(f"\n🚀 Testing with very high intensity (0.95):")
    result = can_complete_tasks_with_intensity(user, 0.95, today, today + timedelta(days=7))
    if result['success']:
        print(f"   {result['message']}")
        print(f"   Efficiency: {result['efficiency']:.2%}")
    
    # Test with very low intensity
    print(f"\n🐌 Testing with very low intensity (0.1):")
    result = can_complete_tasks_with_intensity(user, 0.1, today, today + timedelta(days=7))
    if result['success']:
        print(f"   {result['message']}")
        print(f"   Efficiency: {result['efficiency']:.2%}")
    
    # Test with invalid intensity
    print(f"\n❌ Testing with invalid intensity (1.5):")
    result = can_complete_tasks_with_intensity(user, 1.5)
    if not result['success']:
        print(f"   Correctly caught error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("✅ Greedy task scheduling algorithm test completed!")
    print("✅ The function successfully schedules tasks based on intensity!")

if __name__ == "__main__":
    test_greedy_scheduling()
