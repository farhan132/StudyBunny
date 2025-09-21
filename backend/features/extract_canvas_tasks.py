#!/usr/bin/env python
"""
Extract Canvas assignments and add them as tasks to the frontend
"""
import os
import sys
import django
import requests
from datetime import datetime, timedelta, date, time

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.models import Task

def extract_canvas_data():
    """Extract data directly from Canvas API"""
    canvas_token = "7867~GJxFLY3HMHGQRD6cHvVckvFQV2zBwN2nAtvTDJVMZBtuufeDvVrtymDGyvKEXayH"
    base_url = "https://canvas.instructure.com"
    
    headers = {
        'Authorization': f'Bearer {canvas_token}',
        'Content-Type': 'application/json'
    }
    
    print('🎯 Extracting Canvas data and adding tasks to frontend...')
    print('=' * 60)
    
    # Get courses
    print('📚 Fetching courses...')
    courses_response = requests.get(f"{base_url}/api/v1/courses", headers=headers, params={'enrollment_state': 'active'})
    courses = courses_response.json()
    print(f'Found {len(courses)} courses')
    
    # Get demo_user for frontend
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
    )
    print(f'Using user: {user.username} (created: {created})')
    
    # Clear existing tasks
    Task.objects.filter(user=user).delete()
    print('Cleared existing tasks')
    
    total_tasks = 0
    
    for course in courses:
        course_name = course.get('name', 'Unknown Course')
        course_code = course.get('course_code', 'Unknown')
        course_id = course.get('id')
        
        print(f'\n📝 Processing course: {course_name}')
        
        # Get assignments for this course
        assignments_response = requests.get(
            f"{base_url}/api/v1/courses/{course_id}/assignments", 
            headers=headers,
            params={'order_by': 'due_at'}
        )
        
        if assignments_response.status_code != 200:
            print(f'   ❌ Could not fetch assignments: {assignments_response.status_code}')
            continue
            
        assignments = assignments_response.json()
        print(f'   Found {len(assignments)} assignments')
        
        for assignment in assignments:
            due_at = assignment.get('due_at')
            if not due_at:
                continue  # Skip assignments without due dates
            
            try:
                # Parse due date
                due_datetime = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
                due_date = due_datetime.date()
                due_time = due_datetime.time()
                
                # Calculate priority based on due date
                days_until_due = (due_date - date.today()).days
                if days_until_due <= 1:
                    priority = 5  # Very high
                elif days_until_due <= 3:
                    priority = 4  # High
                elif days_until_due <= 7:
                    priority = 3  # Medium
                else:
                    priority = 2  # Low
                
                # Estimate time based on points
                points = assignment.get('points_possible', 10)
                estimated_hours = max(1, points / 10)  # 1 hour per 10 points
                
                # Create task
                task = Task.objects.create(
                    user=user,
                    title=f'{course_code}: {assignment.get("name", "Assignment")}',
                    description=f'Course: {course_name}\nPoints: {points}\nCanvas URL: {assignment.get("html_url", "")}',
                    T_n=timedelta(hours=estimated_hours),
                    completed_so_far=0.0,
                    delta=priority,
                    due_date=due_date,
                    due_time=due_time
                )
                
                total_tasks += 1
                print(f'   ✅ Added: {task.title} (Due: {task.due_date}, Priority: {task.delta})')
                
            except Exception as e:
                print(f'   ❌ Error adding {assignment.get("name", "Unknown")}: {e}')
    
    print(f'\n🎉 Successfully added {total_tasks} Canvas tasks to frontend!')
    
    # Show all tasks
    print('\n📋 Current tasks in database:')
    for task in Task.objects.filter(user=user).order_by('due_date'):
        print(f'   - {task.title}')
        print(f'     Due: {task.due_date} at {task.due_time}')
        print(f'     Priority: {task.delta}, Time: {task.T_n}')
        print()

if __name__ == "__main__":
    extract_canvas_data()
