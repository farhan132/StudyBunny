import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import './shared.css';
import './Statistics.css';
import apiService from '../services/api';

function Statistics() {
  useEffect(() => {
    // Fetch 14-day schedule to trigger simulation
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
    <div className="page">
      <h1> Statistics</h1>
      <p>Track your study progress and performance metrics</p>
      
      <div className="page-content">
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Study Hours</h3>
            <div className="stat-value">24.5</div>
            <p>This week</p>
          </div>
          <div className="stat-card">
            <h3>Completed Tasks</h3>
            <div className="stat-value">12</div>
            <p>This week</p>
          </div>
          <div className="stat-card">
            <h3>Streak</h3>
            <div className="stat-value">7</div>
            <p>Days in a row</p>
          </div>
          <div className="stat-card">
            <h3>Focus Score</h3>
            <div className="stat-value">85%</div>
            <p>Average</p>
          </div>
        </div>
        
        <div className="chart-placeholder">
          <h3>Study Progress Chart</h3>
          <p>Visual representation of your study patterns will appear here</p>
        </div>
      </div>
    </div>
  );
}

export default Statistics;
