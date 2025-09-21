# StudyBunny Application Startup Script for Windows
Write-Host "🐰 Starting StudyBunny Application..." -ForegroundColor Green

# Function to cleanup background processes
function Cleanup {
    Write-Host "🛑 Shutting down..." -ForegroundColor Yellow
    if ($BackendJob) {
        Stop-Job $BackendJob -ErrorAction SilentlyContinue
        Remove-Job $BackendJob -ErrorAction SilentlyContinue
    }
    if ($FrontendJob) {
        Stop-Job $FrontendJob -ErrorAction SilentlyContinue
        Remove-Job $FrontendJob -ErrorAction SilentlyContinue
    }
    exit 0
}

# Set up cleanup on script exit
Register-EngineEvent PowerShell.Exiting -Action { Cleanup }

# Function to start backend
function Start-Backend {
    Write-Host "🚀 Starting Django Backend..." -ForegroundColor Cyan
    
    # Activate virtual environment
    & ".\studybunny_env\Scripts\Activate.ps1"
    
    # Change to backend directory
    Set-Location backend
    
    # Run migrations
    Write-Host "Running database migrations..." -ForegroundColor Yellow
    python manage.py migrate
    
    # Start Django server
    Write-Host "Starting Django server on port 8000..." -ForegroundColor Yellow
    $BackendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        & ".\studybunny_env\Scripts\Activate.ps1"
        Set-Location backend
        python manage.py runserver 8000
    }
    Write-Host "Backend started with Job ID: $($BackendJob.Id)" -ForegroundColor Green
    
    Set-Location ..
}

# Function to start frontend
function Start-Frontend {
    Write-Host "🎨 Starting React Frontend..." -ForegroundColor Cyan
    Set-Location frontend
    
    # Install dependencies if needed
    if (!(Test-Path "node_modules")) {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    # Start React development server
    Write-Host "Starting React server on port 3000..." -ForegroundColor Yellow
    $FrontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        npm start
    }
    Write-Host "Frontend started with Job ID: $($FrontendJob.Id)" -ForegroundColor Green
    
    Set-Location ..
}

# Main execution
Write-Host "🔧 Setting up StudyBunny..." -ForegroundColor Magenta

# Start backend
Start-Backend

# Wait a moment for backend to start
Start-Sleep -Seconds 5

# Start frontend
Start-Frontend

Write-Host "✅ StudyBunny is running!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Admin: http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow

# Wait for user to stop
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Cleanup
}
