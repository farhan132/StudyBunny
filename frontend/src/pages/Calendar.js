import React from 'react';
import { Link } from 'react-router-dom';
import './shared.css';
import './Calendar.css';

function Calendar() {
  return (
    <div className="page">
      <h1> Calendar</h1>
      <p>Manage your study schedule and upcoming events</p>
      
      <div className="page-content">
        <div className="calendar-placeholder">
          <h2>Calendar View</h2>
          <p>Your study calendar will be displayed here</p>
          <div className="calendar-grid">
            <div className="calendar-day">Mon</div>
            <div className="calendar-day">Tue</div>
            <div className="calendar-day">Wed</div>
            <div className="calendar-day">Thu</div>
            <div className="calendar-day">Fri</div>
            <div className="calendar-day">Sat</div>
            <div className="calendar-day">Sun</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Calendar;
