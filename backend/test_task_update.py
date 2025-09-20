#!/usr/bin/env python
"""
Test script for the update task by name functionality
Run this after starting the Django server
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_auth_session():
    """Get authenticated session"""
    session = requests.Session()
    
    # Login to get session cookie
    login_data = {
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD
    }
    
    response = session.post(f"{BASE_URL}/admin/login/", data=login_data)
    if response.status_code == 200:
        print("✓ Successfully authenticated")
        return session
    else:
        print("✗ Authentication failed")
        return None

def test_create_task(session):
    """Test creating a task"""
    print("\n=== Creating Test Task ===")
    
    task_data = {
        "title": "Complete project report",
        "description": "Write the quarterly project report",
        "T_n": "04:00:00",  # 4 hours
        "delta": 3,  # Medium priority
        "due_date": (datetime.now().date() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "due_time": "17:00:00",
        "completed_so_far": 0.0
    }
    
    response = session.post(f"{BASE_URL}/api/study/tasks/create/", json=task_data)
    if response.status_code == 201:
        data = response.json()
        print(f"✓ Created task: {data['task']['title']} (ID: {data['task']['id']})")
        return data['task']['title']
    else:
        print(f"✗ Failed to create task: {response.status_code}")
        print(f"  Error: {response.text}")
        return None

def test_update_task_by_name(session, task_name):
    """Test updating task by name"""
    print(f"\n=== Updating Task: {task_name} ===")
    
    # Test 1: Update completion percentage only
    print("1. Updating completion percentage to 50%...")
    update_data = {
        "task_name": task_name,
        "completed_so_far": 50.0
    }
    
    response = session.patch(f"{BASE_URL}/api/study/tasks/update-by-name/", json=update_data)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Updated: {data['message']}")
        print(f"  Updated fields: {', '.join(data['updated_fields'])}")
    else:
        print(f"✗ Failed to update: {response.status_code}")
        print(f"  Error: {response.text}")
    
    # Test 2: Update priority and due date
    print("\n2. Updating priority to 4 and due date...")
    update_data = {
        "task_name": task_name,
        "delta": 4,
        "due_date": (datetime.now().date() + timedelta(days=5)).strftime("%Y-%m-%d")
    }
    
    response = session.patch(f"{BASE_URL}/api/study/tasks/update-by-name/", json=update_data)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Updated: {data['message']}")
        print(f"  Updated fields: {', '.join(data['updated_fields'])}")
    else:
        print(f"✗ Failed to update: {response.status_code}")
        print(f"  Error: {response.text}")
    
    # Test 3: Update title and time needed
    print("\n3. Updating title and time needed...")
    update_data = {
        "task_name": task_name,
        "title": "Complete project report - URGENT",
        "T_n": "06:00:00"  # 6 hours
    }
    
    response = session.patch(f"{BASE_URL}/api/study/tasks/update-by-name/", json=update_data)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Updated: {data['message']}")
        print(f"  Updated fields: {', '.join(data['updated_fields'])}")
        return data['task']['title']  # Return new title
    else:
        print(f"✗ Failed to update: {response.status_code}")
        print(f"  Error: {response.text}")
        return task_name

def test_get_task_by_name(session, task_name):
    """Test getting task by name"""
    print(f"\n=== Getting Task: {task_name} ===")
    
    response = session.get(f"{BASE_URL}/api/study/tasks/get-by-name/?task_name={task_name}")
    if response.status_code == 200:
        data = response.json()
        task = data['task']
        print(f"✓ Retrieved task:")
        print(f"  Title: {task['title']}")
        print(f"  Description: {task['description']}")
        print(f"  Completion: {task['completed_so_far']}%")
        print(f"  Priority: {task['delta']}")
        print(f"  Due Date: {task['due_date']}")
        print(f"  Due Time: {task['due_time']}")
        print(f"  Time Needed: {task['T_n']}")
        print(f"  Is Completed: {task['is_completed']}")
    else:
        print(f"✗ Failed to get task: {response.status_code}")
        print(f"  Error: {response.text}")

def test_list_tasks(session):
    """Test listing all tasks"""
    print("\n=== Listing All Tasks ===")
    
    response = session.get(f"{BASE_URL}/api/study/tasks/")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {data['count']} tasks:")
        for task in data['tasks']:
            print(f"  - {task['title']} ({task['completed_so_far']}% complete, Priority: {task['delta']})")
    else:
        print(f"✗ Failed to list tasks: {response.status_code}")
        print(f"  Error: {response.text}")

def test_error_cases(session):
    """Test error cases"""
    print("\n=== Testing Error Cases ===")
    
    # Test 1: Update non-existent task
    print("1. Trying to update non-existent task...")
    update_data = {
        "task_name": "Non-existent task",
        "completed_so_far": 50.0
    }
    
    response = session.patch(f"{BASE_URL}/api/study/tasks/update-by-name/", json=update_data)
    if response.status_code == 400:
        data = response.json()
        print(f"✓ Correctly handled error: {data['error']}")
    else:
        print(f"✗ Expected error but got: {response.status_code}")
    
    # Test 2: Invalid completion percentage
    print("\n2. Trying invalid completion percentage...")
    update_data = {
        "task_name": "Complete project report - URGENT",
        "completed_so_far": 150.0  # Invalid: > 100
    }
    
    response = session.patch(f"{BASE_URL}/api/study/tasks/update-by-name/", json=update_data)
    if response.status_code == 400:
        data = response.json()
        print(f"✓ Correctly handled error: {data['error']}")
    else:
        print(f"✗ Expected error but got: {response.status_code}")

def main():
    """Main test function"""
    print("StudyBunny Task Update Test Script")
    print("=" * 40)
    
    # Get authenticated session
    session = get_auth_session()
    if not session:
        return
    
    # Create a test task
    task_name = test_create_task(session)
    if not task_name:
        return
    
    # Test updating the task
    new_task_name = test_update_task_by_name(session, task_name)
    
    # Test getting the updated task
    test_get_task_by_name(session, new_task_name)
    
    # Test listing all tasks
    test_list_tasks(session)
    
    # Test error cases
    test_error_cases(session)
    
    print("\n=== Test Complete ===")
    print("The update task by name functionality is working!")

if __name__ == "__main__":
    main()
