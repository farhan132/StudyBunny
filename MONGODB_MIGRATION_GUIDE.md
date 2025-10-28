# MongoDB Migration Guide

Guide for migrating StudyBunny from SQLite to MongoDB.

## Overview

This guide explains how to migrate your existing StudyBunny data from SQLite to MongoDB Atlas.

## Why MongoDB?

- **Scalability**: Better horizontal scaling for growing user base
- **Flexibility**: Schema-less design allows for easier iterations
- **Cloud-Native**: MongoDB Atlas provides managed cloud database
- **Performance**: Better performance for document-based queries
- **AWS Integration**: Seamless integration with AWS services

---

## Migration Options

### Option 1: Fresh Start (Recommended for New Deployments)

If you're deploying to production for the first time:

1. Set up MongoDB Atlas (see AWS_DEPLOYMENT_GUIDE.md)
2. Run migrations on MongoDB:
```bash
# Set environment variables
export USE_MONGODB=True
export MONGODB_URI='your-connection-string'
export MONGODB_NAME='studybunny'

# Run migrations
cd backend
python manage.py migrate
```

3. Run MongoDB setup script:
```bash
python setup_mongodb.py
```

### Option 2: Data Migration from SQLite

If you have existing SQLite data to migrate:

#### Step 1: Export Data from SQLite
```bash
cd backend

# Export all data to JSON
python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude=contenttypes --exclude=auth.permission \
  --indent=2 > data_export.json
```

#### Step 2: Set Up MongoDB
```bash
# Configure MongoDB connection
export USE_MONGODB=True
export MONGODB_URI='your-connection-string'
export MONGODB_NAME='studybunny'

# Run migrations on MongoDB
python manage.py migrate

# Setup indexes
python setup_mongodb.py
```

#### Step 3: Import Data to MongoDB
```bash
# Load data into MongoDB
python manage.py loaddata data_export.json
```

#### Step 4: Verify Migration
```bash
# Create a verification script
python manage.py shell
```

```python
from apps.study.models import Task
from apps.core.models import GlobalIntensity
from apps.notifications.models import Notification

# Check counts
print(f"Tasks: {Task.objects.count()}")
print(f"Global Intensity: {GlobalIntensity.objects.count()}")
print(f"Notifications: {Notification.objects.count()}")

# Verify data integrity
task = Task.objects.first()
print(f"Sample task: {task}")
```

---

## Django with MongoDB (Djongo)

### How It Works

Djongo is a connector that translates Django ORM queries to MongoDB queries.

### Supported Features
- ✅ Basic CRUD operations
- ✅ Filtering and queries
- ✅ Foreign keys and relationships
- ✅ Indexes
- ✅ Migrations
- ✅ Admin interface

### Limitations
- ⚠️ Some complex SQL queries may not work
- ⚠️ Transactions are limited (MongoDB supports transactions in replica sets)
- ⚠️ Some Django features may have reduced functionality

### Model Compatibility

Your existing Django models work with MongoDB through Djongo:

```python
# This model works with both SQLite and MongoDB
class Task(models.Model):
    title = models.CharField(max_length=200)
    T_n = models.DurationField()
    due_date = models.DateField()
    # ... other fields
```

---

## Configuration

### Development (SQLite)
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Production (MongoDB)
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'studybunny',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb+srv://...',
        }
    }
}
```

### Environment-Based Configuration
```python
# settings.py
USE_MONGODB = os.environ.get('USE_MONGODB', 'False') == 'True'

if USE_MONGODB:
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': os.environ.get('MONGODB_NAME', 'studybunny'),
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': os.environ.get('MONGODB_URI'),
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

---

## MongoDB Best Practices

### 1. Indexes

Create indexes for frequently queried fields:

```python
# In models.py
class Task(models.Model):
    # ...
    class Meta:
        indexes = [
            models.Index(fields=['user', 'due_date']),
            models.Index(fields=['is_completed']),
        ]
```

### 2. Connection Pooling

MongoDB Atlas handles connection pooling automatically. Configure in connection string:

```
mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority&maxPoolSize=50
```

### 3. Query Optimization

```python
# Good - Select only needed fields
tasks = Task.objects.only('title', 'due_date')

# Good - Use select_related for foreign keys
schedules = DailySchedule.objects.select_related('user')

# Good - Use prefetch_related for many-to-many
schedules = DailySchedule.objects.prefetch_related('task_assignments')
```

### 4. Pagination

```python
# Use pagination for large datasets
from django.core.paginator import Paginator

tasks = Task.objects.all()
paginator = Paginator(tasks, 25)  # 25 tasks per page
page = paginator.get_page(1)
```

---

## Monitoring MongoDB

### MongoDB Atlas Dashboard

1. Log in to MongoDB Atlas
2. Select your cluster
3. View metrics:
   - Operations per second
   - Connections
   - Network traffic
   - Disk usage

### Query Performance

```python
# Enable query profiling in Django
import logging
logging.basicConfig()
logging.getLogger('djongo').setLevel(logging.DEBUG)
```

### Slow Queries

In MongoDB Atlas:
1. Go to Performance Advisor
2. Review slow queries
3. Add suggested indexes

---

## Backup Strategy

### MongoDB Atlas Automated Backups

1. Go to Cluster → Backup
2. Enable "Cloud Backup"
3. Configure:
   - Continuous backups
   - Snapshot schedule
   - Retention period

### Manual Backup

```bash
# Export entire database
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/studybunny" \
  --out=./backup

# Restore from backup
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/studybunny" \
  ./backup/studybunny
```

### Django-Based Backup

```bash
# Export to JSON
python manage.py dumpdata > backup.json

# Restore from JSON
python manage.py loaddata backup.json
```

---

## Troubleshooting

### Connection Issues

```python
# Test MongoDB connection
from pymongo import MongoClient

uri = "your-connection-string"
client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error: {e}")
```

### Authentication Failed

- Verify username and password
- Check user permissions in MongoDB Atlas
- Ensure password is URL-encoded

### Network Errors

- Check IP whitelist in Network Access
- Verify VPC peering (if using)
- Test from your deployment environment

### Migration Errors

```bash
# Clear migrations and retry
python manage.py migrate --fake-initial

# Or reset migrations
python manage.py migrate app_name zero
python manage.py migrate app_name
```

---

## Testing

### Test Both Databases

```python
# test_settings.py
import sys

if '--mongodb' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'studybunny_test',
            'CLIENT': {
                'host': 'mongodb://localhost:27017/',
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
```

```bash
# Test with SQLite
python manage.py test

# Test with MongoDB
python manage.py test --mongodb
```

---

## Performance Comparison

### SQLite vs MongoDB

| Feature | SQLite | MongoDB |
|---------|--------|---------|
| Scalability | Limited | High |
| Concurrent Writes | Limited | High |
| Cloud Integration | Manual | Native |
| Backup | File-based | Automated |
| Replication | Manual | Built-in |
| Horizontal Scaling | No | Yes |

### When to Use Each

**SQLite** (Development):
- Local development
- Small datasets
- Single user
- Simple setup

**MongoDB** (Production):
- Multiple users
- Large datasets
- Cloud deployment
- Need for scaling
- Automated backups

---

## Migration Checklist

- [ ] Set up MongoDB Atlas cluster
- [ ] Configure database user and permissions
- [ ] Whitelist IP addresses
- [ ] Test connection locally
- [ ] Export SQLite data (if migrating)
- [ ] Configure MongoDB in Django settings
- [ ] Run migrations on MongoDB
- [ ] Import data (if migrating)
- [ ] Verify data integrity
- [ ] Test application functionality
- [ ] Create database indexes
- [ ] Set up automated backups
- [ ] Configure monitoring
- [ ] Update deployment scripts
- [ ] Document connection strings securely

---

## Resources

- [Djongo Documentation](https://djongo.readthedocs.io/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [Django Database Configuration](https://docs.djangoproject.com/en/4.2/ref/databases/)

---

**Last Updated**: October 2025

