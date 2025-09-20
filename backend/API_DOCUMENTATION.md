# StudyBunny Backend API Documentation

## Overview

The StudyBunny backend is a Django REST API that provides time management and task scheduling functionality. It includes intelligent time calculation, task prioritization, and daily planning features.

## Architecture

### Core Components

1. **Time Management (`apps.core`)**
   - Time calculations for different dates
   - Free time calculation (skeleton functions for custom implementation)
   - Time analysis and reporting
   - Global intensity variable for system behavior adjustment

2. **Task Management (`apps.study`)**
   - Task creation and management
   - Priority-based scheduling
   - Progress tracking
   - Daily planning generation

3. **User Management (`apps.users`)**
   - User authentication and profiles
   - Task ownership and permissions

## Models

### TimeCalculation
Stores time calculations for different dates.

**Fields:**
- `date`: Date for the calculation
- `time_today`: Time left until midnight
- `free_today`: Available free time
- `created_at`, `updated_at`: Timestamps

### Task
Represents a task with time tracking and priority.

**Fields:**
- `title`: Task title
- `description`: Task description
- `user`: Owner of the task
- `T_n`: Expected time needed to complete (DurationField)
- `completed_so_far`: Completion percentage (0-100%)
- `delta`: Priority level (1-5)
- `due_date`: Due date
- `due_time`: Due time
- `is_completed`: Completion status

**Properties:**
- `due_datetime`: Combined due date and time
- `time_remaining`: Time left based on completion percentage
- `is_overdue`: Whether task is overdue
- `days_until_due`: Days until due date

### DailySchedule
Stores daily task scheduling.

**Fields:**
- `date`: Schedule date
- `user`: Owner of the schedule
- `created_at`, `updated_at`: Timestamps

### TaskAssignment
Specific task assignments for a day.

**Fields:**
- `daily_schedule`: Associated daily schedule
- `task`: Assigned task
- `time_allotted`: Time allocated for the task
- `start_time`: Scheduled start time
- `end_time`: Scheduled end time
- `completed_time`: Actual time spent
- `is_completed`: Completion status

## API Endpoints

### Authentication
All endpoints require authentication. Use either:
- Session authentication (for web interface)
- Token authentication (for API clients)

### Core API (`/api/core/`)

#### Time Calculations
- `GET /api/core/time-calculations/` - List all time calculations
- `POST /api/core/time-calculations/` - Create new time calculation
- `GET /api/core/time-calculations/{id}/` - Get specific time calculation
- `PUT /api/core/time-calculations/{id}/` - Update time calculation
- `DELETE /api/core/time-calculations/{id}/` - Delete time calculation

#### Time Utilities
- `GET /api/core/time-today/` - Get time remaining until midnight
  - Query params: `date` (optional, format: YYYY-MM-DD)
- `GET /api/core/free-time-today/` - Get free time available today
  - Query params: `date` (optional, format: YYYY-MM-DD)
- `GET /api/core/time-analysis/` - Get time analysis for date range
  - Query params: `start_date`, `end_date` (format: YYYY-MM-DD)

#### Intensity Management
- `GET /api/core/intensity/` - Get current global intensity value
- `POST /api/core/intensity/set/` - Set global intensity value
  - Body: `{"intensity": 0.8}` (value between 0.0 and 1.0)

### Study API (`/api/study/`)

#### Tasks
- `GET /api/study/tasks/` - List all tasks for authenticated user
- `POST /api/study/tasks/` - Create new task
- `GET /api/study/tasks/{id}/` - Get specific task
- `PUT /api/study/tasks/{id}/` - Update task
- `DELETE /api/study/tasks/{id}/` - Delete task
- `GET /api/study/tasks/user/` - Get user tasks with filtering
  - Query params:
    - `is_completed`: true/false
    - `priority`: 1-5
    - `due_after`: YYYY-MM-DD
    - `due_before`: YYYY-MM-DD
- `PATCH /api/study/tasks/{id}/progress/` - Update task progress
  - Body: `{"completed_so_far": 75.5}`
- `GET /api/study/tasks/statistics/` - Get task statistics

#### Daily Schedules
- `GET /api/study/daily-schedules/` - List daily schedules
- `POST /api/study/daily-schedules/` - Create daily schedule
- `GET /api/study/daily-schedules/{id}/` - Get specific schedule
- `PUT /api/study/daily-schedules/{id}/` - Update schedule
- `DELETE /api/study/daily-schedules/{id}/` - Delete schedule

#### Planning
- `POST /api/study/generate-daily-plan/` - Generate daily task plan
  - Body: `{"date": "2024-01-15"}` (optional)

## Global Intensity System

The system includes a global intensity variable that affects various calculations:

- **Variable:** `STUDYBUNNY_INTENSITY` in settings.py
- **Range:** 0.0 to 1.0
- **Default:** 0.7
- **Usage:** Can be changed anytime to adjust system behavior

### Intensity Impact
- **0.0:** Very low intensity (relaxed pace)
- **0.5:** Medium intensity (balanced)
- **1.0:** Very high intensity (maximum effort)

The intensity variable can be used in your custom implementations to:
- Adjust free time calculations
- Modify task scheduling algorithms
- Influence priority scoring
- Control time allocation strategies

## Skeleton Functions for Custom Implementation

### Time Calculation Functions

#### `TimeManager.calculate_free_today(target_date=None)`
**Purpose:** Calculate free time available today
**Current Implementation:** Placeholder (50% of remaining time, adjusted by intensity)
**TODO:** Implement your logic considering:
- Work hours
- Scheduled events
- Personal commitments
- Sleep schedule
- Meal times
- Global intensity setting

#### `TimeManager.calculate_free_d(target_date)`
**Purpose:** Calculate free time available on a specific date
**Current Implementation:** Placeholder (50% of day, adjusted by intensity)
**TODO:** Implement your logic considering:
- Day of the week (weekday vs weekend)
- Holidays
- Recurring events
- Personal schedule patterns
- Global intensity setting

### Task Scheduling Functions

#### `TaskScheduler.generate_daily_plan(user, target_date=None)`
**Purpose:** Generate daily task plan for a user
**Current Implementation:** Basic placeholder with intensity-based task limits
**TODO:** Implement your scheduling algorithm considering:
- Available free time for the day
- Task priorities (delta)
- Due dates
- Task completion percentages
- Time needed (T_n)
- Global intensity setting

#### `TaskScheduler._calculate_priority_score(task, target_date)`
**Purpose:** Calculate priority score for a task
**Current Implementation:** Basic urgency + priority calculation with intensity multiplier
**TODO:** Implement your priority scoring considering:
- Task delta (priority level)
- Days until due date
- Completion percentage
- Task size (T_n)
- Global intensity setting
- Any other factors you deem important

#### `TaskScheduler._calculate_time_allocation(task, available_time, priority_score)`
**Purpose:** Calculate how much time to allocate to a task
**Current Implementation:** Basic time allocation
**TODO:** Implement your time allocation logic considering:
- Task's remaining time
- Priority score
- Available time
- Minimum viable work sessions
- Maximum time per task per day
- Global intensity setting

## Example Usage

### Creating a Task
```bash
curl -X POST http://localhost:8000/api/study/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "title": "Complete project report",
    "description": "Write the quarterly project report",
    "T_n": "04:00:00",
    "delta": 4,
    "due_date": "2024-01-20",
    "due_time": "17:00:00"
  }'
```

### Generating Daily Plan
```bash
curl -X POST http://localhost:8000/api/study/generate-daily-plan/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"date": "2024-01-15"}'
```

### Getting Free Time Today
```bash
curl -X GET "http://localhost:8000/api/core/free-time-today/?date=2024-01-15" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Managing Intensity
```bash
# Get current intensity
curl -X GET http://localhost:8000/api/core/intensity/ \
  -H "Authorization: Token YOUR_TOKEN"

# Set new intensity
curl -X POST http://localhost:8000/api/core/intensity/set/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"intensity": 0.8}'
```

## Development Setup

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

4. **Start development server:**
   ```bash
   python manage.py runserver
   ```

5. **Access admin panel:**
   - URL: http://localhost:8000/admin
   - Username: admin
   - Password: admin123

## Next Steps

1. **Implement the skeleton functions** in `apps/core/time_utils.py`:
   - `calculate_free_today()` - Use intensity in calculations
   - `calculate_free_d()` - Use intensity in calculations
   - `generate_daily_plan()` - Use intensity for task limits and scheduling
   - `_calculate_priority_score()` - Use intensity for priority weighting
   - `_calculate_time_allocation()` - Use intensity for time allocation

2. **Customize intensity behavior** in your implementations:
   - Adjust how intensity affects free time calculations
   - Modify task scheduling based on intensity levels
   - Implement intensity-based priority scoring
   - Create intensity-aware time allocation strategies

3. **Add authentication endpoints** for user registration and login

4. **Implement JWT authentication** for better API security

5. **Add more sophisticated scheduling algorithms**

6. **Create frontend integration** with the React app

7. **Add real-time notifications** for task deadlines

8. **Implement data analytics** and reporting features

## Notes

- All time calculations use Django's `timezone` module for proper timezone handling
- Task completion is automatically set to 100% when `completed_so_far` reaches 100
- The system is designed to be extensible - you can add more fields to models as needed
- All API responses are in JSON format
- Error responses include descriptive error messages
- **Intensity variable** can be changed anytime to adjust system behavior
- **Intensity range:** 0.0 (low) to 1.0 (high), default 0.7
- **Intensity access:** Use `from apps.core.intensity import get_intensity` in your code
