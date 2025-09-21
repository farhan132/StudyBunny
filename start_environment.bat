@echo off
echo 🐰 StudyBunny Environment Setup
echo =================================
echo.
echo Activating virtual environment...
call studybunny_env\Scripts\activate.bat
echo.
echo ✅ Environment activated!
echo.
echo Available commands:
echo ===================
echo.
echo Backend (Django):
echo   cd backend
echo   python manage.py runserver
echo.
echo Frontend (React):
echo   cd frontend
echo   npm start
echo.
echo Database migrations (if needed):
echo   cd backend
echo   python manage.py migrate
echo.
echo To run both simultaneously, open two terminals:
echo   Terminal 1: cd backend && python manage.py runserver
echo   Terminal 2: cd frontend && npm start
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo.
cmd /k
