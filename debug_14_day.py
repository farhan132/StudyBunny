#!/usr/bin/env python3.11
import os
import sys
import django

# Setup Django
sys.path.append('/Users/farhan132/StudyBunny/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.study.task_utils import get_14_day_schedule
from datetime import date
import traceback

User = get_user_model()

def debug_14_day():
    print("Debugging 14-day schedule...")
    
    # Get demo user
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
    )
    
    print(f"User: {user.username}")
    
    # Test 14-day schedule
    try:
        print("Calling get_14_day_schedule...")
        result = get_14_day_schedule(user, None)
        print(f"Success: {result.get('success', False)}")
        print(f"Schedule length: {len(result.get('schedule', []))}")
    except Exception as e:
        print(f"Error: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_14_day()
