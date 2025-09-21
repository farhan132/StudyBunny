"""
Task utility functions for StudyBunny
"""
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import Task
from apps.core.models import TimeCalculation
from apps.core.intensity import get_intensity_info
import math


def round_to_5_min_blocks(timedelta_obj, round_up=True):
    """
    Round a timedelta object to the nearest 5-minute block.
    
    Args:
        timedelta_obj: The timedelta object to round
        round_up (bool): If True, round up; if False, round down
    
    Returns:
        timedelta: Rounded timedelta object in 5-minute blocks
    """
    if not isinstance(timedelta_obj, timedelta):
        return timedelta_obj
    
    # Convert to total minutes
    total_minutes = timedelta_obj.total_seconds() / 60
    
    if round_up:
        # Round up to next 5-minute block
        rounded_minutes = math.ceil(total_minutes / 5) * 5
    else:
        # Round down to previous 5-minute block
        rounded_minutes = math.floor(total_minutes / 5) * 5
    
    # Convert back to timedelta
    return timedelta(minutes=rounded_minutes)


def update_task_by_name(user, task_name, **kwargs):
    """
    Update a task by its name with partial parameters
    
    Args:
        user: User instance (owner of the task)
        task_name (str): Name/title of the task to update
        **kwargs: Parameters to update (only provided parameters will be updated)
            - title: New title for the task
            - description: New description
            - T_n: Expected time needed (DurationField format: "HH:MM:SS")
            - completed_so_far: Completion percentage (0-100)
            - delta: Priority level (1-5)
            - due_date: Due date (YYYY-MM-DD format)
            - due_time: Due time (HH:MM:SS format)
    
    Returns:
        dict: Result with success status and task data or error message
    
    Example:
        result = update_task_by_name(
            user=request.user,
            task_name="Complete project report",
            completed_so_far=75.0,
            delta=4
        )
    """
    try:
        # Find the task by name for the specific user
        try:
            task = Task.objects.get(user=user, title=task_name)
        except Task.DoesNotExist:
            return {
                'success': False,
                'error': f'Task "{task_name}" not found for user {user.username}'
            }
        except Task.MultipleObjectsReturned:
            return {
                'success': False,
                'error': f'Multiple tasks found with name "{task_name}". Please be more specific.'
            }
        
        # Track what was updated
        updated_fields = []
        
        # Update title if provided
        if 'title' in kwargs and kwargs['title'] is not None:
            old_title = task.title
            task.title = kwargs['title']
            updated_fields.append(f'title: "{old_title}" -> "{task.title}"')
        
        # Update description if provided
        if 'description' in kwargs and kwargs['description'] is not None:
            task.description = kwargs['description']
            updated_fields.append('description')
        
        # Update T_n (expected time) if provided
        if 'T_n' in kwargs and kwargs['T_n'] is not None:
            try:
                if isinstance(kwargs['T_n'], str):
                    # Parse duration string (HH:MM:SS)
                    time_parts = kwargs['T_n'].split(':')
                    if len(time_parts) == 3:
                        hours, minutes, seconds = map(int, time_parts)
                        task.T_n = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    else:
                        return {
                            'success': False,
                            'error': 'T_n must be in HH:MM:SS format'
                        }
                else:
                    task.T_n = kwargs['T_n']
                updated_fields.append(f'T_n: {task.T_n}')
            except (ValueError, TypeError):
                return {
                    'success': False,
                    'error': 'Invalid T_n format. Use HH:MM:SS or timedelta object'
                }
        
        # Update completed_so_far if provided
        if 'completed_so_far' in kwargs and kwargs['completed_so_far'] is not None:
            try:
                completed = float(kwargs['completed_so_far'])
                if not 0.0 <= completed <= 100.0:
                    return {
                        'success': False,
                        'error': 'completed_so_far must be between 0.0 and 100.0'
                    }
                task.completed_so_far = completed
                updated_fields.append(f'completed_so_far: {completed}%')
            except (ValueError, TypeError):
                return {
                    'success': False,
                    'error': 'completed_so_far must be a number between 0.0 and 100.0'
                }
        
        # Update delta (priority) if provided
        if 'delta' in kwargs and kwargs['delta'] is not None:
            try:
                delta = int(kwargs['delta'])
                if not 1 <= delta <= 5:
                    return {
                        'success': False,
                        'error': 'delta must be between 1 and 5'
                    }
                task.delta = delta
                updated_fields.append(f'delta: {delta}')
            except (ValueError, TypeError):
                return {
                    'success': False,
                    'error': 'delta must be an integer between 1 and 5'
                }
        
        # Update due_date if provided
        if 'due_date' in kwargs and kwargs['due_date'] is not None:
            try:
                if isinstance(kwargs['due_date'], str):
                    task.due_date = datetime.strptime(kwargs['due_date'], '%Y-%m-%d').date()
                else:
                    task.due_date = kwargs['due_date']
                updated_fields.append(f'due_date: {task.due_date}')
            except (ValueError, TypeError):
                return {
                    'success': False,
                    'error': 'due_date must be in YYYY-MM-DD format or date object'
                }
        
        # Update due_time if provided
        if 'due_time' in kwargs and kwargs['due_time'] is not None:
            try:
                if isinstance(kwargs['due_time'], str):
                    task.due_time = datetime.strptime(kwargs['due_time'], '%H:%M:%S').time()
                else:
                    task.due_time = kwargs['due_time']
                updated_fields.append(f'due_time: {task.due_time}')
            except (ValueError, TypeError):
                return {
                    'success': False,
                    'error': 'due_time must be in HH:MM:SS format or time object'
                }
        
        # Save the task if any fields were updated
        if updated_fields:
            task.save()
            return {
                'success': True,
                'message': f'Task "{task_name}" updated successfully',
                'updated_fields': updated_fields,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'T_n': str(task.T_n),
                    'completed_so_far': task.completed_so_far,
                    'delta': task.delta,
                    'due_date': task.due_date.isoformat(),
                    'due_time': task.due_time.isoformat(),
                    'is_completed': task.is_completed,
                    'updated_at': task.updated_at.isoformat()
                }
            }
        else:
            return {
                'success': False,
                'error': 'No valid parameters provided for update'
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'An error occurred while updating task: {str(e)}'
        }


def get_task_by_name(user, task_name):
    """
    Get a task by its name for a specific user
    
    Args:
        user: User instance
        task_name (str): Name/title of the task
    
    Returns:
        dict: Task data or error message
    """
    try:
        task = Task.objects.get(user=user, title=task_name)
        return {
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'T_n': str(task.T_n),
                'completed_so_far': task.completed_so_far,
                'delta': task.delta,
                'due_date': task.due_date.isoformat(),
                'due_time': task.due_time.isoformat(),
                'is_completed': task.is_completed,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            }
        }
    except Task.DoesNotExist:
        return {
            'success': False,
            'error': f'Task "{task_name}" not found for user {user.username}'
        }
    except Task.MultipleObjectsReturned:
        return {
            'success': False,
            'error': f'Multiple tasks found with name "{task_name}". Please be more specific.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'An error occurred while retrieving task: {str(e)}'
        }


def can_complete_tasks_with_intensity_simulation(user, intensity_value, start_date=None, end_date=None):
    """
    Simulate the 14-day schedule to determine if all tasks can be completed.
    This function uses the same logic as the actual 14-day schedule.
    """
    try:
        # Set default dates if not provided
        if start_date is None:
            start_date = timezone.now().date()
        if end_date is None:
            end_date = start_date + timedelta(days=14)
        
        # Get all incomplete tasks for the user
        tasks = Task.objects.filter(
            user=user,
            is_completed=False
        ).order_by('due_date', 'due_time', '-delta')
        
        if not tasks.exists():
            return {
                'success': True,
                'can_complete': True,
                'total_tasks': 0,
                'completed_tasks': 0,
                'remaining_tasks': 0,
                'total_time_needed': '0:00:00',
                'total_time_available': '0:00:00',
                'schedule': [],
                'intensity_used': intensity_value,
                'efficiency': 1.0,
                'message': 'No tasks to complete'
            }
        
        # Calculate total time needed for all tasks
        total_time_needed = timedelta()
        for task in tasks:
            completion_percentage = task.completed_so_far / 100.0
            remaining_percentage = 1.0 - completion_percentage
            remaining_time = task.T_n * remaining_percentage
            total_time_needed += remaining_time
        
        # Simulate the 14-day schedule
        task_progress = {}
        for task in tasks:
            task_progress[task.id] = task.completed_so_far
        
        total_time_available = timedelta()
        completed_tasks_count = 0
        
        # Process each day for 14 days
        for day_index in range(14):
            current_date = start_date + timedelta(days=day_index)
            
            # Get free time for this day
            day_free_time = TimeCalculation.get_free_d(current_date, intensity_value=intensity_value)
            total_time_available += day_free_time
            
            # Get tasks that should be worked on this date (due on or after current date, within next 7 days)
            tasks_due_today = tasks.filter(
                due_date__gte=current_date,
                due_date__lte=current_date + timedelta(days=7)
            )
            
            print(f"   🔍 Tasks due on {current_date}: {tasks_due_today.count()}")
            for task in tasks_due_today:
                print(f"      • {task.title} (due: {task.due_date}, completed: {task.completed_so_far}%)")
            
            if not tasks_due_today.exists():
                print(f"   ⚠️  No tasks due on {current_date}, skipping...")
                current_date += timedelta(days=1)
                continue
            
            # Filter out tasks that are already complete
            incomplete_tasks = []
            for task in tasks_due_today:
                if task_progress.get(task.id, 0.0) < 100.0:
                    incomplete_tasks.append(task)
            
            if not incomplete_tasks:
                continue
            
            # Simulate daily scheduling
            remaining_time = day_free_time
            for task in incomplete_tasks:
                completion_percentage = task_progress.get(task.id, 0.0) / 100.0
                remaining_percentage = 1.0 - completion_percentage
                time_needed = task.T_n * remaining_percentage
                
                if time_needed <= remaining_time:
                    # Complete the task
                    task_progress[task.id] = 100.0
                    completed_tasks_count += 1
                    remaining_time -= time_needed
                else:
                    # Partial completion
                    if remaining_time > timedelta(minutes=30):
                        partial_completion = remaining_time / task.T_n * 100
                        task_progress[task.id] = min(100.0, task_progress.get(task.id, 0.0) + partial_completion)
                        remaining_time = timedelta()
                        break
        
        # Count completed tasks
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task_progress.get(task.id, 0.0) >= 100.0)
        remaining_tasks = total_tasks - completed_tasks
        
        # Calculate efficiency
        efficiency = 0.0
        if total_time_available.total_seconds() > 0:
            efficiency = min(1.0, total_time_needed.total_seconds() / total_time_available.total_seconds())
        
        # Determine if all tasks can be completed
        can_complete = remaining_tasks == 0
        
        return {
            'success': True,
            'can_complete': can_complete,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'remaining_tasks': remaining_tasks,
            'total_time_needed': str(total_time_needed),
            'total_time_available': str(total_time_available),
            'schedule': [],  # Not needed for simulation
            'intensity_used': intensity_value,
            'efficiency': efficiency,
            'message': f"Simulation: {completed_tasks}/{total_tasks} tasks can be completed with intensity {intensity_value:.3f}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'An error occurred during simulation: {str(e)}'
        }


def can_complete_tasks_with_intensity(user, intensity_value, start_date=None, end_date=None):
    """
    Determine if all remaining tasks can be completed within the given time frame
    using a greedy task scheduling algorithm based on the provided intensity value.
    
    Args:
        user: User instance (owner of the tasks)
        intensity_value (float): Intensity value between 0.0 and 1.0
        start_date (date, optional): Start date for scheduling (defaults to today)
        end_date (date, optional): End date for scheduling (defaults to 30 days from start)
    
    Returns:
        dict: Result containing completion status, schedule details, and analysis
            - success (bool): Whether all tasks can be completed
            - can_complete (bool): Same as success, for clarity
            - total_tasks (int): Number of tasks to complete
            - completed_tasks (int): Number of tasks that can be completed
            - remaining_tasks (int): Number of tasks that cannot be completed
            - total_time_needed (str): Total time needed for all tasks
            - total_time_available (str): Total time available in the period
            - schedule (list): Day-by-day schedule of task assignments
            - intensity_used (float): The intensity value used for calculations
            - efficiency (float): Time efficiency ratio (0.0 to 1.0)
            - message (str): Human-readable result message
    """
    try:
        # Validate intensity value
        if not 0.0 <= intensity_value <= 1.0:
            return {
                'success': False,
                'error': 'Intensity value must be between 0.0 and 1.0'
            }
        
        # Set default dates if not provided
        if start_date is None:
            start_date = timezone.now().date()
        if end_date is None:
            end_date = start_date + timedelta(days=30)
        
        # Get all incomplete tasks for the user
        tasks = Task.objects.filter(
            user=user,
            is_completed=False
        ).order_by('due_date', 'due_time', '-delta')  # Sort by due date/time, then by priority (high to low)
        
        if not tasks.exists():
            return {
                'success': True,
                'can_complete': True,
                'total_tasks': 0,
                'completed_tasks': 0,
                'remaining_tasks': 0,
                'total_time_needed': '0:00:00',
                'total_time_available': '0:00:00',
                'schedule': [],
                'intensity_used': intensity_value,
                'efficiency': 1.0,
                'message': 'No tasks to complete'
            }
        
        # Calculate total time needed for all tasks
        total_time_needed = timedelta()
        task_details = []
        
        for task in tasks:
            # Calculate remaining time needed for this task
            completion_percentage = task.completed_so_far / 100.0
            remaining_percentage = 1.0 - completion_percentage
            remaining_time = task.T_n * remaining_percentage
            
            total_time_needed += remaining_time
            task_details.append({
                'task': task,
                'remaining_time': remaining_time,
                'priority': task.delta,
                'due_datetime': datetime.combine(task.due_date, task.due_time),
                'completion_percentage': completion_percentage
            })
        
        # Greedy scheduling algorithm
        schedule = []
        current_date = start_date
        total_time_available = timedelta()
        completed_tasks_count = 0
        remaining_tasks_count = 0
        
        # Process each day from start_date to end_date
        while current_date <= end_date:
            # Calculate available free time for this day with the given intensity
            try:
                # Get free time for this day using the provided intensity value
                # Use user's timezone for today comparison
                user_today = timezone.now().astimezone(timezone.get_current_timezone()).date()
                if current_date == user_today:
                    # For today, use get_free_today with intensity parameter
                    day_free_time = TimeCalculation.get_free_today(intensity_value=intensity_value)
                    print(f"   📅 Today ({current_date}): {day_free_time:.2f} hours free time")
                else:
                    # For future days, use get_free_d with intensity parameter
                    day_free_time = TimeCalculation.get_free_d(current_date, intensity_value=intensity_value)
                    print(f"   📅 {current_date}: {day_free_time:.2f} hours free time")
            except ValueError as e:
                return {
                    'success': False,
                    'error': f'Invalid intensity value: {str(e)}'
                }
            
            total_time_available += day_free_time
            
            # Sort tasks by priority (high delta = high priority) and due date
            available_tasks = [td for td in task_details if not td.get('scheduled', False)]
            available_tasks.sort(key=lambda x: (-x['priority'], x['due_datetime']))
            
            # Greedily assign tasks to this day
            day_schedule = {
                'date': current_date,
                'free_time': day_free_time,
                'assigned_tasks': [],
                'time_used': timedelta(),
                'time_remaining': day_free_time
            }
            
            for task_detail in available_tasks:
                task = task_detail['task']
                remaining_time = task_detail['remaining_time']
                
                # Check if we can fit this task in today's free time
                if remaining_time <= day_schedule['time_remaining']:
                    # Assign the task to this day
                    day_schedule['assigned_tasks'].append({
                        'task_id': task.id,
                        'task_title': task.title,
                        'time_assigned': remaining_time,
                        'priority': task.delta,
                        'due_date': task.due_date,
                        'completion_before': task_detail['completion_percentage']
                    })
                    
                    day_schedule['time_used'] += remaining_time
                    day_schedule['time_remaining'] -= remaining_time
                    task_detail['scheduled'] = True
                    completed_tasks_count += 1
                    
                    # Mark task as completed in our simulation
                    task_detail['completion_percentage'] = 1.0
                else:
                    # Check if we can partially complete this task today
                    if day_schedule['time_remaining'] > timedelta(minutes=30):  # Minimum 30 minutes
                        partial_time = day_schedule['time_remaining']
                        partial_completion = partial_time / task.T_n
                        
                        day_schedule['assigned_tasks'].append({
                            'task_id': task.id,
                            'task_title': task.title,
                            'time_assigned': partial_time,
                            'priority': task.delta,
                            'due_date': task.due_date,
                            'completion_before': task_detail['completion_percentage'],
                            'partial_completion': True,
                            'new_completion': min(1.0, task_detail['completion_percentage'] + partial_completion)
                        })
                        
                        day_schedule['time_used'] += partial_time
                        day_schedule['time_remaining'] = timedelta()
                        task_detail['remaining_time'] -= partial_time
                        task_detail['completion_percentage'] += partial_completion
                        break  # No more time for this day
            
            schedule.append(day_schedule)
            current_date += timedelta(days=1)
        
        # Count remaining unscheduled tasks
        remaining_tasks_count = len([td for td in task_details if not td.get('scheduled', False)])
        
        # Calculate efficiency
        efficiency = 0.0
        if total_time_available.total_seconds() > 0:
            efficiency = min(1.0, total_time_needed.total_seconds() / total_time_available.total_seconds())
        
        # Determine if all tasks can be completed
        can_complete = remaining_tasks_count == 0
        
        # Generate result message
        if can_complete:
            message = f"✅ All {completed_tasks_count} tasks can be completed with intensity {intensity_value:.2f}"
        else:
            message = f"⚠️ Only {completed_tasks_count}/{completed_tasks_count + remaining_tasks_count} tasks can be completed with intensity {intensity_value:.2f}"
        
        return {
            'success': True,
            'can_complete': can_complete,
            'total_tasks': len(tasks),
            'completed_tasks': completed_tasks_count,
            'remaining_tasks': remaining_tasks_count,
            'total_time_needed': str(total_time_needed),
            'total_time_available': str(total_time_available),
            'schedule': schedule,
            'intensity_used': intensity_value,
            'efficiency': efficiency,
            'message': message
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'An error occurred during task scheduling: {str(e)}'
        }


def find_minimum_intensity_for_completion(user, start_date=None, end_date=None, precision=0.01, max_iterations=50):
    """
    Find the minimum intensity value needed to complete all tasks using get_optimal_daily_plan.
    
    This function uses binary search to efficiently find the lowest intensity value
    (between 0.0 and 1.0) that allows all tasks to be completed within the given time frame.
    
    Args:
        user: User instance (owner of the tasks)
        start_date (date, optional): Start date for scheduling (defaults to today)
        end_date (date, optional): End date for scheduling (defaults to 30 days from start)
        precision (float, optional): Search precision (defaults to 0.01)
        max_iterations (int, optional): Maximum number of binary search iterations (defaults to 50)
    
    Returns:
        dict: Result containing minimum intensity and analysis
            - success (bool): Whether the search completed successfully
            - minimum_intensity (float): The minimum intensity needed (or -1 if impossible)
            - can_complete_all (bool): Whether all tasks can be completed with this intensity
            - total_tasks (int): Number of tasks to complete
            - iterations_used (int): Number of binary search iterations performed
            - precision_achieved (float): Actual precision achieved
            - search_range (dict): The final search range [low, high]
            - schedule_analysis (dict): Detailed analysis of the final schedule
            - message (str): Human-readable result message
    """
    try:
        # Set default dates if not provided
        if start_date is None:
            start_date = timezone.now().date()
        if end_date is None:
            end_date = start_date + timedelta(days=30)
        
        # Check if there are any tasks to complete
        tasks = Task.objects.filter(user=user, is_completed=False)
        if not tasks.exists():
            return {
                'success': True,
                'minimum_intensity': 0.0,
                'can_complete_all': True,
                'total_tasks': 0,
                'iterations_used': 0,
                'precision_achieved': 0.0,
                'search_range': {'low': 0.0, 'high': 1.0},
                'schedule_analysis': None,
                'message': 'No tasks to complete - minimum intensity is 0.0'
            }
        
        # Binary search parameters
        low_intensity = 0.0
        high_intensity = 1.0
        minimum_intensity = -1.0
        iterations_used = 0
        
        # First, check if completion is possible at all (with intensity 1.0)
        can_complete_with_max = _test_completion_across_period(user, 1.0, start_date, end_date)
        if not can_complete_with_max:
            return {
                'success': True,
                'minimum_intensity': -1.0,
                'can_complete_all': False,
                'total_tasks': len(tasks),
                'iterations_used': 0,
                'precision_achieved': 0.0,
                'search_range': {'low': 0.0, 'high': 1.0},
                'schedule_analysis': None,
                'message': '❌ Impossible to complete all tasks even with maximum intensity (1.0)'
            }
        
        # Binary search for minimum intensity
        while high_intensity - low_intensity > precision and iterations_used < max_iterations:
            iterations_used += 1
            mid_intensity = (low_intensity + high_intensity) / 2.0
            
            # Test if we can complete all tasks with this intensity
            can_complete = _test_completion_across_period(user, mid_intensity, start_date, end_date)
            
            if can_complete:
                # We can complete all tasks with this intensity
                minimum_intensity = mid_intensity
                high_intensity = mid_intensity  # Try to find a lower intensity
            else:
                # We need higher intensity
                low_intensity = mid_intensity
        
        # Final verification with the found minimum intensity
        if minimum_intensity >= 0:
            can_complete_all = _test_completion_across_period(user, minimum_intensity, start_date, end_date)
            schedule_analysis = None  # We don't need detailed analysis for binary search
        else:
            # This shouldn't happen if we found that intensity 1.0 works
            can_complete_all = False
            schedule_analysis = None
        
        # Calculate actual precision achieved
        precision_achieved = high_intensity - low_intensity
        
        # Generate result message
        if minimum_intensity >= 0:
            if can_complete_all:
                message = f"✅ Minimum intensity needed: {minimum_intensity:.3f} (found in {iterations_used} iterations)"
            else:
                message = f"⚠️ Found intensity {minimum_intensity:.3f} but verification failed"
        else:
            message = "❌ Could not find a valid minimum intensity"
        
        return {
            'success': True,
            'minimum_intensity': minimum_intensity,
            'can_complete_all': can_complete_all,
            'total_tasks': len(tasks),
            'iterations_used': iterations_used,
            'precision_achieved': precision_achieved,
            'search_range': {'low': low_intensity, 'high': high_intensity},
            'schedule_analysis': schedule_analysis,
            'message': message
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'An error occurred during binary search: {str(e)}'
        }


def _test_completion_across_period(user, intensity, start_date, end_date):
    """
    Test if all tasks can be completed across the given period using the specified intensity.
    Uses get_optimal_daily_plan to simulate daily scheduling.
    """
    try:
        # Get all incomplete tasks
        tasks = Task.objects.filter(user=user, is_completed=False)
        if not tasks.exists():
            return True
        
        # Track task progress across the period
        task_progress = {}
        for task in tasks:
            task_progress[task.id] = task.completed_so_far
        
        # Test each day in the period
        current_date = start_date
        while current_date <= end_date:
            # Get tasks that should be worked on this date (due on or after current date, within next 7 days)
            tasks_due_today = tasks.filter(
                due_date__gte=current_date,
                due_date__lte=current_date + timedelta(days=7)
            )
            
            if tasks_due_today.exists():
                # Filter out tasks that are already complete
                incomplete_tasks = []
                for task in tasks_due_today:
                    if task_progress.get(task.id, 0.0) < 100.0:
                        incomplete_tasks.append(task)
                
                if incomplete_tasks:
                    # Test if we can schedule these tasks on this day
                    # We'll simulate by checking if there's enough free time
                    try:
                        # Use get_free_today for today (realistic remaining time) and get_free_d for future days
                        # Convert to user's timezone for accurate date comparison
                        import pytz
                        user_tz = pytz.timezone('America/Chicago')  # CDT timezone
                        user_now = timezone.now().astimezone(user_tz)
                        user_today = user_now.date()
                        
                        if current_date == user_today:
                            day_free_time = TimeCalculation.get_free_today(intensity_value=intensity)
                        else:
                            day_free_time = TimeCalculation.get_free_d(current_date, intensity_value=intensity)
                        
                        # Simulate task scheduling
                        remaining_time = day_free_time
                        for task in incomplete_tasks:
                            completion_percentage = task_progress.get(task.id, 0.0) / 100.0
                            remaining_percentage = 1.0 - completion_percentage
                            time_needed = task.T_n * remaining_percentage
                            
                            if time_needed <= remaining_time:
                                # Complete the task
                                task_progress[task.id] = 100.0
                                remaining_time -= time_needed
                            else:
                                # Partial completion
                                if remaining_time > timedelta(minutes=30):
                                    partial_completion = remaining_time / task.T_n * 100
                                    task_progress[task.id] = min(100.0, task_progress.get(task.id, 0.0) + partial_completion)
                                    remaining_time = timedelta()
                                    break
                    except Exception:
                        # If we can't calculate free time, assume we can't complete
                        return False
            
            current_date += timedelta(days=1)
        
        # Check if all tasks are completed
        all_completed = all(task_progress.get(task.id, 0.0) >= 100.0 for task in tasks)
        return all_completed
        
    except Exception:
        return False


def get_optimal_daily_plan(user, target_date=None, max_intensity=0.9):
    """
    Get optimal daily plan with intelligent task management.
    
    This function:
    1. Finds minimum intensity needed to complete all tasks
    2. If impossible (intensity > max_intensity), recommends tasks to remove
    3. Returns daily plan with tasks and time allocations, preferring plans with at least 2 tasks
    
    Args:
        user: User instance (owner of the tasks)
        target_date (date, optional): Date to generate plan for (defaults to today)
        max_intensity (float, optional): Maximum acceptable intensity (defaults to 0.9)
    
    Returns:
        dict: Comprehensive result containing:
            - success (bool): Whether the operation completed successfully
            - plan_type (str): 'complete_all', 'recommended_removal', or 'daily_plan'
            - minimum_intensity (float): Minimum intensity needed
            - can_complete_all (bool): Whether all tasks can be completed
            - daily_plan (list): List of tasks with time allocations for the day
            - recommended_removals (list): Tasks recommended for removal if impossible
            - intensity_used (float): Intensity used for the plan
            - total_time_allocated (str): Total time allocated for the day
            - tasks_count (int): Number of tasks in the plan
            - message (str): Human-readable result message
    """
    try:
        # Set default target date
        if target_date is None:
            target_date = timezone.now().date()
        
        # Step 1: Find minimum intensity needed to complete all tasks
        print(f"🔍 Finding minimum intensity for all tasks...")
        min_intensity_result = find_minimum_intensity_for_completion(
            user=user,
            start_date=target_date,
            end_date=target_date + timedelta(days=30)  # 30-day window
        )
        
        if not min_intensity_result['success']:
            return {
                'success': False,
                'error': f"Error finding minimum intensity: {min_intensity_result.get('error', 'Unknown error')}"
            }
        
        minimum_intensity = min_intensity_result['minimum_intensity']
        can_complete_all = min_intensity_result['can_complete_all']
        
        # Step 2: Check if completion is possible within acceptable intensity
        if minimum_intensity > max_intensity or not can_complete_all:
            print(f"⚠️ Cannot complete all tasks with intensity <= {max_intensity}")
            print(f"   Minimum intensity needed: {minimum_intensity:.3f}")
            
            # Find tasks to recommend for removal
            recommended_removals = _find_tasks_to_remove(user, max_intensity, target_date)
            
            return {
                'success': True,
                'plan_type': 'recommended_removal',
                'minimum_intensity': minimum_intensity,
                'can_complete_all': False,
                'daily_plan': [],
                'recommended_removals': recommended_removals,
                'intensity_used': max_intensity,
                'total_time_allocated': '0:00:00',
                'tasks_count': 0,
                'message': f"❌ Cannot complete all tasks. Minimum intensity needed: {minimum_intensity:.3f} (max allowed: {max_intensity})"
            }
        
        # Step 3: Generate daily plan with the minimum intensity
        print(f"✅ Can complete all tasks with intensity: {minimum_intensity:.3f}")
        
        # Try to find a plan with at least 2 tasks using the minimum intensity
        daily_plan = generate_daily_plan(
            user, target_date, minimum_intensity, min_tasks=2
        )
        
        # If we can't get 2 tasks with minimum intensity, try with a higher intensity
        if not daily_plan:
            print(f"⚠️ Cannot schedule 2+ tasks with minimum intensity {minimum_intensity:.3f}")
            print(f"   Trying with higher intensity to get 2+ tasks...")
            
            # Try with progressively higher intensities to get at least 2 tasks
            from apps.core.intensity import get_intensity
            global_intensity = get_intensity()
            
            # Create intensity range from global intensity to max_intensity
            intensity_steps = 10
            intensity_range = []
            for i in range(intensity_steps + 1):
                test_intensity = global_intensity + (max_intensity - global_intensity) * i / intensity_steps
                intensity_range.append(round(test_intensity, 2))
            
            for test_intensity in intensity_range:
                if test_intensity >= minimum_intensity and test_intensity <= max_intensity:
                    daily_plan = generate_daily_plan(
                        user, target_date, test_intensity, min_tasks=2
                    )
                    if daily_plan:
                        print(f"   ✅ Found plan with {len(daily_plan)} tasks using intensity {test_intensity:.3f}")
                        minimum_intensity = test_intensity  # Update the intensity used
                        break
        
        # Final fallback: try with any number of tasks
        if not daily_plan:
            print(f"   Fallback: trying with any number of tasks...")
            daily_plan = generate_daily_plan(
                user, target_date, minimum_intensity, min_tasks=1
            )
        
        # Calculate total time allocated
        total_time = timedelta()
        for task in daily_plan:
            if isinstance(task['time_allotted'], timedelta):
                total_time += task['time_allotted']
        
        return {
            'success': True,
            'plan_type': 'daily_plan',
            'minimum_intensity': minimum_intensity,
            'can_complete_all': True,
            'daily_plan': daily_plan,
            'recommended_removals': [],
            'intensity_used': minimum_intensity,
            'total_time_allocated': str(total_time),
            'tasks_count': len(daily_plan),
            'message': f"✅ Daily plan generated with {len(daily_plan)} tasks using intensity {minimum_intensity:.3f}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'An error occurred while generating optimal daily plan: {str(e)}'
        }


def _find_tasks_to_remove(user, max_intensity, target_date):
    """
    Find tasks to recommend for removal to achieve intensity <= max_intensity.
    
    Uses a greedy approach to remove tasks with lowest priority and highest time requirements.
    """
    try:
        # Get all incomplete tasks
        tasks = Task.objects.filter(user=user, is_completed=False).order_by('delta', '-T_n')
        
        if not tasks.exists():
            return []
        
        # Try removing tasks one by one until we can complete with acceptable intensity
        tasks_list = list(tasks)
        recommended_removals = []
        
        for i in range(len(tasks_list)):
            # Test if we can complete remaining tasks with max_intensity
            remaining_tasks = tasks_list[i:]
            
            # Temporarily mark removed tasks as completed for testing
            removed_task_ids = [task.id for task in tasks_list[:i]]
            Task.objects.filter(id__in=removed_task_ids).update(is_completed=True)
            
            try:
                # Test completion with remaining tasks
                result = can_complete_tasks_with_intensity(
                    user, max_intensity, target_date, target_date + timedelta(days=30)
                )
                
                if result['success'] and result['can_complete']:
                    # We can complete with this set of removals
                    recommended_removals = [
                        {
                            'task_id': task.id,
                            'title': task.title,
                            'priority': task.delta,
                            'time_needed': str(task.T_n),
                            'due_date': task.due_date,
                            'reason': f'Low priority ({task.delta}) and high time requirement ({task.T_n})'
                        }
                        for task in tasks_list[:i]
                    ]
                    break
                    
            finally:
                # Restore removed tasks
                Task.objects.filter(id__in=removed_task_ids).update(is_completed=False)
        
        return recommended_removals
        
    except Exception as e:
        print(f"Error finding tasks to remove: {e}")
        return []


def generate_daily_plan_for_tasks_with_progress(user, target_date, intensity, tasks_to_schedule, task_progress, min_tasks=2):
    """
    Generate daily plan with specific intensity for specific tasks, tracking progress across days.
    """
    try:
        # Get free time for the day with the given intensity
        from apps.core.models import TimeCalculation
        
        # Use get_free_d for all dates to ensure consistent behavior
        free_time = TimeCalculation.get_free_d(target_date, intensity_value=intensity)
        
        if not tasks_to_schedule:
            return []
        
        daily_plan = []
        remaining_time = free_time
        tasks_scheduled = 0
        
        for task in tasks_to_schedule:
            # Calculate remaining time needed for this task based on current progress
            completion_percentage = task_progress.get(task.id, 0.0) / 100.0
            remaining_percentage = 1.0 - completion_percentage
            time_needed = task.T_n * remaining_percentage
            
            # Check if we can fit this task in today's free time
            if time_needed <= remaining_time:
                # Allocate full time needed to complete this task
                new_progress = min(100.0, task_progress.get(task.id, 0.0) + (time_needed / task.T_n * 100))
                
                daily_plan.append({
                    'task_id': task.id,
                    'task_title': task.title,
                    'task_description': task.description,
                    'priority': task.delta,
                    'due_date': task.due_date,
                    'due_time': task.due_time,
                    'completion_before': task_progress.get(task.id, 0.0),
                    'time_allotted': time_needed,
                    'time_needed_total': str(task.T_n),
                    'completion_after': new_progress,
                    'start_time': timezone.now().time(),
                })
                
                remaining_time -= time_needed
                tasks_scheduled += 1
                
                # Update task progress for next day
                task_progress[task.id] = new_progress
                
                # If we have enough tasks and time is running low, we can stop
                if tasks_scheduled >= min_tasks and remaining_time < timedelta(minutes=30):
                    break
            else:
                # Check if we can partially complete this task
                if remaining_time > timedelta(minutes=30) and tasks_scheduled < min_tasks:
                    # Allocate remaining time to this task
                    partial_completion = remaining_time / task.T_n * 100
                    new_progress = min(100.0, task_progress.get(task.id, 0.0) + partial_completion)
                    
                    daily_plan.append({
                        'task_id': task.id,
                        'task_title': task.title,
                        'task_description': task.description,
                        'priority': task.delta,
                        'due_date': task.due_date,
                        'due_time': task.due_time,
                        'completion_before': task_progress.get(task.id, 0.0),
                        'time_allotted': remaining_time,
                        'time_needed_total': str(task.T_n),
                        'completion_after': new_progress,
                        'start_time': timezone.now().time(),
                        'partial_completion': True,
                    })
                    
                    # Update task progress for next day
                    task_progress[task.id] = new_progress
                    
                    remaining_time = timedelta()
                    tasks_scheduled += 1
                    break
        
        return daily_plan
        
    except Exception as e:
        print(f"Error generating daily plan: {e}")
        return []


def generate_daily_plan_for_tasks(user, target_date, intensity, tasks_to_schedule, min_tasks=2):
    """
    Generate daily plan with specific intensity for specific tasks.
    """
    try:
        # Get free time for the day with the given intensity
        from apps.core.models import TimeCalculation
        
        # Use get_free_d for all dates to ensure consistent behavior
        free_time = TimeCalculation.get_free_d(target_date, intensity_value=intensity)
        
        if not tasks_to_schedule:
            return []
        
        daily_plan = []
        remaining_time = free_time
        tasks_scheduled = 0
        
        for task in tasks_to_schedule:
            # Calculate remaining time needed for this task
            completion_percentage = task.completed_so_far / 100.0
            remaining_percentage = 1.0 - completion_percentage
            time_needed = task.T_n * remaining_percentage
            
            # Check if we can fit this task in today's free time
            if time_needed <= remaining_time:
                # Allocate full time needed to complete this task
                daily_plan.append({
                    'task_id': task.id,
                    'task_title': task.title,
                    'task_description': task.description,
                    'priority': task.delta,
                    'due_date': task.due_date,
                    'due_time': task.due_time,
                    'completion_before': task.completed_so_far,
                    'time_allotted': time_needed,
                    'time_needed_total': str(task.T_n),
                    'completion_after': min(100.0, task.completed_so_far + (time_needed / task.T_n * 100)),
                    'start_time': timezone.now().time(),  # Could be improved with actual scheduling
                })
                
                remaining_time -= time_needed
                tasks_scheduled += 1
                
                # If we have enough tasks and time is running low, we can stop
                if tasks_scheduled >= min_tasks and remaining_time < timedelta(minutes=30):
                    break
            else:
                # Check if we can partially complete this task
                if remaining_time > timedelta(minutes=30) and tasks_scheduled < min_tasks:
                    # Allocate remaining time to this task
                    daily_plan.append({
                        'task_id': task.id,
                        'task_title': task.title,
                        'task_description': task.description,
                        'priority': task.delta,
                        'due_date': task.due_date,
                        'due_time': task.due_time,
                        'completion_before': task.completed_so_far,
                        'time_allotted': remaining_time,
                        'time_needed_total': str(task.T_n),
                        'completion_after': min(100.0, task.completed_so_far + (remaining_time / task.T_n * 100)),
                        'start_time': timezone.now().time(),
                        'partial_completion': True,
                    })
                    
                    remaining_time = timedelta()
                    tasks_scheduled += 1
                    break
        
        return daily_plan
        
    except Exception as e:
        print(f"Error generating daily plan: {e}")
        return []


def generate_daily_plan(user, target_date, intensity, min_tasks=2):
    """
    Generate daily plan with specific intensity, preferring plans with at least min_tasks.
    """
    try:
        # Get free time for the day with the given intensity
        from apps.core.models import TimeCalculation
        
        # Use get_free_d for all dates to ensure consistent behavior
        free_time = TimeCalculation.get_free_d(target_date, intensity_value=intensity)
        
        # Get incomplete tasks sorted by priority and due date
        tasks = Task.objects.filter(
            user=user,
            is_completed=False
        ).order_by('due_date', 'due_time', '-delta')
        
        if not tasks.exists():
            return []
        
        daily_plan = []
        remaining_time = free_time
        tasks_scheduled = 0
        
        for task in tasks:
            # Calculate remaining time needed for this task
            completion_percentage = task.completed_so_far / 100.0
            remaining_percentage = 1.0 - completion_percentage
            time_needed = task.T_n * remaining_percentage
            
            # Check if we can fit this task in today's free time
            if time_needed <= remaining_time:
                # Allocate full time needed to complete this task
                daily_plan.append({
                    'task_id': task.id,
                    'task_title': task.title,
                    'task_description': task.description,
                    'priority': task.delta,
                    'due_date': task.due_date,
                    'due_time': task.due_time,
                    'completion_before': task.completed_so_far,
                    'time_allotted': time_needed,
                    'time_needed_total': str(task.T_n),
                    'completion_after': min(100.0, task.completed_so_far + (time_needed / task.T_n * 100)),
                    'start_time': timezone.now().time(),  # Could be improved with actual scheduling
                })
                
                remaining_time -= time_needed
                tasks_scheduled += 1
                
                # If we have enough tasks and time is running low, we can stop
                if tasks_scheduled >= min_tasks and remaining_time < timedelta(minutes=30):
                    break
            else:
                # Check if we can partially complete this task
                if remaining_time > timedelta(minutes=30) and tasks_scheduled < min_tasks:
                    # Allocate remaining time to this task
                    daily_plan.append({
                        'task_id': task.id,
                        'task_title': task.title,
                        'task_description': task.description,
                        'priority': task.delta,
                        'due_date': task.due_date,
                        'due_time': task.due_time,
                        'completion_before': task.completed_so_far,
                        'time_allotted': remaining_time,
                        'time_needed_total': str(task.T_n),
                        'completion_after': min(100.0, task.completed_so_far + (remaining_time / task.T_n * 100)),
                        'start_time': timezone.now().time(),
                        'partial_completion': True,
                    })
                    
                    remaining_time = timedelta()
                    tasks_scheduled += 1
                    break
        
        return daily_plan
        
    except Exception as e:
        print(f"Error generating daily plan: {e}")
        return []


def get_14_day_schedule(user, start_date=None, max_intensity=0.9):
    """
    Generate a 14-day task schedule using get_optimal_daily_plan for each day.
    
    Returns a list where:
    - Index 0: Tasks for remaining time today
    - Index 1: Tasks for tomorrow
    - Index 2: Tasks for day after tomorrow
    - ... and so on for 14 days
    
    Args:
        user: User instance (owner of the tasks)
        start_date (date, optional): Start date for scheduling (defaults to today)
        max_intensity (float, optional): Maximum acceptable intensity (defaults to 0.9)
    
    Returns:
        dict: Result containing:
            - success (bool): Whether the operation completed successfully
            - schedule (list): 14-day schedule, each day is a list of task assignments
            - total_days (int): Number of days in the schedule (14)
            - start_date (date): The start date of the schedule
            - end_date (date): The end date of the schedule
            - total_tasks_scheduled (int): Total number of tasks scheduled across all days
            - intensity_used (float): Average intensity used across all days
            - completion_analysis (dict): Analysis of task completion across the schedule
            - message (str): Human-readable result message
    """
    try:
        # Set default start date to user's timezone
        if start_date is None:
            import pytz
            user_tz = pytz.timezone('America/Chicago')  # CDT timezone
            user_now = timezone.now().astimezone(user_tz)
            start_date = user_now.date()
        
        end_date = start_date + timedelta(days=13)  # 14 days total (0-13)
        
        print(f"🗓️ Generating 14-day schedule from {start_date} to {end_date}")
        
        # Get all incomplete tasks
        all_tasks = Task.objects.filter(
            user=user,
            is_completed=False
        ).order_by('due_date', 'due_time', '-delta')
        
        if not all_tasks.exists():
            return {
                'success': True,
                'schedule': [[] for _ in range(14)],
                'total_days': 14,
                'start_date': start_date,
                'end_date': end_date,
                'total_tasks_scheduled': 0,
                'intensity_used': 0.0,
                'completion_analysis': {
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'remaining_tasks': 0,
                    'completion_rate': 1.0
                },
                'message': 'No tasks to schedule - empty 14-day schedule generated'
            }
        
        # Convert tasks to a list for processing
        tasks_list = list(all_tasks)
        
        # Mark tasks past due date as completed (100% progress)
        today = timezone.now().date()
        for task in tasks_list:
            if task.due_date < today and not task.is_completed:
                print(f"📅 Task '{task.title}' is past due ({task.due_date}), marking as completed")
                task.completed_so_far = 100.0
                task.is_completed = True
                task.save()
        
        # Filter out completed tasks for scheduling
        incomplete_tasks = [task for task in tasks_list if not task.is_completed]
        print(f"📊 Total tasks: {len(tasks_list)}, Incomplete tasks: {len(incomplete_tasks)}")
        
        schedule = [[] for _ in range(14)]  # 14 empty days
        total_tasks_scheduled = 0
        intensity_values = []
        
        # Use binary search to find minimum intensity needed for incomplete tasks only
        if incomplete_tasks:
            print(f"🔍 Finding minimum intensity for {len(incomplete_tasks)} incomplete tasks...")
            # Find the latest due date among incomplete tasks
            latest_due_date = max(task.due_date for task in incomplete_tasks)
            print(f"Latest due date: {latest_due_date}")
            
            min_intensity_result = find_minimum_intensity_for_completion(
                user=user,
                start_date=start_date,
                end_date=latest_due_date  # Use actual task deadlines, not fixed 14 days
            )
        else:
            print(f"✅ All tasks are completed, no minimum intensity needed")
            min_intensity_result = {
                'success': True,
                'minimum_intensity': 0.0,
                'can_complete_all': True,
                'total_tasks': len(tasks_list),
                'iterations_used': 0,
                'precision_achieved': 0.0,
                'search_range': {'low': 0.0, 'high': 0.0},
                'schedule_analysis': None,
                'message': 'All tasks completed - minimum intensity is 0.0'
            }
        
        if not min_intensity_result['success']:
            print(f"❌ Error finding minimum intensity: {min_intensity_result.get('error', 'Unknown')}")
            return {
                'success': False,
                'error': f"Error finding minimum intensity: {min_intensity_result.get('error', 'Unknown')}"
            }
        
        minimum_intensity = min_intensity_result['minimum_intensity']
        true_minimum_required_intensity = minimum_intensity  # Store the true minimum required intensity before any modifications
        print(f"✅ Minimum intensity found: {minimum_intensity:.3f}")

        # Use current global intensity if it's higher than minimum required
        intensity_info = get_intensity_info()
        current_intensity = intensity_info['intensityXcap']  # Use the calculated intensity cap
        minimum_intensity = max(minimum_intensity, current_intensity)
        
        # Track task progress across the 14-day schedule
        task_progress = {}
        for task in tasks_list:
            task_progress[task.id] = task.completed_so_far
        
        # Process each day using the exact same algorithm as binary search
        for day_index in range(14):
            current_date = start_date + timedelta(days=day_index)
            print(f"📅 Processing day {day_index + 1}: {current_date}")
            
            # For 14-day schedule, we want to distribute tasks across all 14 days
            # Get all incomplete tasks that are due on or after this date
            day_incomplete_tasks = []
            for task in incomplete_tasks:
                if task_progress.get(task.id, 0.0) < 100.0 and task.due_date >= current_date:
                    day_incomplete_tasks.append(task)
            
            print(f"   🔍 Incomplete tasks: {len(day_incomplete_tasks)}")
            for task in day_incomplete_tasks:
                print(f"      • {task.title} (due: {task.due_date}, progress: {task_progress.get(task.id, 0.0):.1f}%)")
            
            if not day_incomplete_tasks:
                print(f"   ⚠️ No incomplete tasks to schedule for {current_date}")
                intensity_values.append(0.0)
                continue
            
            try:
                # Use get_free_today for today (realistic remaining time) and get_free_d for future days
                # Convert to user's timezone for accurate date comparison
                import pytz
                user_tz = pytz.timezone('America/Chicago')  # CDT timezone
                user_now = timezone.now().astimezone(user_tz)
                user_today = user_now.date()
                
                if current_date == user_today:
                    day_free_time = TimeCalculation.get_free_today(intensity_value=minimum_intensity)
                else:
                    day_free_time = TimeCalculation.get_free_d(current_date, intensity_value=minimum_intensity)
                
                # Simulate task scheduling using the same logic as binary search
                remaining_time = day_free_time
                daily_plan = []
                
                for task in day_incomplete_tasks:
                    completion_percentage = task_progress.get(task.id, 0.0) / 100.0
                    remaining_percentage = 1.0 - completion_percentage
                    time_needed = task.T_n * remaining_percentage
                    
                    if time_needed <= remaining_time:
                        # Complete the task
                        new_progress = 100.0
                        daily_plan.append({
                            'task_id': task.id,
                            'task_title': task.title,
                            'task_description': task.description,
                            'priority': task.delta,
                            'due_date': task.due_date,
                            'due_time': task.due_time,
                            'completion_before': task_progress.get(task.id, 0.0),
                            'time_allotted': time_needed,
                            'time_needed_total': str(task.T_n),
                            'completion_after': new_progress,
                            'start_time': timezone.now().time(),
                        })
                        
                        remaining_time -= time_needed
                        task_progress[task.id] = new_progress
                        
                    else:
                        # Partial completion - schedule work if there's any meaningful time left
                        if remaining_time > timedelta(minutes=15):
                            current_progress = task_progress.get(task.id, 0.0)
                            partial_completion = remaining_time / task.T_n * 100
                            new_progress = min(100.0, current_progress + partial_completion)
                            
                            daily_plan.append({
                                'task_id': task.id,
                                'task_title': task.title,
                                'task_description': task.description,
                                'priority': task.delta,
                                'due_date': task.due_date,
                                'due_time': task.due_time,
                                'completion_before': current_progress,
                                'time_allotted': remaining_time,
                                'time_needed_total': str(task.T_n),
                                'completion_after': new_progress,
                                'start_time': timezone.now().time(),
                                'partial_completion': True,
                            })
                            
                            task_progress[task.id] = new_progress
                            remaining_time = timedelta()
                            break
                
                if daily_plan:
                    schedule[day_index] = daily_plan
                    total_tasks_scheduled += len(daily_plan)
                    intensity_values.append(minimum_intensity)
                    
                    print(f"   ✅ Scheduled {len(daily_plan)} tasks with intensity {minimum_intensity:.3f}")
                    
                    # Show what was scheduled
                    for task in daily_plan:
                        print(f"      • {task['task_title']} ({task['time_allotted']}) - Progress: {task['completion_after']:.1f}%")
                    
                else:
                    print(f"   ⚠️ No tasks scheduled for {current_date}")
                    intensity_values.append(0.0)
                    
            except Exception as e:
                print(f"   ❌ Error processing day {current_date}: {e}")
                intensity_values.append(0.0)
        
        
        # No need to restore task progress since we're not modifying task completion status
        
        # Calculate completion analysis
        scheduled_task_ids = set()
        for day_schedule in schedule:
            for task in day_schedule:
                scheduled_task_ids.add(task['task_id'])

        total_tasks = len(tasks_list)
        scheduled_tasks = len(scheduled_task_ids)
        remaining_tasks = total_tasks - scheduled_tasks
        completion_rate = scheduled_tasks / total_tasks if total_tasks > 0 else 1.0
        
        # Tasks remain in their original completion status
        
        # Calculate average intensity
        avg_intensity = sum(intensity_values) / len(intensity_values) if intensity_values else 0.0
        
        # Generate summary
        print(f"\n📊 14-DAY SCHEDULE SUMMARY:")
        print(f"   Total tasks scheduled: {total_tasks_scheduled}")
        print(f"   Tasks scheduled: {scheduled_tasks}/{total_tasks} ({completion_rate:.1%})")
        print(f"   Average intensity: {avg_intensity:.3f}")
        print(f"   Days with tasks: {sum(1 for day in schedule if day)}/14")
        
        return {
            'success': True,
            'schedule': schedule,
            'total_days': 14,
            'start_date': start_date,
            'end_date': end_date,
            'total_tasks_scheduled': total_tasks_scheduled,
            'intensity_used': avg_intensity,
            'minimum_required_intensity': true_minimum_required_intensity,  # Use the true minimum required intensity
            'intensity_used_for_scheduling': minimum_intensity,  # The intensity actually used for scheduling
            'completion_analysis': {
                'total_tasks': total_tasks,
                'completed_tasks': scheduled_tasks,
                'remaining_tasks': remaining_tasks,
                'completion_rate': completion_rate
            },
            'message': f"✅ 14-day schedule generated with {total_tasks_scheduled} tasks scheduled across {sum(1 for day in schedule if day)} days"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'An error occurred while generating 14-day schedule: {str(e)}'
        }


def create_task(user, name, priority, due_date, expected_time, progress_so_far=0.0, description=""):
    """
    Create a new task and save it to the database.
    
    Args:
        user: User instance (owner of the task)
        name (str): Name of the task
        priority (int): Priority of the task (1-10)
        due_date (date): Due date of the task
        expected_time (timedelta): Expected time to complete the task
        progress_so_far (float, optional): Progress percentage (0.0-100.0, defaults to 0.0)
        description (str, optional): Description of the task (defaults to empty string)
    
    Returns:
        dict: Result containing:
            - success (bool): Whether the operation completed successfully
            - task_id (int): ID of the created task (if successful)
            - message (str): Human-readable result message
    """
    try:
        from .models import Task
        from datetime import datetime
        
        # Validate inputs
        if not name or not name.strip():
            return {
                'success': False,
                'error': 'Task name cannot be empty'
            }
        
        if not (1 <= priority <= 10):
            return {
                'success': False,
                'error': 'Priority must be between 1 and 10'
            }
        
        if not (0.0 <= progress_so_far <= 100.0):
            return {
                'success': False,
                'error': 'Progress must be between 0.0 and 100.0'
            }
        
        # Create the task
        task = Task.objects.create(
            user=user,
            title=name.strip(),
            description=description.strip(),
            T_n=expected_time,
            delta=priority,
            due_date=due_date,
            due_time=datetime.now().time(),  # Default to current time
            completed_so_far=progress_so_far
        )
        
        return {
            'success': True,
            'task_id': task.id,
            'message': f"✅ Task '{name}' created successfully with ID {task.id}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'An error occurred while creating task: {str(e)}'
        }


def get_tasks_for_date(user, target_date, max_intensity=0.9):
    """
    Get tasks scheduled for a specific date by generating a 14-day schedule.
    
    This function generates a 14-day schedule starting from today and returns
    the tasks scheduled for the target date within that schedule.
    
    Args:
        user: User instance (owner of the tasks)
        target_date (date): The date to get tasks for
        max_intensity (float, optional): Maximum acceptable intensity (defaults to 0.9)
    
    Returns:
        dict: Result containing:
            - success (bool): Whether the operation completed successfully
            - target_date (date): The date requested
            - tasks (list): List of tasks scheduled for the target date
            - total_tasks (int): Number of tasks scheduled for the date
            - total_time (str): Total time allocated for the date
            - intensity_used (float): Intensity used for the date
            - schedule_info (dict): Information about the full 14-day schedule
            - message (str): Human-readable result message
    """
    try:
        print(f"📅 Getting tasks for {target_date}")
        
        # Generate 14-day schedule starting from today
        today = timezone.now().date()
        schedule_result = get_14_day_schedule(user, start_date=today, max_intensity=max_intensity)
        
        if not schedule_result['success']:
            return {
                'success': False,
                'error': f"Error generating 14-day schedule: {schedule_result.get('error', 'Unknown error')}"
            }
        
        # Calculate the day index for the target date
        days_difference = (target_date - today).days
        
        # Check if target date is within the 14-day schedule
        if days_difference < 0 or days_difference >= 14:
            return {
                'success': True,
                'target_date': target_date,
                'tasks': [],
                'total_tasks': 0,
                'total_time': '0:00:00',
                'intensity_used': 0.0,
                'schedule_info': {
                    'start_date': schedule_result['start_date'],
                    'end_date': schedule_result['end_date'],
                    'total_tasks_scheduled': schedule_result['total_tasks_scheduled'],
                    'completion_rate': schedule_result['completion_analysis']['completion_rate']
                },
                'message': f"📅 Target date {target_date} is outside the 14-day schedule range ({today} to {today + timedelta(days=13)})"
            }
        
        # Get tasks for the target date (using the calculated day index)
        day_tasks = schedule_result['schedule'][days_difference] if schedule_result['schedule'] else []
        
        # Calculate total time for the day
        total_time = timedelta()
        for task in day_tasks:
            if isinstance(task.get('time_allotted'), timedelta):
                total_time += task['time_allotted']
        
        # Get intensity used for the day (we'll use the average from the schedule)
        intensity_used = schedule_result['intensity_used']
        
        # Format the response
        if day_tasks:
            message = f"✅ Found {len(day_tasks)} tasks scheduled for {target_date}"
        else:
            message = f"📅 No tasks scheduled for {target_date} - it's a free day!"
        
        return {
            'success': True,
            'target_date': target_date,
            'tasks': day_tasks,
            'total_tasks': len(day_tasks),
            'total_time': str(total_time),
            'intensity_used': intensity_used,
            'schedule_info': {
                'start_date': schedule_result['start_date'],
                'end_date': schedule_result['end_date'],
                'total_tasks_scheduled': schedule_result['total_tasks_scheduled'],
                'completion_rate': schedule_result['completion_analysis']['completion_rate']
            },
            'message': message
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'An error occurred while getting tasks for date: {str(e)}'
        }


def get_tasks_for_date_with_rounding(user, target_date, max_intensity=0.9, round_to_5min=True):
    """
    Get tasks scheduled for a specific date with optional 5-minute rounding.
    
    This function generates a 14-day schedule starting from today and returns
    the tasks scheduled for the target date within that schedule, with optional
    time rounding to 5-minute blocks.
    
    Args:
        user: User instance (owner of the tasks)
        target_date (date): The date to get tasks for
        max_intensity (float, optional): Maximum acceptable intensity (defaults to 0.9)
        round_to_5min (bool, optional): Whether to round times to 5-minute blocks (defaults to True)
    
    Returns:
        dict: Result containing:
            - success (bool): Whether the operation completed successfully
            - target_date (date): The date requested
            - tasks (list): List of tasks scheduled for the target date (with rounded times if requested)
            - total_tasks (int): Number of tasks scheduled for the date
            - total_time (str): Total time allocated for the date (rounded if requested)
            - total_time_original (str): Original total time before rounding
            - intensity_used (float): Intensity used for the date
            - schedule_info (dict): Information about the full 14-day schedule
            - message (str): Human-readable result message
    """
    try:
        print(f"📅 Getting tasks for {target_date} (rounding: {'enabled' if round_to_5min else 'disabled'})")
        
        # Generate 14-day schedule starting from today
        today = timezone.now().date()
        schedule_result = get_14_day_schedule(user, start_date=today, max_intensity=max_intensity)
        
        if not schedule_result['success']:
            return {
                'success': False,
                'error': f"Error generating 14-day schedule: {schedule_result.get('error', 'Unknown error')}"
            }
        
        # Calculate the day index for the target date
        days_difference = (target_date - today).days
        
        # Check if target date is within the 14-day schedule
        if days_difference < 0 or days_difference >= 14:
            return {
                'success': True,
                'target_date': target_date,
                'tasks': [],
                'total_tasks': 0,
                'total_time': '0:00:00',
                'intensity_used': 0.0,
                'schedule_info': {
                    'start_date': schedule_result['start_date'],
                    'end_date': schedule_result['end_date'],
                    'total_tasks_scheduled': schedule_result['total_tasks_scheduled'],
                    'completion_rate': schedule_result['completion_analysis']['completion_rate']
                },
                'message': f"📅 Target date {target_date} is outside the 14-day schedule range ({today} to {today + timedelta(days=13)})"
            }
        
        # Get tasks for the target date (using the calculated day index)
        day_tasks = schedule_result['schedule'][days_difference] if schedule_result['schedule'] else []
        
        # Calculate original total time
        original_total_time = timedelta()
        for task in day_tasks:
            if isinstance(task.get('time_allotted'), timedelta):
                original_total_time += task['time_allotted']
        
        # Apply 5-minute rounding if requested
        if round_to_5min and day_tasks:
            rounded_tasks = []
            for task in day_tasks:
                rounded_task = task.copy()
                if isinstance(task.get('time_allotted'), timedelta):
                    rounded_task['time_allotted'] = round_to_5_min_blocks(task['time_allotted'], round_up=True)
                    rounded_task['time_allotted_original'] = task['time_allotted']  # Keep original for reference
                rounded_tasks.append(rounded_task)
            day_tasks = rounded_tasks
        
        # Calculate total time (rounded if applicable)
        total_time = timedelta()
        for task in day_tasks:
            if isinstance(task.get('time_allotted'), timedelta):
                total_time += task['time_allotted']
        
        # Get intensity used for the day
        intensity_used = schedule_result['intensity_used']
        
        # Format the response
        if day_tasks:
            rounding_note = " (times rounded to 5-minute blocks)" if round_to_5min else ""
            message = f"✅ Found {len(day_tasks)} tasks scheduled for {target_date}{rounding_note}"
        else:
            message = f"📅 No tasks scheduled for {target_date} - it's a free day!"
        
        result = {
            'success': True,
            'target_date': target_date,
            'tasks': day_tasks,
            'total_tasks': len(day_tasks),
            'total_time': str(total_time),
            'intensity_used': intensity_used,
            'schedule_info': {
                'start_date': schedule_result['start_date'],
                'end_date': schedule_result['end_date'],
                'total_tasks_scheduled': schedule_result['total_tasks_scheduled'],
                'completion_rate': schedule_result['completion_analysis']['completion_rate']
            },
            'message': message
        }
        
        # Add original time if rounding was applied
        if round_to_5min:
            result['total_time_original'] = str(original_total_time)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'An error occurred while getting tasks for date: {str(e)}'
        }
