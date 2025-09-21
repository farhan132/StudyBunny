# StudyBunny Features - Canvas Integration

This directory contains all Canvas LMS integration features for StudyBunny.

## 📁 File Structure

### Core Integration Files
- **`canvas.py`** - Main Canvas integration class (`CanvasIntegrator`) and sync function
- **`canvas_models.py`** - Data models for Canvas courses, assignments, and StudyBunny task conversion
- **`canvas_utils.py`** - Low-level API client, data processing, and filtering utilities
- **`canvas_config.py`** - Configuration constants, API endpoints, and settings

### Scripts and Examples
- **`extract_canvas_tasks.py`** - Standalone script to extract Canvas data and create StudyBunny tasks
- **`test_canvas_integration.py`** - Test script for Canvas API connectivity and data fetching
- **`canvas_example.py`** - Usage examples and demonstrations
- **`__init__.py`** - Module exports and imports

## 🚀 Quick Start

### 1. Set up your Canvas API token
```bash
# Add to backend/.env file
CANVAS_API_TOKEN=your_canvas_token_here
CANVAS_BASE_URL=https://canvas.instructure.com  # Optional, defaults to this
```

### 2. Basic usage in Django views/scripts
```python
from features import CanvasIntegrator, sync_canvas_homework
from django.contrib.auth.models import User

# Get or create user
user = User.objects.get(username='your_username')

# Sync Canvas homework to StudyBunny tasks
success, message, tasks_created = sync_canvas_homework(user, api_token)
print(f"Created {tasks_created} tasks: {message}")
```

### 3. Advanced usage with utilities
```python
from features import CanvasSync, CanvasTaskConverter

# Initialize Canvas sync
canvas_sync = CanvasSync()

# Get upcoming assignments
upcoming = canvas_sync.get_upcoming_assignments(days_ahead=14)

# Convert to StudyBunny tasks
converter = CanvasTaskConverter()
for course, assignment in upcoming:
    task = converter.convert_to_studybunny_task(assignment, course)
    print(f"Task: {task.title}, Est. Time: {task.estimated_hours}h")
```

## 🔧 Key Features

### Data Models
- **`CanvasCourse`** - Represents Canvas course with credit hour extraction
- **`CanvasAssignment`** - Assignment data with due date/time parsing
- **`StudyBunnyTask`** - Converted task ready for StudyBunny database
- **`CanvasTaskConverter`** - Intelligent conversion with time estimation and priority

### API Client
- **`CanvasAPIClient`** - Low-level Canvas API requests
- **`CanvasDataProcessor`** - Parse and transform Canvas JSON data
- **`CanvasDataFilter`** - Filter active/relevant courses and assignments
- **`CanvasSync`** - High-level sync operations

### Smart Features
- **Time Estimation**: Automatically estimates study time based on:
  - Assignment points/weight
  - Course credit hours
  - Assignment type (exam, project, homework, etc.)
  - Due date proximity

- **Priority Calculation**: Sets priority (1-5) based on:
  - Days until due date
  - Assignment importance
  - Course workload

- **MIT Course Support**: Built-in recognition of MIT course codes (6.006, 18.600, etc.)

## 🛠️ Scripts

### Extract Canvas Tasks
```bash
cd backend/features
python extract_canvas_tasks.py
```
Extracts all Canvas assignments and creates StudyBunny tasks for the demo user.

### Test Canvas Integration  
```bash
cd backend/features
python test_canvas_integration.py
```
Tests Canvas API connectivity and displays fetched data.

### Usage Examples
```bash
cd backend/features  
python canvas_example.py
```
Demonstrates various Canvas integration features.

## 📊 Data Flow

1. **Canvas API** → Raw JSON data
2. **CanvasDataProcessor** → Structured objects (`CanvasCourse`, `CanvasAssignment`)
3. **CanvasDataFilter** → Active/relevant assignments only
4. **CanvasTaskConverter** → StudyBunny-compatible tasks
5. **Django Models** → Saved to StudyBunny database

## ⚙️ Configuration

### Environment Variables
```bash
CANVAS_API_TOKEN=your_token_here
CANVAS_BASE_URL=https://your-institution.instructure.com  # Optional
```

### Time Estimation Defaults
- Quiz: 1 hour
- Homework: 3 hours  
- Project: 8 hours
- Exam: 5 hours (study time)
- Paper: 6 hours

### Priority Thresholds
- Priority 1: Due in ≤1 day
- Priority 2: Due in ≤3 days
- Priority 3: Due in ≤1 week
- Priority 4: Due in ≤2 weeks
- Priority 5: Due later

## 🔍 Troubleshooting

### Common Issues

1. **`CANVAS_API_TOKEN not found`**
   - Add your Canvas token to `backend/.env`
   - Get token from Canvas → Settings → Approved Integrations

2. **`ModuleNotFoundError`** 
   - Ensure Django is set up: `python manage.py check`
   - Run from correct directory with virtual environment active

3. **Canvas API errors**
   - Check token permissions
   - Verify Canvas base URL
   - Check rate limiting

### Debug Mode
Set `DEBUG=True` in Django settings for detailed error messages.

## 🚀 Integration with StudyBunny

The Canvas integration seamlessly works with:
- **Task Management**: Creates proper StudyBunny `Task` objects
- **Time Estimation**: Uses StudyBunny's time calculation system
- **Priority System**: Maps to StudyBunny's 1-5 priority scale
- **User System**: Associates tasks with Django users
- **API Endpoints**: Works with existing StudyBunny REST API

## 📈 Future Enhancements

- [ ] Real-time sync with webhooks
- [ ] Grade integration
- [ ] Calendar export
- [ ] Multiple Canvas instances
- [ ] Batch operations UI
- [ ] Assignment group weighting
- [ ] Submission status tracking
