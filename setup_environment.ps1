# StudyBunny Environment Setup Script
# This script activates the virtual environment and provides commands to run both frontend and backend

Write-Host "🐰 StudyBunny Environment Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Activate the virtual environment
Write-Host "Activating Python virtual environment..." -ForegroundColor Yellow
& ".\studybunny_env\Scripts\Activate.ps1"

Write-Host ""
Write-Host "✅ Environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend (Django):" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Frontend (React):" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm start" -ForegroundColor White
Write-Host ""
Write-Host "Database migrations (if needed):" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  python manage.py migrate" -ForegroundColor White
Write-Host ""
Write-Host "To run both simultaneously, open two terminals:" -ForegroundColor Magenta
Write-Host "  Terminal 1: cd backend && python manage.py runserver" -ForegroundColor White
Write-Host "  Terminal 2: cd frontend && npm start" -ForegroundColor White
Write-Host ""
Write-Host "Backend will run on: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend will run on: http://localhost:3000" -ForegroundColor Green
