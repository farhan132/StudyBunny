#!/usr/bin/env python
"""
MongoDB setup script for StudyBunny
Creates indexes and initial data
"""

import os
import sys
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime

def setup_mongodb():
    """Setup MongoDB collections and indexes"""
    
    # Get MongoDB connection string from environment
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    mongodb_name = os.environ.get('MONGODB_NAME', 'studybunny')
    
    print(f"Connecting to MongoDB: {mongodb_name}...")
    
    try:
        client = MongoClient(mongodb_uri)
        db = client[mongodb_name]
        
        # Test connection
        client.server_info()
        print("✓ Connected to MongoDB successfully")
        
        # Create collections if they don't exist
        collections = {
            'core_globalintensity': 'Global intensity settings',
            'core_timecalculation': 'Time calculations',
            'study_task': 'Tasks',
            'study_dailyschedule': 'Daily schedules',
            'study_taskassignment': 'Task assignments',
            'notifications_notificationsettings': 'Notification settings',
            'notifications_notification': 'Notifications',
            'notifications_notificationtemplate': 'Notification templates',
            'auth_user': 'Users',
        }
        
        print("\nCreating collections and indexes...")
        
        # Tasks collection indexes
        tasks_collection = db['study_task']
        tasks_collection.create_index([('user_id', ASCENDING)])
        tasks_collection.create_index([('due_date', ASCENDING)])
        tasks_collection.create_index([('is_completed', ASCENDING)])
        tasks_collection.create_index([('created_at', DESCENDING)])
        print("✓ Created indexes for tasks collection")
        
        # Notifications collection indexes
        notifications_collection = db['notifications_notification']
        notifications_collection.create_index([('user_id', ASCENDING), ('is_read', ASCENDING)])
        notifications_collection.create_index([('created_at', DESCENDING)])
        print("✓ Created indexes for notifications collection")
        
        # Daily schedules collection indexes
        schedules_collection = db['study_dailyschedule']
        schedules_collection.create_index([('date', ASCENDING)], unique=True)
        schedules_collection.create_index([('user_id', ASCENDING)])
        print("✓ Created indexes for daily schedules collection")
        
        # Time calculations collection indexes
        time_calc_collection = db['core_timecalculation']
        time_calc_collection.create_index([('date', ASCENDING)], unique=True)
        print("✓ Created indexes for time calculations collection")
        
        # Global intensity - ensure only one document exists
        intensity_collection = db['core_globalintensity']
        if intensity_collection.count_documents({}) == 0:
            intensity_collection.insert_one({
                '_id': 1,
                'intensity': 0.7,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            print("✓ Created default global intensity setting")
        else:
            print("✓ Global intensity setting already exists")
        
        print("\n" + "="*50)
        print("MongoDB setup completed successfully!")
        print("="*50)
        
        # Print collection stats
        print("\nDatabase Statistics:")
        for collection_name, description in collections.items():
            if collection_name in db.list_collection_names():
                count = db[collection_name].count_documents({})
                print(f"  {description}: {count} documents")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error setting up MongoDB: {e}")
        return False
    finally:
        client.close()

if __name__ == '__main__':
    print("="*50)
    print("StudyBunny MongoDB Setup")
    print("="*50)
    print()
    
    success = setup_mongodb()
    sys.exit(0 if success else 1)

