#!/bin/bash

# StudyBunny Application Startup Script
echo "🐰 Starting StudyBunny Application..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Function to start backend
start_backend() {
    echo "🚀 Starting Django Backend..."
    cd backend

    # Check if virtual environment exists
    if [ ! -d "venv311" ]; then
        echo "Creating virtual environment with Python 3.11..."
        python3.11 -m venv venv311
    fi

    # Activate virtual environment
    source venv311/bin/activate

    # Install dependencies
    echo "Installing backend dependencies..."
    pip install -r requirements.txt

    # Run migrations
    echo "Running database migrations..."
    python3.11 manage.py makemigrations
    python3.11 manage.py migrate

    # Start Django server
    echo "Starting Django server on port 8000..."
    python3.11 manage.py runserver 8000 &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"

    cd ..
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting React Frontend..."
    cd frontend

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi

    # Start React development server
    echo "Starting React server on port 3000..."
    npm start &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"

    cd ..
}

# Main execution
echo "🔧 Setting up StudyBunny..."

# Start backend
start_backend

# Wait a moment for backend to start
sleep 3

# Start frontend
start_frontend

echo "✅ StudyBunny is running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 Admin: http://localhost:8000/admin"
echo ""
echo "Press Ctrl+C to stop the application"

# Wait for user to stop
wait
