# StudyBunny Development Environment Setup

This document explains how to set up and run the StudyBunny application with both frontend and backend components.

## Quick Start

### Option 1: PowerShell (Recommended)
```powershell
.\setup_environment.ps1
```

### Option 2: Batch File
```cmd
start_environment.bat
```

### Option 3: Manual Setup
```powershell
# Activate virtual environment
.\studybunny_env\Scripts\Activate.ps1

# Install Python dependencies (already done)
cd backend
pip install -r requirements.txt

# Install Node.js dependencies (already done)
cd ..\frontend
npm install
```

## Running the Application

### Backend (Django)
```powershell
cd backend
python manage.py runserver
```
- Backend will be available at: http://localhost:8000

### Frontend (React)
```powershell
cd frontend
npm start
```
- Frontend will be available at: http://localhost:3000

### Running Both Simultaneously
Open two terminal windows:

**Terminal 1 (Backend):**
```powershell
.\studybunny_env\Scripts\Activate.ps1
cd backend
python manage.py runserver
```

**Terminal 2 (Frontend):**
```powershell
cd frontend
npm start
```

## Database Setup

If you need to set up the database:
```powershell
cd backend
python manage.py migrate
```

## Environment Details

- **Python Virtual Environment**: `studybunny_env/`
- **Backend Framework**: Django 4.2.7 with Django REST Framework
- **Frontend Framework**: React 18.2.0
- **Database**: SQLite (default Django database)

## Dependencies

### Backend Dependencies
- Django==4.2.7
- djangorestframework==3.14.0
- django-cors-headers==4.3.1
- google-generativeai==0.3.2
- SpeechRecognition==3.10.0
- pydub==0.25.1
- python-multipart==0.0.6
- python-dotenv==1.0.0
- requests==2.31.0

### Frontend Dependencies
- react: ^18.2.0
- react-dom: ^18.2.0
- react-scripts: 5.0.1
- react-router-dom: ^6.8.1
- axios: ^1.6.2

## Troubleshooting

### Virtual Environment Issues
If you have issues with the virtual environment:
```powershell
# Remove and recreate
Remove-Item -Recurse -Force studybunny_env
python -m venv studybunny_env
.\studybunny_env\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
```

### Node.js Issues
If you have issues with Node.js dependencies:
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Port Conflicts
- Backend default port: 8000
- Frontend default port: 3000
- If these ports are in use, Django and React will automatically find available ports

## Development Workflow

1. Activate the environment using one of the setup scripts
2. Run database migrations if needed
3. Start the backend server
4. Start the frontend development server
5. Access the application at http://localhost:3000

The frontend is configured to proxy API requests to the backend at http://localhost:8000.
