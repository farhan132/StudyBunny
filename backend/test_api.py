#!/usr/bin/env python
"""
Simple test script to verify StudyBunny API functionality
Run this after starting the Django server
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token for API requests"""
    # For now, we'll use session authentication
    # In production, you'd want to implement proper token authentication
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

def test_time_endpoints(session):
    """Test time-related API endpoints"""
    print("\n=== Testing Time Endpoints ===")
    
    # Test time today
    response = session.get(f"{BASE_URL}/api/core/time-today/")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Time today: {data['time_today_hours']:.2f} hours")
    else:
        print(f"✗ Time today failed: {response.status_code}")
    
    # Test free time today
    response = session.get(f"{BASE_URL}/api/core/free-time-today/")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Free time today: {data['free_today_hours']:.2f} hours")
    else:
        print(f"✗ Free time today failed: {response.status_code}")

def test_task_endpoints(session):
    """Test task-related API endpoints"""
    print("\n=== Testing Task Endpoints ===")
    
    # Create a test task
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "T_n": "02:00:00",  # 2 hours
        "delta": 3,  # Medium priority
        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "due_time": "17:00:00"
    }
    
    response = session.post(f"{BASE_URL}/api/study/tasks/", json=task_data)
    if response.status_code == 201:
        task = response.json()
        print(f"✓ Created task: {task['title']} (ID: {task['id']})")
        task_id = task['id']
        
        # Test updating task progress
        progress_data = {"completed_so_far": 50.0}
        response = session.patch(f"{BASE_URL}/api/study/tasks/{task_id}/progress/", json=progress_data)
        if response.status_code == 200:
            print("✓ Updated task progress to 50%")
        else:
            print(f"✗ Failed to update progress: {response.status_code}")
        
        # Test getting task statistics
        response = session.get(f"{BASE_URL}/api/study/tasks/statistics/")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Task statistics: {stats['total_tasks']} total tasks")
        else:
            print(f"✗ Failed to get statistics: {response.status_code}")
            
    else:
        print(f"✗ Failed to create task: {response.status_code}")

def test_daily_planning(session):
    """Test daily planning functionality"""
    print("\n=== Testing Daily Planning ===")
    
    # Generate daily plan
    plan_data = {"date": datetime.now().strftime("%Y-%m-%d")}
    response = session.post(f"{BASE_URL}/api/study/generate-daily-plan/", json=plan_data)
    if response.status_code == 200:
        plan = response.json()
        print(f"✓ Generated daily plan with {plan['tasks_scheduled']} tasks")
        print(f"  Free time available: {plan['free_time_available']}")
        print(f"  Total time allocated: {plan['total_time_allocated']}")
    else:
        print(f"✗ Failed to generate daily plan: {response.status_code}")

def main():
    """Main test function"""
    print("StudyBunny API Test Script")
    print("=" * 30)
    
    # Get authenticated session
    session = get_auth_token()
    if not session:
        return
    
    # Test all endpoints
    test_time_endpoints(session)
    test_task_endpoints(session)
    test_daily_planning(session)
    
    print("\n=== Test Complete ===")
    print("Note: Some skeleton functions return placeholder data.")
    print("Implement the actual logic in apps/core/time_utils.py")

if __name__ == "__main__":
    main()
