#!/usr/bin/env python
"""
Test script for the initialize_tasks function
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import initialize_tasks

def test_initialize_tasks():
    """Test the initialize_tasks function"""
    print("🚀 TESTING INITIALIZE TASKS FUNCTION")
    print("=" * 80)
    
    # Get or create a test user
    try:
        user = User.objects.get(username='testuser')
        print(f"👤 Using existing user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"👤 Created new user: {user.username}")
    
    print("\n" + "=" * 80)
    print("🧪 TEST 1: Initialize with default sample tasks")
    print("=" * 80)
    
    # Test 1: Initialize with default sample tasks
    result1 = initialize_tasks(user, clear_existing=True)
    
    if result1['success']:
        print(f"✅ {result1['message']}")
        print(f"📊 Tasks created: {result1['tasks_created']}")
        print(f"🗑️ Tasks cleared: {result1['tasks_cleared']}")
    else:
        print(f"❌ Error: {result1['error']}")
    
    print("\n" + "=" * 80)
    print("🧪 TEST 2: Initialize with custom tasks")
    print("=" * 80)
    
    # Test 2: Initialize with custom tasks
    custom_tasks = [
        {
            'name': 'Custom Task 1',
            'description': 'This is a custom task for testing',
            'expected_time': timedelta(hours=1, minutes=30),
            'priority': 7,
            'due_date': datetime.now().date() + timedelta(days=3),
            'due_time': datetime.now().time().replace(hour=10, minute=0, second=0, microsecond=0),
            'completed_so_far': 0.0
        },
        {
            'name': 'Custom Task 2',
            'description': 'Another custom task',
            'expected_time': timedelta(minutes=45),
            'priority': 5,
            'due_date': datetime.now().date() + timedelta(days=5),
            'due_time': datetime.now().time().replace(hour=14, minute=30, second=0, microsecond=0),
            'completed_so_far': 0.0
        }
    ]
    
    result2 = initialize_tasks(user, clear_existing=True, sample_tasks=custom_tasks)
    
    if result2['success']:
        print(f"✅ {result2['message']}")
        print(f"📊 Tasks created: {result2['tasks_created']}")
        print(f"🗑️ Tasks cleared: {result2['tasks_cleared']}")
    else:
        print(f"❌ Error: {result2['error']}")
    
    print("\n" + "=" * 80)
    print("🧪 TEST 3: Initialize without clearing existing")
    print("=" * 80)
    
    # Test 3: Initialize without clearing existing tasks
    result3 = initialize_tasks(user, clear_existing=False)
    
    if result3['success']:
        print(f"✅ {result3['message']}")
        print(f"📊 Tasks created: {result3['tasks_created']}")
        print(f"🗑️ Tasks cleared: {result3['tasks_cleared']}")
    else:
        print(f"❌ Error: {result3['error']}")
    
    print("\n" + "=" * 80)
    print("🧪 TEST 4: Initialize with empty custom tasks")
    print("=" * 80)
    
    # Test 4: Initialize with empty custom tasks (should use defaults)
    result4 = initialize_tasks(user, clear_existing=True, sample_tasks=[])
    
    if result4['success']:
        print(f"✅ {result4['message']}")
        print(f"📊 Tasks created: {result4['tasks_created']}")
        print(f"🗑️ Tasks cleared: {result4['tasks_cleared']}")
    else:
        print(f"❌ Error: {result4['error']}")
    
    print("\n" + "=" * 80)
    print("📋 FINAL TASK COUNT")
    print("=" * 80)
    
    # Show final task count
    from apps.study.models import Task
    total_tasks = Task.objects.filter(owner=user).count()
    print(f"📊 Total tasks for user '{user.username}': {total_tasks}")
    
    # Show some task details
    tasks = Task.objects.filter(owner=user).order_by('due_date', 'due_time')[:5]
    print(f"\n📋 First 5 tasks:")
    for i, task in enumerate(tasks, 1):
        print(f"   {i}. {task.name}")
        print(f"      ⏱️  Time: {task.expected_time}")
        print(f"      🎯 Priority: {task.priority}")
        print(f"      📅 Due: {task.due_date} at {task.due_time}")
        print(f"      📈 Progress: {task.completed_so_far}%")
        print()
    
    print("=" * 80)
    print("✅ INITIALIZE TASKS TEST COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    test_initialize_tasks()
