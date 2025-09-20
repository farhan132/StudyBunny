import voice_agent_gemini as va
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
                    print(f"✅ user said: {user_text}")
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

def delete_task(task_name=None, parameters=None):
    """Delete task function - called when status update indicates completion"""
    print("=" * 50)
    print("🗑️ DELETE TASK FUNCTION TRIGGERED!")
    print(f"   Task name: {task_name}")
    print(f"   Parameters: {parameters}")
    print("   ✅ This means a task was marked as COMPLETED/FINISHED")
    print("=" * 50)
    # TODO: Implement delete completed task functionality
    pass

def update_task(task_name=None, parameters=None):
    """Update task function - handles all status updates"""
    print("=" * 50)
    print("📝 UPDATE TASK FUNCTION TRIGGERED!")
    print(f"   Task name: {task_name}")
    print(f"   Parameters: {parameters}")
    print("   ✅ This means a task status was updated (progress/priority/etc)")
    print("=" * 50)
    # TODO: Implement update task functionality
    pass

def process_voice_command(text):
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
                        delete_task(task_name, parameters)
                    else:  # PROGRESS or UPDATE
                        print(f"📝 Calling update_task() for update #{update_count}")
                        update_task(task_name, parameters)
            
            print(f"\n✅ Processed {update_count} updates total")
                
        else:
            print("❌ No Gemini API key found")
            return text
            
    except Exception as e:
        print(f"❌ Error with Gemini: {e}")
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
        print("❌ No voice input captured")
        return None

# Example usage
if __name__ == "__main__":
    result = main()
    print(f"Final result: {result}")
