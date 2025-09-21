#!/usr/bin/env python
"""
Test script for Canvas API integration
"""
import os
import sys
import django
from dotenv import load_dotenv

# Add the project directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from canvas import CanvasIntegrator, sync_canvas_homework
import json

def test_canvas_api_connection():
    """Test basic Canvas API connection"""
    print("🔍 Testing Canvas API Connection...")
    print("=" * 50)
    
    # Get API token from environment
    canvas_token = os.getenv('CANVAS_API_TOKEN')
    if not canvas_token:
        print("❌ CANVAS_API_TOKEN not found in environment variables")
        print("   Please add CANVAS_API_TOKEN to your .env file")
        return False
    
    print(f"✅ Found Canvas API token: {canvas_token[:10]}...")
    
    # Initialize Canvas integrator
    try:
        integrator = CanvasIntegrator(canvas_token)
        print("✅ Canvas integrator initialized successfully")
        return integrator
    except Exception as e:
        print(f"❌ Error initializing Canvas integrator: {e}")
        return False

def test_fetch_courses(integrator):
    """Test fetching courses from Canvas"""
    print("\n📚 Testing Course Fetching...")
    print("=" * 50)
    
    try:
        courses = integrator.fetch_all_courses()
        
        if not courses:
            print("⚠️  No courses found or API call failed")
            return []
        
        print(f"✅ Found {len(courses)} courses:")
        for i, course in enumerate(courses[:5]):  # Show first 5 courses
            print(f"   {i+1}. {course['name']} ({course['course_code']})")
            print(f"      Credit Hours: {course['credit_hours']}")
            print(f"      Students: {course['total_students']}")
            print(f"      Term: {course['term']}")
            print()
        
        if len(courses) > 5:
            print(f"   ... and {len(courses) - 5} more courses")
        
        return courses
        
    except Exception as e:
        print(f"❌ Error fetching courses: {e}")
        return []

def test_fetch_assignments(integrator, courses):
    """Test fetching assignments from Canvas"""
    print("\n📝 Testing Assignment Fetching...")
    print("=" * 50)
    
    if not courses:
        print("⚠️  No courses available to test assignments")
        return
    
    # Test with first course
    test_course = courses[0]
    print(f"Testing assignments for: {test_course['name']}")
    
    try:
        assignments = integrator.fetch_course_assignments(test_course['canvas_id'])
        
        if not assignments:
            print("⚠️  No assignments found for this course")
            return
        
        print(f"✅ Found {len(assignments)} assignments:")
        for i, assignment in enumerate(assignments[:3]):  # Show first 3 assignments
            print(f"   {i+1}. {assignment['title']}")
            print(f"      Due: {assignment['due_date']} at {assignment['due_time']}")
            print(f"      Points: {assignment['points_possible']}")
            print(f"      Group: {assignment['assignment_group']}")
            print(f"      Estimated Time: {assignment['estimated_time']}")
            print()
        
        if len(assignments) > 3:
            print(f"   ... and {len(assignments) - 3} more assignments")
            
    except Exception as e:
        print(f"❌ Error fetching assignments: {e}")

def test_full_sync():
    """Test full Canvas sync with StudyBunny"""
    print("\n🔄 Testing Full Canvas Sync...")
    print("=" * 50)
    
    # Get or create test user
    try:
        user, created = User.objects.get_or_create(
            username='canvas_test_user',
            defaults={
                'email': 'test@studybunny.com',
                'first_name': 'Canvas',
                'last_name': 'Tester'
            }
        )
        
        if created:
            print(f"✅ Created test user: {user.username}")
        else:
            print(f"✅ Using existing test user: {user.username}")
        
        # Get Canvas token from environment
        canvas_token = os.getenv('CANVAS_API_TOKEN')
        if not canvas_token:
            print("❌ CANVAS_API_TOKEN not found in environment")
            return
        
        # Run full sync
        print("🚀 Starting Canvas sync...")
        results = sync_canvas_homework(user, canvas_token)
        
        print("📊 Sync Results:")
        print(f"   Courses synced: {results['courses_synced']}")
        print(f"   Assignments synced: {results['assignments_synced']}")
        print(f"   Tasks created: {results['tasks_created']}")
        
        if results['errors']:
            print(f"   Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"      - {error}")
        else:
            print("   ✅ No errors!")
        
        # Show created tasks
        from apps.study.models import Task
        user_tasks = Task.objects.filter(user=user).order_by('-created_at')[:5]
        
        if user_tasks:
            print(f"\n📋 Recent tasks created for {user.username}:")
            for task in user_tasks:
                print(f"   - {task.title}")
                print(f"     Due: {task.due_date} | Priority: {task.delta} | Time: {task.T_n}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during full sync test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all Canvas integration tests"""
    print("🎯 StudyBunny Canvas Integration Test")
    print("=" * 60)
    
    # Test 1: API Connection
    integrator = test_canvas_api_connection()
    if not integrator:
        print("\n❌ Canvas API connection failed. Cannot proceed with further tests.")
        return
    
    # Test 2: Fetch Courses
    courses = test_fetch_courses(integrator)
    
    # Test 3: Fetch Assignments
    if courses:
        test_fetch_assignments(integrator, courses)
    
    # Test 4: Full Sync
    test_full_sync()
    
    print("\n🏁 Canvas Integration Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
