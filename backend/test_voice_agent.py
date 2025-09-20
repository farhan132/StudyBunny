#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('.')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from voice_agent.update_task import delete_task, update_task
from django.contrib.auth.models import User

def test_voice_agent():
    """Test the voice agent functions without speech recognition"""
    print("🧪 Testing Voice Agent Functions")
    print("=" * 40)
    
    try:
        # Get first user
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return
        
        print(f"✅ Testing with user: {user.username}")
        
        # Test delete_task function
        print("\n🗑️ Testing delete_task function...")
        result = delete_task('test task', 'completed', user)
        print(f"   Result: {result}")
        
        # Test update_task function  
        print("\n📝 Testing update_task function...")
        result = update_task('test task', '50% progress', user)
        print(f"   Result: {result}")
        
        # Test with different parameters
        print("\n📝 Testing update_task with priority...")
        result = update_task('test task', 'high priority', user)
        print(f"   Result: {result}")
        
        print("\n✅ Voice agent functions tested successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_voice_agent()
