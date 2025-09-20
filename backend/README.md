# StudyBunny Backend

Django REST API backend for the StudyBunny mobile application.

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser (optional):
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

## Project Structure

```
backend/
├── apps/
│   ├── core/          # Core functionality
│   ├── users/         # User management
│   └── study/         # Study tracking
├── study_bunny/       # Django settings
├── requirements.txt
└── manage.py
```

## Development

- Backend runs on http://localhost:8000
- Admin panel: http://localhost:8000/admin
- API endpoints will be added in the respective app directories
