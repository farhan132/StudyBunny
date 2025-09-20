import React from 'react';
import { Link } from 'react-router-dom';
import './shared.css';
import './Notifications.css';

function Notifications() {
  return (
    <div className="page">
      <h1> Notifications</h1>
      <p>Manage your study reminders and alerts</p>
      
      <div className="page-content">
        <div className="notification-settings">
          <h2>Notification Settings</h2>
          <div className="setting-item">
            <label>
              <input type="checkbox" defaultChecked />
              Study session reminders
            </label>
          </div>
          <div className="setting-item">
            <label>
              <input type="checkbox" defaultChecked />
              Break time alerts
            </label>
          </div>
          <div className="setting-item">
            <label>
              <input type="checkbox" />
              Daily progress reports
            </label>
          </div>
          <div className="setting-item">
            <label>
              <input type="checkbox" defaultChecked />
              Goal achievement notifications
            </label>
          </div>
        </div>
        
        <div className="recent-notifications">
          <h2>Recent Notifications</h2>
          <div className="notification-list">
            <div className="notification-item">
              <span className="notification-time">2 hours ago</span>
              <p>Great job! You completed your math study session.</p>
            </div>
            <div className="notification-item">
              <span className="notification-time">1 day ago</span>
              <p>Time for your scheduled break! Take a 10-minute rest.</p>
            </div>
            <div className="notification-item">
              <span className="notification-time">2 days ago</span>
              <p>You've reached your weekly study goal! </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Notifications;
