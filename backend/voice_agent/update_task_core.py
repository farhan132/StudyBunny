"""
Core voice agent functions without speech recognition dependencies
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from django.contrib.auth.models import User
from apps.study.task_utils import update_task_by_name, get_task_by_name
from apps.study.models import Task

def delete_task(task_name=None, parameters=None, user=None):
    """Delete task function - called when status update indicates completion"""
    print("=" * 50)
    print("🗑️ DELETE TASK FUNCTION TRIGGERED!")
    print(f"   Task name: {task_name}")
    print(f"   Parameters: {parameters}")
    print("   ✅ This means a task was marked as COMPLETED/FINISHED")
    print("=" * 50)
    
    if not user:
        print("❌ No user provided for task deletion")
        return False
    
    if not task_name:
        print("❌ No task name provided for deletion")
        return False
    
    try:
        # Find the task by name for the specific user
        task = Task.objects.get(user=user, title=task_name)
        
        # Mark task as completed instead of deleting
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
    """Update task function - handles all status updates using existing task_utils"""
    print("=" * 50)
    print("📝 UPDATE TASK FUNCTION TRIGGERED!")
    print(f"   Task name: {task_name}")
    print(f"   Parameters: {parameters}")
    print("   ✅ This means a task status was updated (progress/priority/etc)")
    print("=" * 50)
    
    if not user:
        print("❌ No user provided for task update")
        return False
    
    if not task_name:
        print("❌ No task name provided for update")
        return False
    
    # Parse parameters to extract update values
    update_kwargs = {}
    
    if parameters:
        # Parse different types of parameters
        params_lower = parameters.lower()
        
        # Check for progress/percentage updates
        if '%' in parameters:
            try:
                # Extract percentage value
                import re
                percent_match = re.search(r'(\d+(?:\.\d+)?)%', parameters)
                if percent_match:
                    progress = float(percent_match.group(1))
                    update_kwargs['completed_so_far'] = progress
                    print(f"   📊 Setting progress to {progress}%")
            except ValueError:
                print(f"   ⚠️ Could not parse percentage: {parameters}")
        
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
                # Extract time value - this is a simplified parser
                import re
                time_match = re.search(r'(\d+(?:\.\d+)?)\s*(hours?|minutes?|mins?)', params_lower)
                if time_match:
                    value = float(time_match.group(1))
                    unit = time_match.group(2)
                    
                    if 'hour' in unit:
                        from datetime import timedelta
                        update_kwargs['T_n'] = timedelta(hours=value)
                        print(f"   ⏰ Setting expected time to {value} hours")
                    elif 'minute' in unit or 'min' in unit:
                        from datetime import timedelta
                        update_kwargs['T_n'] = timedelta(minutes=value)
                        print(f"   ⏰ Setting expected time to {value} minutes")
            except ValueError:
                print(f"   ⚠️ Could not parse time: {parameters}")
    
    # If no specific parameters were parsed, try to update progress to a reasonable value
    if not update_kwargs and parameters:
        # Default to updating progress if we have parameters but couldn't parse them
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

def process_voice_command(text, user=None):
    """Process voice command and call appropriate functions for MULTIPLE updates"""
    
    # Ask Gemini to identify ALL status updates and extract details for each
    ask_gemini = f"""Analyze this text: "{text}" 
    
    This text might contain MULTIPLE status updates. Identify ALL status updates mentioned and extract details for each one.
    
    For each status update, identify:
    - Type: COMPLETED (finished/done), PROGRESS (time spent/progress), or UPDATE (other)
    - Task name: What specific task is being mentioned
    - Parameters: Any specific values, numbers, percentages, times, etc.
    
    Look for multiple tasks/updates in the same text.
    
    Respond in this format (one line per update):
    UPDATE1: TYPE=[COMPLETED/PROGRESS/UPDATE] | TASK=[task name] | PARAMS=[parameters]
    UPDATE2: TYPE=[COMPLETED/PROGRESS/UPDATE] | TASK=[task name] | PARAMS=[parameters]
    etc.
    
    Examples:
    "I finished math homework and spent 2 hours on science project" 
    → UPDATE1: TYPE=COMPLETED | TASK=math homework | PARAMS=none
    → UPDATE2: TYPE=PROGRESS | TASK=science project | PARAMS=2 hours
    
    "Update task 1 progress to 50% and set high priority for task 2"
    → UPDATE1: TYPE=PROGRESS | TASK=task 1 | PARAMS=50%
    → UPDATE2: TYPE=UPDATE | TASK=task 2 | PARAMS=high priority
    
    "I completed homework, spent 3 hours on project, and want to update task 3"
    → UPDATE1: TYPE=COMPLETED | TASK=homework | PARAMS=none
    → UPDATE2: TYPE=PROGRESS | TASK=project | PARAMS=3 hours
    → UPDATE3: TYPE=UPDATE | TASK=task 3 | PARAMS=none"""
    
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
            
            # Parse multiple updates
            update_count = 0
            lines = analysis.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('UPDATE') and '|' in line:
                    update_count += 1
                    
                    # Parse each update
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
                    
                    print(f"\n📋 Update #{update_count}: Type={action_type}, Task={task_name}, Params={parameters}")
                    
                    # Call appropriate function for this update
                    if "COMPLETED" in action_type:
                        print(f"🗑️ Calling delete_task() for update #{update_count}")
                        delete_task(task_name, parameters, user)
                    else:  # PROGRESS or UPDATE
                        print(f"📝 Calling update_task() for update #{update_count}")
                        update_task(task_name, parameters, user)
            
            print(f"\n✅ Processed {update_count} updates total")
                
        else:
            print("❌ No Gemini API key found")
            return text
            
    except Exception as e:
        print(f"❌ Error with Gemini: {e}")
        return text

def main(user=None):
    """Main function to process voice commands"""
    print("🎤 Voice Status Update Processor - MULTIPLE UPDATES")
    print("=" * 55)
    
    if not user:
        print("❌ No user provided. Please provide a user for task operations.")
        return None
    
    # For testing, we'll simulate voice input
    test_commands = [
        "I finished my math homework",
        "Update science project progress to 75%",
        "Set high priority for English essay",
        "I completed homework and spent 2 hours on the project"
    ]
    
    print("Available test commands:")
    for i, cmd in enumerate(test_commands, 1):
        print(f"  {i}. {cmd}")
    
    choice = input("\nEnter command number (1-4) or type your own command: ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(test_commands):
        text = test_commands[int(choice) - 1]
    else:
        text = choice
    
    print(f"\n📝 Processing command: {text}")
    
    # Process the command and call appropriate functions
    process_voice_command(text, user)
    
    return text

# Example usage
if __name__ == "__main__":
    # For testing, you would need to provide a user
    # result = main(user=some_user)
    result = main()
    print(f"Final result: {result}")

def create_task(task_name=None, parameters=None, user=None):
    """Create task function - called when voice command indicates task creation"""
    print("=" * 50)
    print("📝 CREATE TASK FUNCTION TRIGGERED!")
    print(f"   Task name: {task_name}")
    print(f"   Parameters: {parameters}")
    print("   ✅ This means a new task should be created")
    print("=" * 50)
    
    if not user:
        print("❌ No user provided for task creation")
        return False
    
    if not task_name:
        print("❌ No task name provided for creation")
        return False
    
    try:
        from apps.study.task_utils import create_task as create_task_util
        from datetime import datetime, timedelta, date
        
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
                    expected_time = timedelta(days=value * 8)  # 8 hours per day
                    print(f"   ⏰ Setting expected time to {value} days ({value * 8} hours)")
            
            # Parse due date
            due_keywords = ['due', 'deadline', 'finish by', 'complete by']
            for keyword in due_keywords:
                if keyword in params_lower:
                    # Simple parsing for "due tomorrow", "due next week", etc.
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
