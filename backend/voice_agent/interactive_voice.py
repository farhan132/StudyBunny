#!/usr/bin/env python
"""
Interactive Voice Agent - Talk to your StudyBunny!
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('.')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from voice_agent.update_task_core import process_voice_command
from django.contrib.auth.models import User

def get_user_input():
    """Get text input from user (simulating voice input)"""
    print("\n🎤 Voice Agent Ready!")
    print("Type your command (or 'quit' to exit):")
    return input("You: ").strip()

def main():
    """Interactive voice agent main function"""
    print("🎤 StudyBunny Voice Agent - Interactive Mode")
    print("=" * 50)
    
    # Get user
    user = User.objects.first()
    if not user:
        print("❌ No users found. Please create a user first.")
        return
    
    print(f"✅ Connected as: {user.username}")
    print("\n💡 Example commands:")
    print("   • I finished my math homework")
    print("   • Update science project progress to 75%")
    print("   • Set high priority for English essay")
    print("   • I completed homework and spent 2 hours on the project")
    print("\n" + "="*50)
    
    while True:
        try:
            # Get user input
            command = get_user_input()
            
            if not command:
                continue
                
            if command.lower() in ['quit', 'exit', 'stop', 'bye']:
                print("👋 Goodbye!")
                break
            
            print(f"\n🤖 Processing: '{command}'")
            print("-" * 30)
            
            # Process the command
            process_voice_command(command, user)
            
            print("\n" + "="*50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()
