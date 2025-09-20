#!/usr/bin/env python
"""
Test the 14-day schedule function
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import get_14_day_schedule
from apps.study.models import Task
from datetime import datetime, timedelta, date
from django.utils import timezone

def test_14_day_schedule():
    """Test the 14-day schedule function"""
    print("🗓️ TESTING 14-DAY SCHEDULE FUNCTION")
    print("=" * 80)
    
    # Get test user
    user = User.objects.get(username='testuser')
    today = timezone.now().date()
    
    # Clear existing tasks
    Task.objects.filter(user=user).delete()
    
    print("📋 Creating test tasks for 14-day schedule...")
    
    # Create a variety of tasks with different priorities and due dates
    test_tasks = [
        # High priority tasks due soon
        {
            'title': 'Urgent Bug Fix',
            'description': 'Fix critical bug in production',
            'T_n': timedelta(hours=2),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': today + timedelta(days=1),
            'due_time': datetime.strptime('18:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Client Meeting Prep',
            'description': 'Prepare for important client meeting',
            'T_n': timedelta(hours=3),
            'completed_so_far': 0.0,
            'delta': 5,  # Very High priority
            'due_date': today + timedelta(days=2),
            'due_time': datetime.strptime('14:00:00', '%H:%M:%S').time()
        },
        
        # Medium priority tasks
        {
            'title': 'Code Review',
            'description': 'Review team member code changes',
            'T_n': timedelta(hours=1, minutes=30),
            'completed_so_far': 0.0,
            'delta': 4,  # High priority
            'due_date': today + timedelta(days=3),
            'due_time': datetime.strptime('16:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Documentation Update',
            'description': 'Update project documentation',
            'T_n': timedelta(hours=2, minutes=30),
            'completed_so_far': 25.0,  # 25% completed
            'delta': 3,  # Medium priority
            'due_date': today + timedelta(days=5),
            'due_time': datetime.strptime('10:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Database Optimization',
            'description': 'Optimize database queries',
            'T_n': timedelta(hours=4),
            'completed_so_far': 0.0,
            'delta': 3,  # Medium priority
            'due_date': today + timedelta(days=7),
            'due_time': datetime.strptime('09:00:00', '%H:%M:%S').time()
        },
        
        # Low priority tasks
        {
            'title': 'UI Improvements',
            'description': 'Improve user interface design',
            'T_n': timedelta(hours=6),
            'completed_so_far': 0.0,
            'delta': 2,  # Low priority
            'due_date': today + timedelta(days=10),
            'due_time': datetime.strptime('11:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Research New Technology',
            'description': 'Research and evaluate new technology stack',
            'T_n': timedelta(hours=8),
            'completed_so_far': 0.0,
            'delta': 1,  # Very Low priority
            'due_date': today + timedelta(days=12),
            'due_time': datetime.strptime('13:00:00', '%H:%M:%S').time()
        },
        
        # Quick tasks
        {
            'title': 'Email Cleanup',
            'description': 'Clean up old emails',
            'T_n': timedelta(minutes=45),
            'completed_so_far': 0.0,
            'delta': 2,  # Low priority
            'due_date': today + timedelta(days=4),
            'due_time': datetime.strptime('15:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Backup Verification',
            'description': 'Verify system backups',
            'T_n': timedelta(hours=1),
            'completed_so_far': 0.0,
            'delta': 3,  # Medium priority
            'due_date': today + timedelta(days=6),
            'due_time': datetime.strptime('17:00:00', '%H:%M:%S').time()
        },
        {
            'title': 'Team Standup Notes',
            'description': 'Prepare standup meeting notes',
            'T_n': timedelta(minutes=30),
            'completed_so_far': 0.0,
            'delta': 4,  # High priority
            'due_date': today + timedelta(days=8),
            'due_time': datetime.strptime('09:30:00', '%H:%M:%S').time()
        }
    ]
    
    # Create tasks
    for task_data in test_tasks:
        Task.objects.create(user=user, **task_data)
    
    print(f"✅ Created {len(test_tasks)} test tasks")
    print("\n📋 Task Summary:")
    for task in Task.objects.filter(user=user, is_completed=False):
        print(f"  • {task.title} ({task.T_n}, Priority: {task.delta}, Due: {task.due_date})")
    
    print("\n" + "=" * 80)
    print("🚀 GENERATING 14-DAY SCHEDULE")
    print("=" * 80)
    
    # Generate 14-day schedule
    result = get_14_day_schedule(user, start_date=today, max_intensity=0.9)
    
    if result['success']:
        print(f"\n✅ {result['message']}")
        print(f"📊 Schedule Summary:")
        print(f"   Start Date: {result['start_date']}")
        print(f"   End Date: {result['end_date']}")
        print(f"   Total Days: {result['total_days']}")
        print(f"   Tasks Scheduled: {result['total_tasks_scheduled']}")
        print(f"   Average Intensity: {result['intensity_used']:.3f}")
        print(f"   Completion Rate: {result['completion_analysis']['completion_rate']:.1%}")
        
        print(f"\n📅 14-DAY SCHEDULE BREAKDOWN:")
        print("=" * 80)
        
        for day_index, day_schedule in enumerate(result['schedule']):
            current_date = result['start_date'] + timedelta(days=day_index)
            day_name = current_date.strftime('%A')
            
            if day_schedule:
                print(f"\n📅 Day {day_index + 1} - {current_date} ({day_name})")
                print("-" * 50)
                
                total_time = timedelta()
                for i, task in enumerate(day_schedule, 1):
                    print(f"  {i}. {task['task_title']}")
                    print(f"     ⏱️  Time: {task['time_allotted']}")
                    print(f"     🎯 Priority: {task['priority']}")
                    print(f"     📈 Progress: {task['completion_before']:.1f}% → {task['completion_after']:.1f}%")
                    if task.get('partial_completion'):
                        print(f"     ⚠️  Partial completion")
                    
                    if isinstance(task['time_allotted'], timedelta):
                        total_time += task['time_allotted']
                
                print(f"     📊 Total time: {total_time}")
            else:
                print(f"\n📅 Day {day_index + 1} - {current_date} ({day_name})")
                print("-" * 50)
                print("  🆓 No tasks scheduled - free day!")
        
        print(f"\n📈 COMPLETION ANALYSIS:")
        print(f"   Total Tasks: {result['completion_analysis']['total_tasks']}")
        print(f"   Completed: {result['completion_analysis']['completed_tasks']}")
        print(f"   Remaining: {result['completion_analysis']['remaining_tasks']}")
        print(f"   Completion Rate: {result['completion_analysis']['completion_rate']:.1%}")
        
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print("✅ 14-DAY SCHEDULE TEST COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    test_14_day_schedule()
