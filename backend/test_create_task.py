#!/usr/bin/env python
"""
Test script for the create_task function
"""

import os
import sys
import django
from datetime import datetime, timedelta, date

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import create_task

def test_create_task():
    """Test the create_task function"""
    print("🚀 TESTING CREATE TASK FUNCTION")
    print("=" * 60)
    
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
    
    print("\n" + "=" * 60)
    print("🧪 TEST 1: Create a basic task")
    print("=" * 60)
    
    # Test 1: Create a basic task
    result1 = create_task(
        user=user,
        name="Learn Python",
        priority=8,
        due_date=date(2025, 10, 15),
        expected_time=timedelta(hours=3, minutes=30),
        progress_so_far=25.0,
        description="Complete Python fundamentals course"
    )
    
    if result1['success']:
        print(f"✅ {result1['message']}")
        print(f"📊 Task ID: {result1['task_id']}")
    else:
        print(f"❌ Error: {result1['error']}")
    
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Create a task with minimal parameters")
    print("=" * 60)
    
    # Test 2: Create a task with minimal parameters
    result2 = create_task(
        user=user,
        name="Daily Exercise",
        priority=5,
        due_date=date(2025, 9, 25),
        expected_time=timedelta(minutes=45)
    )
    
    if result2['success']:
        print(f"✅ {result2['message']}")
        print(f"📊 Task ID: {result2['task_id']}")
    else:
        print(f"❌ Error: {result2['error']}")
    
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Test validation - invalid priority")
    print("=" * 60)
    
    # Test 3: Test validation - invalid priority
    result3 = create_task(
        user=user,
        name="Invalid Priority Task",
        priority=15,  # Invalid priority
        due_date=date(2025, 10, 1),
        expected_time=timedelta(hours=1)
    )
    
    if result3['success']:
        print(f"✅ {result3['message']}")
    else:
        print(f"❌ Expected Error: {result3['error']}")
    
    print("\n" + "=" * 60)
    print("🧪 TEST 4: Test validation - invalid progress")
    print("=" * 60)
    
    # Test 4: Test validation - invalid progress
    result4 = create_task(
        user=user,
        name="Invalid Progress Task",
        priority=7,
        due_date=date(2025, 10, 1),
        expected_time=timedelta(hours=2),
        progress_so_far=150.0  # Invalid progress
    )
    
    if result4['success']:
        print(f"✅ {result4['message']}")
    else:
        print(f"❌ Expected Error: {result4['error']}")
    
    print("\n" + "=" * 60)
    print("🧪 TEST 5: Test validation - empty name")
    print("=" * 60)
    
    # Test 5: Test validation - empty name
    result5 = create_task(
        user=user,
        name="",  # Empty name
        priority=5,
        due_date=date(2025, 10, 1),
        expected_time=timedelta(hours=1)
    )
    
    if result5['success']:
        print(f"✅ {result5['message']}")
    else:
        print(f"❌ Expected Error: {result5['error']}")
    
    print("\n" + "=" * 60)
    print("📋 FINAL TASK COUNT")
    print("=" * 60)
    
    # Show final task count
    from apps.study.models import Task
    total_tasks = Task.objects.filter(user=user).count()
    print(f"📊 Total tasks for user '{user.username}': {total_tasks}")
    
    # Show all tasks
    tasks = Task.objects.filter(user=user).order_by('-id')
    print(f"\n📋 All tasks:")
    for i, task in enumerate(tasks, 1):
        print(f"   {i}. {task.title}")
        print(f"      ⏱️  Time: {task.T_n}")
        print(f"      🎯 Priority: {task.delta}")
        print(f"      📅 Due: {task.due_date}")
        print(f"      📈 Progress: {task.completed_so_far}%")
        if task.description:
            print(f"      📝 Description: {task.description}")
        print()
    
    print("=" * 60)
    print("✅ CREATE TASK TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    test_create_task()
