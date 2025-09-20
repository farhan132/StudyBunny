#!/usr/bin/env python
"""
Real Voice Agent - Actual Speech Recognition!
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('.')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv
from voice_agent.update_task_core import process_voice_command
from django.contrib.auth.models import User

def get_voice_input():
    """Capture actual voice input and return as string"""
    
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
                    print(f"✅ You said: {user_text}")
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

def main():
    """Main function for real voice agent"""
    print("🎤 StudyBunny Real Voice Agent")
    print("=" * 40)
    
    # Get user
    user = User.objects.first()
    if not user:
        print("❌ No users found. Please create a user first.")
        return
    
    print(f"✅ Connected as: {user.username}")
    print("\n💡 Example things to say:")
    print("   • I finished my math homework")
    print("   • Update science project progress to 75%")
    print("   • Set high priority for English essay")
    print("   • I completed homework and spent 2 hours on the project")
    print("\n" + "="*40)
    
    while True:
        try:
            # Get voice input
            command = get_voice_input()
            
            if not command:
                print("🔄 Try again...")
                continue
                
            if command.lower() in ['quit', 'exit', 'stop', 'bye', 'goodbye']:
                print("👋 Goodbye!")
                break
            
            print(f"\n🤖 Processing: '{command}'")
            print("-" * 30)
            
            # Process the command
            process_voice_command(command, user)
            
            print("\n" + "="*40)
            print("🎤 Ready for next command...")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()
