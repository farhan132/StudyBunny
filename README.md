# 🐰 StudyBunny

A comprehensive study management application that helps students organize their academic tasks, track progress, and optimize their study schedule using AI-powered voice commands and intelligent scheduling algorithms.

## ✨ Features

### 📚 Task Management
- Create, update, and delete academic tasks
- Track completion progress with visual progress bars
- Set due dates, priorities, and estimated completion times
- Automatic task categorization and organization

### 🎤 Voice AI Agent
- Voice-controlled task management using Web Speech API
- Natural language commands for task updates
- AI-powered task matching and completion tracking
- Real-time voice feedback and confirmation

### 📊 Intelligent Scheduling
- 14-day dynamic study schedule generation
- AI-optimized task distribution based on intensity levels
- Personal score calculation based on minimum required intensity
- Automatic past-due task handling

### 🎨 Canvas LMS Integration
- Import assignments directly from Canvas courses
- Automatic task creation with proper time estimation
- Configurable Canvas API token management
- Real-time assignment synchronization

### 📈 Analytics & Statistics
- Personal performance metrics
- Study intensity tracking
- Progress visualization
- Historical data analysis

### 🔔 Notifications System
- Real-time task reminders
- Progress update notifications
- Due date alerts
- Achievement celebrations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- npm or yarn
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/farhan132/StudyBunny.git
   cd StudyBunny
   ```

2. **Start the application**
   ```bash
   chmod +x start_app.sh
   ./start_app.sh
   ```

   This script will automatically:
   - Set up Python virtual environment
   - Install backend dependencies
   - Run database migrations
   - Start Django backend server (port 8000)
   - Install frontend dependencies
   - Start React development server (port 3000)

3. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **Admin Panel**: http://localhost:8000/admin

### Manual Setup (Alternative)

If you prefer to set up manually:

#### Backend Setup
```bash
cd backend
python3.11 -m venv venv311
source venv311/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🎯 Usage

### Voice Commands
Click the microphone button (🎤) and try these commands:
- "I finished the math assignment"
- "I completed PSET 1"
- "I'm done with my homework"
- "I finished 50% of the science project"

### Canvas Integration
1. Click the Canvas sync button (🎨)
2. Enter your Canvas API token
3. Configure your Canvas base URL
4. Import assignments automatically

### Task Management
- **Add Tasks**: Use the "Add Assignment" form
- **Update Progress**: Drag the progress sliders
- **Mark Complete**: Use voice commands or click complete
- **View Schedule**: Check the 14-day schedule view

## 🛠️ Technology Stack

### Backend
- **Python 3.11** - Core language
- **Django** - Web framework
- **Django REST Framework** - API development
- **SQLite/PostgreSQL** - Database
- **Celery** - Background tasks
- **Redis** - Caching and message broker

### Frontend
- **React 18** - UI framework
- **JavaScript ES6+** - Programming language
- **CSS3** - Styling
- **Web Speech API** - Voice recognition
- **Fetch API** - HTTP requests

### AI & Integrations
- **Google Gemini AI** - Natural language processing
- **Canvas LMS API** - Educational platform integration
- **Web Speech API** - Browser-based voice recognition

### Development Tools
- **Git** - Version control
- **npm** - Package management
- **pip** - Python package management
- **ESLint** - Code linting
- **Prettier** - Code formatting

## 📁 Project Structure

```
StudyBunny/
├── backend/                 # Django backend
│   ├── apps/
│   │   ├── core/           # Core functionality
│   │   ├── study/          # Study management
│   │   └── notifications/  # Notification system
│   ├── voice_agent/        # Voice AI integration
│   ├── features/           # Canvas integration
│   └── study_bunny/        # Django settings
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   └── public/             # Static assets
├── start_app.sh           # Application startup script
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `backend/voice_agent/` directory:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Canvas Integration
1. Get your Canvas API token from Canvas → Account → Settings → Approved Integrations
2. Use the Canvas sync button in the app to configure

## 🐛 Troubleshooting

### Common Issues

**Voice Agent Not Working**
- Ensure you're using Chrome or Edge browser
- Check browser permissions for microphone access
- Verify Gemini API key is configured

**Canvas Integration Issues**
- Verify Canvas API token is correct
- Check Canvas base URL format
- Ensure assignments are published in Canvas

**Database Issues**
- Run `python manage.py migrate` to apply migrations
- Check database permissions
- Verify database connection settings

### Debug Mode
Enable debug logging by checking browser console and Django server logs for detailed information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for natural language processing
- Canvas LMS for educational platform integration
- React and Django communities for excellent documentation
- Web Speech API for browser-based voice recognition

## 📞 Support

For support, email support@studybunny.com or create an issue in the GitHub repository.

---

**Happy Studying! 🎓✨**