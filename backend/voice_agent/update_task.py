# import voice_agent_gemini as va

# Import aifc compatibility module before importing speech_recognition
try:
    import aifc
except ImportError:
    # Python 3.13+ compatibility - aifc module was removed
    from . import aifc_compat

import speech_recognition as sr
import os
import google.generativeai as genai
from dotenv import load_dotenv
from django.contrib.auth.models import User
from apps.study.task_utils import update_task_by_name, get_task_by_name
from apps.study.models import Task

def get_voice_input():
    """Capture voice input and return as string"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize speech recognition
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    # Settings for complete sentences
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 2.0  # Wait 2 seconds of silence
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 1.0
    
    print("🎤 Listening... (speak now)")
    
    try:
        with microphone as source:
            print("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Ready! Speak to me...")
            
            # Listen for complete speech
            audio = recognizer.listen(
                source, 
                timeout=30,
                phrase_time_limit=60
            )
            
            print("🔄 Processing your speech...")
            
            try:
                # Convert speech to text
                user_text = recognizer.recognize_google(audio, language='en-US')
                
                if user_text and len(user_text.strip()) > 0:
                    print(f"✅ User said: {user_text}")
                    return user_text
                else:
                    print("❌ No speech detected")
                    return None
                    
            except sr.UnknownValueError:
                print("❌ Could not understand - try speaking more clearly")
                return None
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                return None
                
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return None

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
        # First try exact match
        try:
            task = Task.objects.get(user=user, title=task_name)
        except Task.DoesNotExist:
            # Try partial match - look for tasks that contain the task name
            tasks = Task.objects.filter(user=user, title__icontains=task_name)
            if tasks.count() == 1:
                task = tasks.first()
                print(f"🔍 Found task by partial match: '{task.title}'")
            elif tasks.count() > 1:
                print(f"❌ Multiple tasks found containing '{task_name}':")
                for t in tasks:
                    print(f"   - {t.title}")
                return False
            else:
                # Try reverse partial match - look for tasks where the title is contained in the task name
                tasks = Task.objects.filter(user=user)
                matching_tasks = [t for t in tasks if t.title.lower() in task_name.lower()]
                
                # If no direct match, try word-based matching
                if not matching_tasks:
                    task_name_words = set(task_name.lower().split())
                    task_matches = []
                    for t in tasks:
                        title_words = set(t.title.lower().split())
                        # Check if any significant words from the title appear in the task name
                        common_words = title_words.intersection(task_name_words)
                        # Remove common words like "the", "a", "an", "and", "or", "of", "in", "on", "at", "to", "for"
                        common_words = common_words - {'the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'assignment', 'task', 'work'}
                        if len(common_words) > 0:
                            task_matches.append((t, len(common_words), common_words))
                            print(f"🔍 Found task by word matching: '{t.title}' (common words: {common_words}, score: {len(common_words)})")
                    
                    # Sort by number of matching words (descending) and take the best match
                    if task_matches:
                        task_matches.sort(key=lambda x: x[1], reverse=True)
                        best_match = task_matches[0]
                        # Only use this match if it has a reasonable number of common words or if it's the only match
                        if best_match[1] >= 2 or len(task_matches) == 1:
                            matching_tasks.append(best_match[0])
                        else:
                            # If multiple matches with low scores, show all options
                            matching_tasks.extend([match[0] for match in task_matches])
                
                if len(matching_tasks) == 1:
                    task = matching_tasks[0]
                    print(f"🔍 Found task by reverse partial match: '{task.title}'")
                elif len(matching_tasks) > 1:
                    print(f"❌ Multiple tasks found containing '{task_name}':")
                    for t in matching_tasks:
                        print(f"   - {t.title}")
                    return False
                else:
                    raise Task.DoesNotExist()
        
        # Mark task as completed instead of deleting
        task.is_completed = True
        task.completed_so_far = 100.0
        task.save()
        
        print(f"✅ Task '{task.title}' marked as completed!")
        return True
        
    except Task.DoesNotExist:
        print(f"❌ Task '{task_name}' not found for user {user.username}")
        # Show available tasks
        available_tasks = Task.objects.filter(user=user, is_completed=False)
        if available_tasks.exists():
            print("📋 Available incomplete tasks:")
            for t in available_tasks:
                print(f"   - {t.title}")
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
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
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
    
    # Get voice input
    text = get_voice_input()
    
    if text:
        print(f"📝 Voice command: {text}")
        
        # Process the command and call appropriate functions
        process_voice_command(text, user)
        
        return text
    else:
        print("❌ No voice input captured")
        return None

# Example usage
if __name__ == "__main__":
    # For testing, you would need to provide a user
    # result = main(user=some_user)
    result = main()
    print(f"Final result: {result}")
