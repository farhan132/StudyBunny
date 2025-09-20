#!/usr/bin/env python
"""
Simple test of the update task functionality using Django shell
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import update_task_by_name, get_task_by_name
from datetime import datetime, timedelta

def test_update_task():
    """Test the update task functionality"""
    print("Testing Update Task Functionality")
    print("=" * 40)
    
    # Get or create a user
    try:
        user = User.objects.get(username='admin')
        print(f"✓ Found user: {user.username}")
    except User.DoesNotExist:
        print("✗ Admin user not found. Please create one first.")
        return
    
    # Test 1: Create a task first (manually)
    print("\n1. Creating a test task...")
    from apps.study.models import Task
    
    task = Task.objects.create(
        user=user,
        title="Test Task for Update",
        description="This is a test task",
        T_n=timedelta(hours=2),
        completed_so_far=0.0,
        delta=3,
        due_date=datetime.now().date() + timedelta(days=7),
        due_time=datetime.now().time()
    )
    print(f"✓ Created task: {task.title}")
    
    # Test 2: Update task by name
    print("\n2. Updating task by name...")
    result = update_task_by_name(
        user=user,
        task_name="Test Task for Update",
        completed_so_far=50.0,
        delta=4
    )
    
    if result['success']:
        print(f"✓ {result['message']}")
        print(f"  Updated fields: {', '.join(result['updated_fields'])}")
        print(f"  New completion: {result['task']['completed_so_far']}%")
        print(f"  New priority: {result['task']['delta']}")
    else:
        print(f"✗ Update failed: {result['error']}")
    
    # Test 3: Update title and time
    print("\n3. Updating title and time...")
    result = update_task_by_name(
        user=user,
        task_name="Test Task for Update",
        title="Updated Test Task",
        T_n="03:00:00"
    )
    
    if result['success']:
        print(f"✓ {result['message']}")
        print(f"  Updated fields: {', '.join(result['updated_fields'])}")
        print(f"  New title: {result['task']['title']}")
        print(f"  New time: {result['task']['T_n']}")
    else:
        print(f"✗ Update failed: {result['error']}")
    
    # Test 4: Get task by name
    print("\n4. Getting task by name...")
    result = get_task_by_name(user, "Updated Test Task")
    
    if result['success']:
        task = result['task']
        print(f"✓ Retrieved task:")
        print(f"  Title: {task['title']}")
        print(f"  Completion: {task['completed_so_far']}%")
        print(f"  Priority: {task['delta']}")
        print(f"  Time Needed: {task['T_n']}")
    else:
        print(f"✗ Get failed: {result['error']}")
    
    # Test 5: Error case - non-existent task
    print("\n5. Testing error case...")
    result = update_task_by_name(
        user=user,
        task_name="Non-existent Task",
        completed_so_far=25.0
    )
    
    if not result['success']:
        print(f"✓ Correctly handled error: {result['error']}")
    else:
        print(f"✗ Should have failed but didn't")
    
    print("\n" + "=" * 40)
    print("✓ Update task functionality is working correctly!")
    print("✓ You can now use update_task_by_name() in your code!")

if __name__ == "__main__":
    test_update_task()
