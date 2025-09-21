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
    <div className="page statistics-page">
      <div className="statistics-header">
        <div className="header-content">
          <h1 className="page-title">
            Statistics
          </h1>
          <p className="page-subtitle">Track your study progress and performance metrics</p>
        </div>
        <div className="header-decoration">
          <div className="floating-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3v18h18"/>
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
            </svg>
          </div>
          <div className="floating-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
          </div>
          <div className="floating-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </div>
          <div className="floating-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>
              <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>
              <path d="M4 22h16"/>
              <path d="M10 14.66V17c0 .55.47.98.97 1.21l1.03.5c.5.23 1.03.23 1.53 0l1.03-.5c.5-.23.97-.66.97-1.21v-2.34"/>
              <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>
            </svg>
          </div>
          <div className="floating-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
          </div>
          <div className="floating-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
          </div>
        </div>
      </div>
      
      <div className="page-content">
        <div className="stats-grid">
          <div className="stat-card study-hours">
            <div className="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <h3>Study Hours</h3>
            <div className="stat-value">24.5</div>
            <p>This week</p>
          </div>
          
          <div className="stat-card completed-tasks">
            <div className="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9 12l2 2 4-4"/>
              </svg>
            </div>
            <h3>Completed Tasks</h3>
            <div className="stat-value">12</div>
            <p>This week</p>
          </div>
          
          <div className="stat-card streak">
            <div className="card-icon streak">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
              </svg>
            </div>
            <h3>Streak</h3>
            <div className="stat-value">7</div>
            <p>Days in a row</p>
          </div>
          
          <div className="stat-card focus-score">
            <div className="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </div>
            <h3>Focus Score</h3>
            <div className="stat-value">85%</div>
            <p>Average</p>
          </div>
        </div>
        
        <div className="chart-section">
          <div className="chart-header">
            <h3>🥕 Study Progress Chart</h3>
            <div className="chart-controls">
              <button className="chart-btn active">Week</button>
              <button className="chart-btn">Month</button>
              <button className="chart-btn">Year</button>
            </div>
          </div>
          <div className="chart-container">
            <div className="temporary-chart">
              <div className="chart-content">
                <div className="chart-bars">
                  <div className="chart-bar-container">
                    <div className="chart-bar" style={{height: '140px'}}></div>
                    <span className="bar-label">Mon</span>
                  </div>
                  <div className="chart-bar-container">
                    <div className="chart-bar" style={{height: '168px'}}></div>
                    <span className="bar-label">Tue</span>
                  </div>
                  <div className="chart-bar-container">
                    <div className="chart-bar" style={{height: '85px'}}></div>
                    <span className="bar-label">Wed</span>
                  </div>
                  <div className="chart-bar-container">
                    <div className="chart-bar" style={{height: '188px'}}></div>
                    <span className="bar-label">Thu</span>
                  </div>
                  <div className="chart-bar-container">
                    <div className="chart-bar" style={{height: '113px'}}></div>
                    <span className="bar-label">Fri</span>
                  </div>
                  <div className="chart-bar-container">
                    <div className="chart-bar" style={{height: '160px'}}></div>
                    <span className="bar-label">Sat</span>
                  </div>
                  <div className="chart-bar-container">
                    <div className="chart-bar" style={{height: '56px'}}></div>
                    <span className="bar-label">Sun</span>
                  </div>
                </div>
                <div className="chart-y-axis">
                  <span>8h</span>
                  <span>6h</span>
                  <span>4h</span>
                  <span>2h</span>
                  <span>0h</span>
                </div>
              </div>
              <div className="chart-legend-bottom">
                <div className="legend-item">
                  <div className="legend-color" style={{backgroundColor: '#90caf9'}}></div>
                  <span>Study Hours</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="achievements-section">
          <h3>🥕 Recent Achievements</h3>
          <div className="achievements-grid">
            <div className="achievement-card">
              <div className="achievement-icon">🎯</div>
              <h4>Focus Master</h4>
              <p>Maintained 85% focus for 3 days straight</p>
            </div>
            <div className="achievement-card">
              <div className="achievement-icon">⚡</div>
              <h4>Speed Learner</h4>
              <p>Completed 5 tasks in one day</p>
            </div>
            <div className="achievement-card">
              <div className="achievement-icon">🌟</div>
              <h4>Consistency Star</h4>
              <p>7-day study streak achieved</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Statistics;
