# import voice_agent_gemini as va  # Not needed for this implementation
import speech_recognition as sr
import os
import google.generativeai as genai
from dotenv import load_dotenv

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
            print("Ready! Speak to me...")
            
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
                    print(f"user said: {user_text}")
                    return user_text
                else:
                    print("No speech detected")
                    return None
                    
            except sr.UnknownValueError:
                print("Could not understand - try speaking more clearly")
                return None
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                return None
                
    except Exception as e:
        print(f" Microphone error: {e}")
        return None

def delete_task(task_name=None, parameters=None, user=None):
    """Delete task function - called when status update indicates completion"""
    print("=" * 50)
    print("🗑️ DELETE TASK FUNCTION TRIGGERED!")
    print(f"   Task name: {task_name}")
    print(f"   Parameters: {parameters}")
    print("    This means a task was marked as COMPLETED/FINISHED")
    print("=" * 50)
    
    # Import Django models
    from django.contrib.auth.models import User
    from apps.study.models import Task
    
    if not user:
        # Get demo user as fallback
        try:
            user = User.objects.get(username='demo_user')
        except User.DoesNotExist:
            print("❌ No user provided and demo_user not found")
            return False
    
    if not task_name:
        print("❌ No task name provided for deletion")
        return False
    
    try:
        # First try exact match
        task = None
        try:
            task = Task.objects.get(user=user, title=task_name, is_completed=False)
        except Task.DoesNotExist:
            # Try fuzzy matching - look for tasks containing keywords
            tasks = Task.objects.filter(user=user, is_completed=False)
            
            # Extract keywords from the voice command
            keywords = task_name.lower().split()
            if parameters:
                keywords.extend(parameters.lower().split())
            
            # Look for tasks that contain any of these keywords
            for t in tasks:
                title_lower = t.title.lower()
                if any(keyword in title_lower for keyword in keywords if len(keyword) > 2):
                    task = t
                    print(f"🔍 Found matching task: '{t.title}' for keywords: {keywords}")
                    break
        
        if task:
            # Mark task as completed instead of deleting
            task.is_completed = True
            task.completed_so_far = 100.0
            task.save()
            
            print(f"✅ Task '{task.title}' marked as completed!")
            return True
        else:
            print(f"❌ Task '{task_name}' not found for user {user.username}")
            # Show available tasks
            available_tasks = Task.objects.filter(user=user, is_completed=False)
            if available_tasks.exists():
                print("📋 Available incomplete tasks:")
                for t in available_tasks:
                    print(f"   - {t.title}")
            return False
        
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
    """Update task function - handles all status updates"""
    print("=" * 50)
    print("UPDATE TASK FUNCTION TRIGGERED!")
    print(f"   Task name: {task_name}")
    print(f"   Parameters: {parameters}")
    print("    This means a task status was updated (progress/priority/etc)")
    print("=" * 50)
    
    # Import Django models
    from django.contrib.auth.models import User
    from apps.study.models import Task
    
    if not user:
        # Get demo user as fallback
        try:
            user = User.objects.get(username='demo_user')
        except User.DoesNotExist:
            print("❌ No user provided and demo_user not found")
            return False
    
    if not task_name:
        print("❌ No task name provided for update")
        return False
    
    try:
        # First try exact match
        task = None
        try:
            task = Task.objects.get(user=user, title=task_name, is_completed=False)
        except Task.DoesNotExist:
            # Try fuzzy matching - look for tasks containing keywords
            tasks = Task.objects.filter(user=user, is_completed=False)
            
            # Extract keywords from the voice command
            keywords = task_name.lower().split()
            if parameters:
                keywords.extend(parameters.lower().split())
            
            # Look for tasks that contain any of these keywords
            for t in tasks:
                title_lower = t.title.lower()
                if any(keyword in title_lower for keyword in keywords if len(keyword) > 2):
                    task = t
                    print(f"🔍 Found matching task: '{t.title}' for keywords: {keywords}")
                    break
        
        if task:
            # Parse parameters to update task
            if parameters:
                params_lower = parameters.lower()
                
                # Look for progress updates
                if '%' in params_lower or 'percent' in params_lower:
                    # Extract percentage
                    import re
                    percentage_match = re.search(r'(\d+)%?', params_lower)
                    if percentage_match:
                        progress = float(percentage_match.group(1))
                        task.completed_so_far = min(progress, 100.0)
                        task.save()
                        print(f"✅ Updated '{task.title}' progress to {progress}%")
                        return True
                
                # Look for time spent updates
                elif 'hour' in params_lower or 'minute' in params_lower:
                    print(f"⏰ Time update detected for '{task.title}': {parameters}")
                    # Could implement time tracking here
                    return True
                
                # Look for priority updates
                elif any(word in params_lower for word in ['high', 'low', 'medium', 'priority']):
                    print(f"📈 Priority update detected for '{task.title}': {parameters}")
                    # Could implement priority updates here
                    return True
            
            print(f"✅ Task '{task.title}' updated with parameters: {parameters}")
            return True
        else:
            print(f"❌ Task '{task_name}' not found for user {user.username}")
            # Show available tasks
            available_tasks = Task.objects.filter(user=user, is_completed=False)
            if available_tasks.exists():
                print("📋 Available incomplete tasks:")
                for t in available_tasks:
                    print(f"   - {t.title}")
            return False
        
    except Exception as e:
        print(f"❌ Error updating task: {e}")
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
            
            print(f" Gemini analysis:")
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
            
            print(f"\n Processed {update_count} updates total")
                
        else:
            print("No Gemini API key found")
            return text
            
    except Exception as e:
        print(f"Error with Gemini: {e}")
        return text

def main():
    """Main function to process voice commands"""
    print(" Voice Status Update Processor - MULTIPLE UPDATES")
    print("=" * 55)
    
    # Get voice input
    text = get_voice_input()
    
    if text:
        print(f"📝 Voice command: {text}")
        
        # Process the command and call appropriate functions
        process_voice_command(text)
        
        return text
    else:
        print(" No voice input captured")
        return None

# Example usage
if __name__ == "__main__":
    result = main()
    print(f"Final result: {result}")
