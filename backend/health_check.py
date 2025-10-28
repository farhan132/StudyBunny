#!/usr/bin/env python
"""
Health check script for StudyBunny deployment
Verifies all services are working correctly
"""

import os
import sys
import requests
from pymongo import MongoClient
from datetime import datetime

def print_status(service, status, message=""):
    """Print colored status message"""
    colors = {
        'success': '\033[92m',  # Green
        'error': '\033[91m',    # Red
        'warning': '\033[93m',  # Yellow
        'info': '\033[94m',     # Blue
        'end': '\033[0m'        # Reset
    }
    
    status_symbol = {
        'success': '✓',
        'error': '✗',
        'warning': '⚠',
        'info': 'ℹ'
    }
    
    color = colors.get(status, colors['info'])
    symbol = status_symbol.get(status, '•')
    
    print(f"{color}{symbol} {service}{colors['end']}", end='')
    if message:
        print(f" - {message}")
    else:
        print()

def check_mongodb():
    """Check MongoDB connection"""
    try:
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        mongodb_name = os.environ.get('MONGODB_NAME', 'studybunny')
        
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        
        db = client[mongodb_name]
        collections = db.list_collection_names()
        
        print_status("MongoDB Connection", "success", f"Connected to {mongodb_name}")
        print_status("MongoDB Collections", "info", f"{len(collections)} collections found")
        
        client.close()
        return True
    except Exception as e:
        print_status("MongoDB Connection", "error", str(e))
        return False

def check_django():
    """Check Django application"""
    try:
        # Import Django
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
        django.setup()
        
        print_status("Django Setup", "success", f"Django {django.get_version()}")
        
        # Check database connection
        from django.db import connection
        connection.ensure_connection()
        print_status("Django Database", "success", "Database connection working")
        
        # Check models
        from apps.study.models import Task
        from apps.core.models import GlobalIntensity
        
        task_count = Task.objects.count()
        intensity = GlobalIntensity.get_current_intensity()
        
        print_status("Django Models", "success", f"{task_count} tasks, intensity: {intensity}")
        
        return True
    except Exception as e:
        print_status("Django Setup", "error", str(e))
        return False

def check_api_endpoint(url):
    """Check if API endpoint is accessible"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print_status(f"API Endpoint", "success", f"{url} - Status: {response.status_code}")
            return True
        else:
            print_status(f"API Endpoint", "warning", f"{url} - Status: {response.status_code}")
            return False
    except Exception as e:
        print_status(f"API Endpoint", "error", f"{url} - {str(e)}")
        return False

def check_environment_variables():
    """Check required environment variables"""
    required_vars = [
        'SECRET_KEY',
        'MONGODB_URI',
        'MONGODB_NAME',
    ]
    
    optional_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_STORAGE_BUCKET_NAME',
    ]
    
    all_good = True
    
    print_status("Environment Variables", "info", "Checking required variables...")
    for var in required_vars:
        if os.environ.get(var):
            print_status(f"  {var}", "success", "Set")
        else:
            print_status(f"  {var}", "error", "Missing")
            all_good = False
    
    print_status("Optional Variables", "info", "Checking optional variables...")
    for var in optional_vars:
        if os.environ.get(var):
            print_status(f"  {var}", "success", "Set")
        else:
            print_status(f"  {var}", "warning", "Not set (optional)")
    
    return all_good

def check_aws_services():
    """Check AWS services connectivity"""
    try:
        import boto3
        
        # Check S3
        if os.environ.get('USE_S3') == 'True':
            s3 = boto3.client('s3')
            bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
            
            if bucket_name:
                s3.head_bucket(Bucket=bucket_name)
                print_status("AWS S3", "success", f"Bucket {bucket_name} accessible")
            else:
                print_status("AWS S3", "warning", "Bucket name not configured")
        else:
            print_status("AWS S3", "info", "S3 not enabled")
        
        return True
    except ImportError:
        print_status("AWS Services", "warning", "boto3 not installed")
        return False
    except Exception as e:
        print_status("AWS Services", "error", str(e))
        return False

def main():
    """Run all health checks"""
    print("=" * 60)
    print("StudyBunny Health Check")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    print("1. Environment Variables")
    print("-" * 60)
    results.append(check_environment_variables())
    print()
    
    print("2. MongoDB Connection")
    print("-" * 60)
    results.append(check_mongodb())
    print()
    
    print("3. Django Application")
    print("-" * 60)
    results.append(check_django())
    print()
    
    print("4. AWS Services")
    print("-" * 60)
    results.append(check_aws_services())
    print()
    
    # Optional: Check API endpoint if URL is provided
    api_url = os.environ.get('API_URL')
    if api_url:
        print("5. API Endpoint")
        print("-" * 60)
        results.append(check_api_endpoint(api_url))
        print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print_status("Overall Status", "success", f"All checks passed ({passed}/{total})")
        return 0
    else:
        print_status("Overall Status", "warning", f"{passed}/{total} checks passed")
        return 1

if __name__ == '__main__':
    sys.exit(main())

