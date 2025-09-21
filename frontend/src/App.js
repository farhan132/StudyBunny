import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Home from './pages/Home';
import Calendar from './pages/Calendar';
import Statistics from './pages/Statistics';
import Notifications from './pages/Notifications';
import apiService from './services/api';
import './App.css';

function App() {
  useEffect(() => {
    // Fetch 14-day schedule on app load to trigger simulation
    const fetch14DaySchedule = async () => {
      try {
        await apiService.get14DaySchedule();
      } catch (error) {
        console.error('Error fetching 14-day schedule:', error);
      }
    };
    
    fetch14DaySchedule();
  }, []);
  return (
    <Router>
      <div className="App">
        <Navigation />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/notifications" element={<Notifications />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
