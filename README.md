# StudyBunny Mobile App

A mobile application project with React.js frontend and Python Django backend.

## Project Structure

```
StudyBunny/
├── frontend/          # React.js mobile app
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── hooks/
│   │   └── contexts/
│   ├── package.json
│   └── README.md
├── backend/           # Django REST API
│   ├── apps/
│   │   ├── core/
│   │   ├── users/
│   │   └── study/
│   ├── study_bunny/
│   ├── requirements.txt
│   ├── manage.py
│   └── README.md
└── README.md
```

## Team Workflow

### Backend Team
- Work in `/backend` directory
- Use Django REST Framework for API development
- Follow Django best practices

### Frontend Team
- Work in `/frontend` directory
- Mobile-first responsive design
- Use React best practices

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Development

Each team can work independently in their respective directories. The backend runs on port 8000 and frontend on port 3000.