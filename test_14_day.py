#!/usr/bin/env python3.11
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from django.contrib.auth.models import User
from apps.study.task_utils import get_14_day_schedule
from datetime import date

def test_14_day():
    print("Testing 14-day schedule...")
    
    # Get demo user
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
    )
    
    print(f"User: {user.username}")
    
    # Test 14-day schedule
    try:
        result = get_14_day_schedule(user, None)
        print(f"Success: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_14_day()
