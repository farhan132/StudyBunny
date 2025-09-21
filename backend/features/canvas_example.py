#!/usr/bin/env python
"""
Example usage of Canvas integration features
Run this to see how to use the Canvas integration
"""
import os
import sys
import django
from dotenv import load_dotenv

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

load_dotenv(os.path.join(backend_dir, '.env'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.models import Task
from features import (
    CanvasSync, 
    CanvasTaskConverter,
    CanvasConfig,
    CanvasAPIError
)


def example_basic_sync():
    """Example: Basic Canvas sync"""
    print("🎯 Example: Basic Canvas Sync")
    print("=" * 40)
    
    try:
        # Initialize Canvas sync
        canvas_sync = CanvasSync()
        
        # Get upcoming assignments
        upcoming = canvas_sync.get_upcoming_assignments(days_ahead=14)
        
        print(f"Found {len(upcoming)} upcoming assignments:")
        for course, assignment in upcoming[:5]:  # Show first 5
            print(f"  📚 {course.course_code}: {assignment.name}")
            print(f"     Due: {assignment.due_date}")
            print(f"     Points: {assignment.points_possible}")
            print()
            
    except CanvasAPIError as e:
        print(f"❌ Canvas API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_task_conversion():
    """Example: Convert Canvas assignments to StudyBunny tasks"""
    print("🔄 Example: Task Conversion")
    print("=" * 40)
    
    try:
        canvas_sync = CanvasSync()
        courses, assignments_by_course, groups_by_course = canvas_sync.get_all_course_data()
        
        converter = CanvasTaskConverter()
        studybunny_tasks = []
        
        for course in courses[:2]:  # Process first 2 courses
            assignments = assignments_by_course.get(course.id, [])
            groups = {g.id: g for g in groups_by_course.get(course.id, [])}
            
            print(f"📚 Course: {course.name} ({course.course_code})")
            
            for assignment in assignments[:3]:  # First 3 assignments
                assignment_group = groups.get(assignment.assignment_group_id)
                
                # Convert to StudyBunny task
                task = converter.convert_to_studybunny_task(
                    assignment, course, assignment_group
                )
                studybunny_tasks.append(task)
                
                print(f"  ✅ {task.title}")
                print(f"     Est. Time: {task.estimated_hours:.1f}h")
                print(f"     Priority: {task.priority}")
                print(f"     Due: {task.due_date}")
                print()
        
        print(f"🎉 Converted {len(studybunny_tasks)} assignments to tasks!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_create_demo_tasks():
    """Example: Actually create tasks in the database"""
    print("💾 Example: Create Demo Tasks")
    print("=" * 40)
    
    try:
        # Get or create demo user
        user, created = User.objects.get_or_create(
            username='canvas_demo_user',
            defaults={
                'email': 'canvas_demo@studybunny.com',
                'first_name': 'Canvas',
                'last_name': 'Demo'
            }
        )
        
        if created:
            print(f"✅ Created demo user: {user.username}")
        else:
            print(f"📝 Using existing user: {user.username}")
        
        # Get Canvas data and convert to tasks
        canvas_sync = CanvasSync()
        upcoming = canvas_sync.get_upcoming_assignments(days_ahead=7)
        
        converter = CanvasTaskConverter()
        created_tasks = 0
        
        for course, assignment in upcoming[:3]:  # Create first 3 tasks
            # Convert to StudyBunny task
            task_data = converter.convert_to_studybunny_task(assignment, course)
            
            # Check if task already exists
            existing = Task.objects.filter(
                user=user,
                title=task_data.title
            ).first()
            
            if not existing:
                # Create the task
                task = Task.objects.create(
                    user=user,
                    **task_data.to_dict()
                )
                created_tasks += 1
                print(f"✅ Created: {task.title}")
            else:
                print(f"⏭️  Skipped (exists): {task_data.title}")
        
        print(f"\n🎉 Created {created_tasks} new tasks!")
        print(f"📊 Total tasks for {user.username}: {Task.objects.filter(user=user).count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Canvas Integration Examples")
    print("=" * 50)
    print()
    
    # Check if API token is available
    try:
        token = CanvasConfig.get_api_token()
        print(f"✅ Canvas API token found: {token[:10]}...")
        print()
    except ValueError as e:
        print(f"❌ {e}")
        print("Please set CANVAS_API_TOKEN in your .env file")
        sys.exit(1)
    
    # Run examples
    example_basic_sync()
    print()
    
    example_task_conversion()
    print()
    
    example_create_demo_tasks()
    print()
    
    print("🏁 Examples complete!")
