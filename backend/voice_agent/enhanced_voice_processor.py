"""
Enhanced Voice Processor - Handles task creation, updates, and completion
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from django.contrib.auth.models import User
from apps.study.task_utils import update_task_by_name, get_task_by_name, create_task as create_task_util
from apps.study.models import Task
from datetime import datetime, timedelta

def delete_task(task_name=None, parameters=None, user=None):
    """Delete/Complete task function - called when status update indicates completion"""
    print("=" * 50)
    print("🗑️ COMPLETE TASK FUNCTION TRIGGERED!")
    print(f"   Task name: {task_name}")
    print(f"   Parameters: {parameters}")
    print("   ✅ This means a task was marked as COMPLETED/FINISHED")
    print("=" * 50)
    
    if not user or not task_name:
        print("❌ Missing user or task name for completion")
        return False
    
    try:
        task = Task.objects.get(user=user, title=task_name)
        task.is_completed = True
        task.completed_so_far = 100.0
        task.save()
        print(f"✅ Task '{task_name}' marked as completed!")
        return True
    except Task.DoesNotExist:
        print(f"❌ Task '{task_name}' not found for user {user.username}")
        return False
    except Task.MultipleObjectsReturned:
        print(f"❌ Multiple tasks found with name '{task_name}'. Please be more specific.")
        return False
    except Exception as e:
        print(f"❌ Error completing task: {e}")
        return False

def update_task(task_name=None, parameters=None, user=None):
    """Update task function - handles all status updates"""
    print("=" * 50)
    print("📝 UPDATE TASK FUNCTION TRIGGERED!")
    print(f"   Task name: {task_name}")
    print(f"   Parameters: {parameters}")
    print("   ✅ This means a task status was updated (progress/priority/etc)")
    print("=" * 50)
    
    if not user or not task_name:
        print("❌ Missing user or task name for update")
        return False
    
    # Parse parameters to extract update values
    update_kwargs = {}
    
    if parameters:
        params_lower = parameters.lower()
        
        # Check for progress/percentage updates
        if '%' in parameters:
            try:
                import re
                percent_match = re.search(r'(\d+(?:\.\d+)?)%', parameters)
                if percent_match:
                    progress = float(percent_match.group(1))
                    update_kwargs['completed_so_far'] = progress
                    print(f"   📊 Setting progress to {progress}%")
            except ValueError:
                print(f"   ⚠️ Could not parse percentage: {parameters}")
        
        # Check for numeric progress without % symbol
        elif any(word in params_lower for word in ['progress', 'percent', 'complete']):
            try:
                import re
                number_match = re.search(r'(\d+(?:\.\d+)?)', parameters)
                if number_match:
                    progress = float(number_match.group(1))
                    if progress <= 100:  # Assume it's a percentage
                        update_kwargs['completed_so_far'] = progress
                        print(f"   📊 Setting progress to {progress}%")
            except ValueError:
                print(f"   ⚠️ Could not parse progress: {parameters}")
        
        # Check for priority updates
        priority_keywords = {
            'very high': 5, 'high': 4, 'medium': 3, 'low': 2, 'very low': 1,
            'priority 5': 5, 'priority 4': 4, 'priority 3': 3, 'priority 2': 2, 'priority 1': 1
        }
        
        for keyword, priority in priority_keywords.items():
            if keyword in params_lower:
                update_kwargs['delta'] = priority
                print(f"   🔥 Setting priority to {priority} ({keyword})")
                break
        
        # Check for time updates
        time_keywords = ['hours', 'hour', 'minutes', 'minute', 'time']
        if any(keyword in params_lower for keyword in time_keywords):
            try:
                import re
                time_match = re.search(r'(\d+(?:\.\d+)?)\s*(hours?|minutes?|mins?)', params_lower)
                if time_match:
                    value = float(time_match.group(1))
                    unit = time_match.group(2)
                    
                    if 'hour' in unit:
                        update_kwargs['T_n'] = timedelta(hours=value)
                        print(f"   ⏰ Setting expected time to {value} hours")
                    elif 'minute' in unit or 'min' in unit:
                        update_kwargs['T_n'] = timedelta(minutes=value)
                        print(f"   ⏰ Setting expected time to {value} minutes")
            except ValueError:
                print(f"   ⚠️ Could not parse time: {parameters}")
    
    # If no specific parameters were parsed, try to update progress
    if not update_kwargs and parameters:
        update_kwargs['completed_so_far'] = 50.0  # Default progress update
        print(f"   📊 Setting default progress to 50%")
    
    # Use the existing task utility function
    result = update_task_by_name(user, task_name, **update_kwargs)
    
    if result['success']:
        print(f"✅ Task updated successfully: {result['message']}")
        if 'updated_fields' in result:
            print(f"   Updated fields: {', '.join(result['updated_fields'])}")
        return True
    else:
        print(f"❌ Task update failed: {result['error']}")
        return False

def create_task(task_name=None, parameters=None, user=None):
    """Create task function - called when voice command indicates task creation"""
    print("=" * 50)
    print("📝 CREATE TASK FUNCTION TRIGGERED!")
    print(f"   Task name: {task_name}")
    print(f"   Parameters: {parameters}")
    print("   ✅ This means a new task should be created")
    print("=" * 50)
    
    if not user or not task_name:
        print("❌ Missing user or task name for creation")
        return False
    
    try:
        # Parse parameters to extract creation values
        priority = 3  # Default medium priority
        expected_time = timedelta(hours=2)  # Default 2 hours
        due_date = datetime.now().date() + timedelta(days=7)  # Default 1 week
        description = ""
        
        if parameters:
            params_lower = parameters.lower()
            
            # Parse priority
            priority_keywords = {
                'very high': 5, 'high': 4, 'medium': 3, 'low': 2, 'very low': 1,
                'priority 5': 5, 'priority 4': 4, 'priority 3': 3, 'priority 2': 2, 'priority 1': 1
            }
            
            for keyword, prio in priority_keywords.items():
                if keyword in params_lower:
                    priority = prio
                    print(f"   🔥 Setting priority to {priority} ({keyword})")
                    break
            
            # Parse time estimates
            import re
            time_match = re.search(r'(\d+(?:\.\d+)?)\s*(hours?|minutes?|mins?|days?)', params_lower)
            if time_match:
                value = float(time_match.group(1))
                unit = time_match.group(2)
                
                if 'hour' in unit:
                    expected_time = timedelta(hours=value)
                    print(f"   ⏰ Setting expected time to {value} hours")
                elif 'minute' in unit or 'min' in unit:
                    expected_time = timedelta(minutes=value)
                    print(f"   ⏰ Setting expected time to {value} minutes")
                elif 'day' in unit:
                    expected_time = timedelta(hours=value * 8)  # 8 hours per day
                    print(f"   ⏰ Setting expected time to {value} days ({value * 8} hours)")
            
            # Parse due date
            due_keywords = ['due', 'deadline', 'finish by', 'complete by']
            for keyword in due_keywords:
                if keyword in params_lower:
                    if 'tomorrow' in params_lower:
                        due_date = datetime.now().date() + timedelta(days=1)
                        print(f"   📅 Setting due date to tomorrow ({due_date})")
                    elif 'next week' in params_lower:
                        due_date = datetime.now().date() + timedelta(days=7)
                        print(f"   📅 Setting due date to next week ({due_date})")
                    elif 'today' in params_lower:
                        due_date = datetime.now().date()
                        print(f"   📅 Setting due date to today ({due_date})")
                    break
        
        # Create the task using the utility function
        result = create_task_util(
            user=user,
            name=task_name,
            priority=priority,
            due_date=due_date,
            expected_time=expected_time,
            description=description
        )
        
        if result['success']:
            print(f"✅ Task created successfully: {result['message']}")
            print(f"   Task ID: {result['task_id']}")
            return True
        else:
            print(f"❌ Task creation failed: {result['error']}")
            return False
        
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return False

def process_voice_command(text, user=None):
    """Enhanced voice command processor - handles creation, updates, and completion"""
    
    # Enhanced Gemini prompt for task creation, updates, and completion
    ask_gemini = f"""Analyze this text: "{text}" 
    
    This text might contain MULTIPLE task operations. Identify ALL operations mentioned and extract details for each one.
    
    For each operation, identify:
    - Type: CREATE (new task), COMPLETED (finished/done), PROGRESS (progress updates), or UPDATE (other changes)
    - Task name: What specific task is being mentioned
    - Parameters: Any specific values, numbers, percentages, times, priorities, due dates, etc.
    
    Look for multiple operations in the same text.
    
    Respond in this format (one line per operation):
    OPERATION1: TYPE=[CREATE/COMPLETED/PROGRESS/UPDATE] | TASK=[task name] | PARAMS=[parameters]
    OPERATION2: TYPE=[CREATE/COMPLETED/PROGRESS/UPDATE] | TASK=[task name] | PARAMS=[parameters]
    etc.
    
    Examples:
    "Create a new task called math homework with high priority"
    → OPERATION1: TYPE=CREATE | TASK=math homework | PARAMS=high priority
    
    "I finished my math homework and want to create a science project due tomorrow"
    → OPERATION1: TYPE=COMPLETED | TASK=math homework | PARAMS=none
    → OPERATION2: TYPE=CREATE | TASK=science project | PARAMS=due tomorrow
    
    "Update physics progress to 75% and create English essay with 3 hours estimated time"
    → OPERATION1: TYPE=PROGRESS | TASK=physics | PARAMS=75%
    → OPERATION2: TYPE=CREATE | TASK=English essay | PARAMS=3 hours
    
    "Add a new task for research paper and set high priority for math homework"
    → OPERATION1: TYPE=CREATE | TASK=research paper | PARAMS=none
    → OPERATION2: TYPE=UPDATE | TASK=math homework | PARAMS=high priority
    
    Keywords for CREATE: create, add, new task, make a task, start a task
    Keywords for COMPLETED: finished, completed, done, accomplished
    Keywords for PROGRESS: progress, percent, %, complete
    Keywords for UPDATE: update, change, modify, set priority"""
    
    try:
        # Configure Gemini
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            print("🤖 Analyzing with Gemini...")
            response = model.generate_content(ask_gemini)
            analysis = response.text.strip()
            
            print(f"🤖 Gemini analysis:")
            print(analysis)
            
            # Parse multiple operations
            operation_count = 0
            lines = analysis.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('OPERATION') and '|' in line:
                    operation_count += 1
                    
                    # Parse each operation
                    parts = line.split('|')
                    task_name = None
                    parameters = None
                    action_type = None
                    
                    for part in parts:
                        part = part.strip()
                        if 'TYPE=' in part:
                            action_type = part.replace('TYPE=', '').strip()
                        elif 'TASK=' in part:
                            task_name = part.replace('TASK=', '').strip()
                            if task_name.lower() == 'none':
                                task_name = None
                        elif 'PARAMS=' in part:
                            parameters = part.replace('PARAMS=', '').strip()
                            if parameters.lower() == 'none':
                                parameters = None
                    
                    print(f"\n📋 Operation #{operation_count}: Type={action_type}, Task={task_name}, Params={parameters}")
                    
                    # Call appropriate function for this operation
                    if "CREATE" in action_type:
                        print(f"📝 Calling create_task() for operation #{operation_count}")
                        create_task(task_name, parameters, user)
                    elif "COMPLETED" in action_type:
                        print(f"🗑️ Calling delete_task() for operation #{operation_count}")
                        delete_task(task_name, parameters, user)
                    else:  # PROGRESS or UPDATE
                        print(f"📝 Calling update_task() for operation #{operation_count}")
                        update_task(task_name, parameters, user)
            
            print(f"\n✅ Processed {operation_count} operations total")
                
        else:
            print("❌ No Gemini API key found")
            return text
            
    except Exception as e:
        print(f"❌ Error with Gemini: {e}")
        return text
