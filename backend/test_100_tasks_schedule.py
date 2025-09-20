#!/usr/bin/env python
"""
Test the 14-day schedule function with 100 tasks
"""
import os
import sys
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import get_14_day_schedule
from apps.study.models import Task
from datetime import datetime, timedelta, date, time
from django.utils import timezone

def create_100_tasks(user, start_date):
    """Create 100 tasks with varied due dates and times"""
    print("🏗️ Creating 100 diverse tasks...")
    
    # Clear existing tasks
    Task.objects.filter(user=user).delete()
    
    # Task templates with different characteristics
    task_templates = [
        # Quick tasks (15-60 minutes)
        {'base_time': 30, 'time_variance': 15, 'count': 20, 'priority_range': (3, 5)},
        # Medium tasks (1-3 hours)
        {'base_time': 90, 'time_variance': 60, 'count': 40, 'priority_range': (2, 4)},
        # Long tasks (3-8 hours)
        {'base_time': 300, 'time_variance': 180, 'count': 25, 'priority_range': (1, 3)},
        # Very long tasks (8+ hours)
        {'base_time': 600, 'time_variance': 240, 'count': 15, 'priority_range': (1, 2)},
    ]
    
    # Time slots throughout the day
    time_slots = [
        time(8, 0),   # 8:00 AM
        time(9, 30),  # 9:30 AM
        time(11, 0),  # 11:00 AM
        time(13, 0),  # 1:00 PM
        time(14, 30), # 2:30 PM
        time(16, 0),  # 4:00 PM
        time(17, 30), # 5:30 PM
        time(19, 0),  # 7:00 PM
        time(20, 30), # 8:30 PM
    ]
    
    # Task categories
    categories = [
        'Development', 'Testing', 'Documentation', 'Research', 'Meetings',
        'Code Review', 'Bug Fixes', 'Feature Work', 'Refactoring', 'Deployment',
        'Planning', 'Analysis', 'Design', 'Review', 'Optimization'
    ]
    
    # Task types
    task_types = [
        'Implement', 'Fix', 'Review', 'Test', 'Document', 'Research', 'Design',
        'Optimize', 'Refactor', 'Deploy', 'Plan', 'Analyze', 'Debug', 'Update'
    ]
    
    tasks_created = []
    
    for template in task_templates:
        for i in range(template['count']):
            # Generate random time within range
            time_minutes = max(15, template['base_time'] + random.randint(-template['time_variance'], template['time_variance']))
            task_time = timedelta(minutes=time_minutes)
            
            # Generate random priority
            priority = random.randint(template['priority_range'][0], template['priority_range'][1])
            
            # Generate random due date (spread over 30 days)
            days_ahead = random.randint(0, 29)
            due_date = start_date + timedelta(days=days_ahead)
            
            # Generate random due time
            due_time = random.choice(time_slots)
            
            # Generate random completion percentage (0-50% for most tasks)
            completion = random.uniform(0, 50) if random.random() < 0.8 else random.uniform(50, 90)
            
            # Generate task name and description
            category = random.choice(categories)
            task_type = random.choice(task_types)
            task_name = f"{task_type} {category} Task {i+1:03d}"
            description = f"{task_type.lower()} {category.lower()} - estimated {time_minutes} minutes"
            
            # Create task
            task = Task.objects.create(
                user=user,
                title=task_name,
                description=description,
                T_n=task_time,
                completed_so_far=completion,
                delta=priority,
                due_date=due_date,
                due_time=due_time
            )
            
            tasks_created.append(task)
    
    print(f"✅ Created {len(tasks_created)} tasks")
    return tasks_created

def analyze_task_distribution(tasks):
    """Analyze the distribution of created tasks"""
    print("\n📊 TASK DISTRIBUTION ANALYSIS:")
    print("-" * 50)
    
    # Priority distribution
    priority_counts = {}
    for task in tasks:
        priority_counts[task.delta] = priority_counts.get(task.delta, 0) + 1
    
    print("Priority Distribution:")
    for priority in sorted(priority_counts.keys()):
        priority_names = {1: 'Very Low', 2: 'Low', 3: 'Medium', 4: 'High', 5: 'Very High'}
        print(f"  {priority} ({priority_names[priority]}): {priority_counts[priority]} tasks")
    
    # Time distribution
    time_ranges = {
        'Quick (≤1h)': 0,
        'Medium (1-3h)': 0,
        'Long (3-8h)': 0,
        'Very Long (>8h)': 0
    }
    
    for task in tasks:
        hours = task.T_n.total_seconds() / 3600
        if hours <= 1:
            time_ranges['Quick (≤1h)'] += 1
        elif hours <= 3:
            time_ranges['Medium (1-3h)'] += 1
        elif hours <= 8:
            time_ranges['Long (3-8h)'] += 1
        else:
            time_ranges['Very Long (>8h)'] += 1
    
    print("\nTime Distribution:")
    for range_name, count in time_ranges.items():
        print(f"  {range_name}: {count} tasks")
    
    # Due date distribution
    due_dates = {}
    for task in tasks:
        due_dates[task.due_date] = due_dates.get(task.due_date, 0) + 1
    
    print(f"\nDue Date Distribution:")
    print(f"  Tasks due in next 7 days: {sum(1 for d, c in due_dates.items() if (d - timezone.now().date()).days <= 7)}")
    print(f"  Tasks due in next 14 days: {sum(1 for d, c in due_dates.items() if (d - timezone.now().date()).days <= 14)}")
    print(f"  Tasks due in next 30 days: {sum(1 for d, c in due_dates.items() if (d - timezone.now().date()).days <= 30)}")
    
    # Completion distribution
    completion_ranges = {
        'Not Started (0%)': 0,
        'Started (1-25%)': 0,
        'In Progress (26-50%)': 0,
        'Almost Done (51-90%)': 0,
        'Nearly Complete (91-99%)': 0
    }
    
    for task in tasks:
        completion = task.completed_so_far
        if completion == 0:
            completion_ranges['Not Started (0%)'] += 1
        elif completion <= 25:
            completion_ranges['Started (1-25%)'] += 1
        elif completion <= 50:
            completion_ranges['In Progress (26-50%)'] += 1
        elif completion <= 90:
            completion_ranges['Almost Done (51-90%)'] += 1
        else:
            completion_ranges['Nearly Complete (91-99%)'] += 1
    
    print("\nCompletion Distribution:")
    for range_name, count in completion_ranges.items():
        print(f"  {range_name}: {count} tasks")

def test_100_tasks_schedule():
    """Test the 14-day schedule function with 100 tasks"""
    print("🚀 TESTING 14-DAY SCHEDULE WITH 100 TASKS")
    print("=" * 80)
    
    # Get test user
    user = User.objects.get(username='testuser')
    today = timezone.now().date()
    
    # Create 100 tasks
    tasks = create_100_tasks(user, today)
    
    # Analyze task distribution
    analyze_task_distribution(tasks)
    
    print("\n" + "=" * 80)
    print("🗓️ GENERATING 14-DAY SCHEDULE")
    print("=" * 80)
    
    # Generate 14-day schedule
    result = get_14_day_schedule(user, start_date=today, max_intensity=0.9)
    
    if result['success']:
        print(f"\n✅ {result['message']}")
        print(f"\n📊 SCHEDULE SUMMARY:")
        print(f"   Start Date: {result['start_date']}")
        print(f"   End Date: {result['end_date']}")
        print(f"   Total Days: {result['total_days']}")
        print(f"   Tasks Scheduled: {result['total_tasks_scheduled']}")
        print(f"   Average Intensity: {result['intensity_used']:.3f}")
        print(f"   Completion Rate: {result['completion_analysis']['completion_rate']:.1%}")
        print(f"   Days with Tasks: {sum(1 for day in result['schedule'] if day)}/14")
        
        # Detailed day-by-day analysis
        print(f"\n📅 DAY-BY-DAY BREAKDOWN:")
        print("=" * 80)
        
        total_time_scheduled = timedelta()
        days_with_tasks = 0
        
        for day_index, day_schedule in enumerate(result['schedule']):
            current_date = result['start_date'] + timedelta(days=day_index)
            day_name = current_date.strftime('%A')
            
            if day_schedule:
                days_with_tasks += 1
                day_time = timedelta()
                
                print(f"\n📅 Day {day_index + 1:2d} - {current_date} ({day_name})")
                print("-" * 60)
                
                for i, task in enumerate(day_schedule, 1):
                    print(f"  {i:2d}. {task['task_title']}")
                    print(f"      ⏱️  Time: {task['time_allotted']}")
                    print(f"      🎯 Priority: {task['priority']}")
                    print(f"      📈 Progress: {task['completion_before']:.1f}% → {task['completion_after']:.1f}%")
                    if task.get('partial_completion'):
                        print(f"      ⚠️  Partial completion")
                    
                    if isinstance(task['time_allotted'], timedelta):
                        day_time += task['time_allotted']
                
                print(f"      📊 Total time: {day_time}")
                total_time_scheduled += day_time
            else:
                if day_index < 7:  # Only show first 7 days for brevity
                    print(f"\n📅 Day {day_index + 1:2d} - {current_date} ({day_name})")
                    print("-" * 60)
                    print("  🆓 No tasks scheduled - free day!")
        
        # Summary statistics
        print(f"\n📈 FINAL STATISTICS:")
        print("=" * 80)
        print(f"   Total Tasks Created: {len(tasks)}")
        print(f"   Tasks Scheduled: {result['total_tasks_scheduled']}")
        print(f"   Tasks Not Scheduled: {len(tasks) - result['total_tasks_scheduled']}")
        print(f"   Days with Tasks: {days_with_tasks}/14")
        print(f"   Days without Tasks: {14 - days_with_tasks}/14")
        print(f"   Total Time Scheduled: {total_time_scheduled}")
        print(f"   Average Time per Day: {total_time_scheduled / 14}")
        print(f"   Average Tasks per Day: {result['total_tasks_scheduled'] / 14:.1f}")
        print(f"   Completion Rate: {result['completion_analysis']['completion_rate']:.1%}")
        
        # Efficiency analysis
        if result['total_tasks_scheduled'] > 0:
            efficiency = result['total_tasks_scheduled'] / len(tasks) * 100
            print(f"   Scheduling Efficiency: {efficiency:.1f}%")
        
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print("✅ 100-TASK SCHEDULE TEST COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    test_100_tasks_schedule()
