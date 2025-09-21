import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './shared.css';
import './Notifications.css';
import apiService from '../services/api';

function Notifications() {
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: 'success',
      title: 'Study Session Complete!',
      message: 'Great job! You completed your math study session.',
      time: '2 hours ago',
      icon: '🎉',
      read: false
    },
    {
      id: 2,
      type: 'reminder',
      title: 'Break Time!',
      message: 'Time for your scheduled break! Take a 10-minute rest.',
      time: '1 day ago',
      icon: '⏰',
      read: false
    },
    {
      id: 3,
      type: 'achievement',
      title: 'Goal Achieved!',
      message: 'You\'ve reached your weekly study goal!',
      time: '2 days ago',
      icon: '🏆',
      read: true
    },
    {
      id: 4,
      type: 'motivation',
      title: 'Keep Going!',
      message: 'You\'re on a 5-day streak! Don\'t stop now.',
      time: '3 days ago',
      icon: '🔥',
      read: true
    }
  ]);

  const [settings, setSettings] = useState({
    studyReminders: true,
    breakAlerts: true,
    progressReports: false,
    goalAchievements: true,
    motivationMessages: true,
    soundEnabled: true
  });

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

  const handleSettingChange = (setting) => {
    setSettings(prev => ({
      ...prev,
      [setting]: !prev[setting]
    }));
  };

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="notifications-page">
      {/* Header */}
      <div className="notifications-header">
        <div className="header-content">
          <div className="page-title">
            <span className="title-icon bunny-icon">🥕</span>
            <span>Notifications</span>
          </div>
          <p className="page-subtitle">Stay updated with your study progress and reminders</p>
        </div>
      </div>

      <div className="notifications-content">

        {/* Notification Settings */}
        <div className="settings-section">
          
          <div className="settings-grid">
            <div className="setting-card">
              <div className="setting-info">
                <div className="setting-icon study-icon"></div>
                <div className="setting-details">
                  <h3>Study Reminders</h3>
                  <p>Get notified about upcoming study sessions</p>
                </div>
              </div>
              <div className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={settings.studyReminders}
                  onChange={() => handleSettingChange('studyReminders')}
                />
                <span className="slider"></span>
              </div>
            </div>

            <div className="setting-card">
              <div className="setting-info">
                <div className="setting-icon break-icon"></div>
                <div className="setting-details">
                  <h3>Break Alerts</h3>
                  <p>Reminders to take breaks between sessions</p>
                </div>
              </div>
              <div className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={settings.breakAlerts}
                  onChange={() => handleSettingChange('breakAlerts')}
                />
                <span className="slider"></span>
              </div>
            </div>

            <div className="setting-card">
              <div className="setting-info">
                <div className="setting-icon progress-icon"></div>
                <div className="setting-details">
                  <h3>Progress Reports</h3>
                  <p>Daily summaries of your study progress</p>
                </div>
              </div>
              <div className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={settings.progressReports}
                  onChange={() => handleSettingChange('progressReports')}
                />
                <span className="slider"></span>
              </div>
            </div>

            <div className="setting-card">
              <div className="setting-info">
                <div className="setting-icon achievement-icon"></div>
                <div className="setting-details">
                  <h3>Goal Achievements</h3>
                  <p>Celebrate when you reach your goals</p>
                </div>
              </div>
              <div className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={settings.goalAchievements}
                  onChange={() => handleSettingChange('goalAchievements')}
                />
                <span className="slider"></span>
              </div>
            </div>

            <div className="setting-card">
              <div className="setting-info">
                <div className="setting-icon motivation-icon"></div>
                <div className="setting-details">
                  <h3>Motivation Messages</h3>
                  <p>Encouraging messages to keep you going</p>
                </div>
              </div>
              <div className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={settings.motivationMessages}
                  onChange={() => handleSettingChange('motivationMessages')}
                />
                <span className="slider"></span>
              </div>
            </div>

            <div className="setting-card">
              <div className="setting-info">
                <div className="setting-icon sound-icon"></div>
                <div className="setting-details">
                  <h3>Sound Notifications</h3>
                  <p>Play sounds for notifications</p>
                </div>
              </div>
              <div className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={settings.soundEnabled}
                  onChange={() => handleSettingChange('soundEnabled')}
                />
                <span className="slider"></span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Notifications */}
        <div className="notifications-section">
          <div className="section-header">
            <h2>🥕 Recent Notifications</h2>
            <div className="header-actions">
              <button className="action-btn" onClick={clearAllNotifications}>
                🗑️ Clear All
              </button>
            </div>
          </div>
          
          <div className="notifications-list">
            {notifications.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🔔</div>
                <h3>No notifications yet</h3>
                <p>You'll see your study reminders and achievements here</p>
              </div>
            ) : (
              notifications.map(notification => (
                <div 
                  key={notification.id} 
                  className={`notification-card ${notification.type} ${notification.read ? 'read' : 'unread'}`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="notification-icon">{notification.icon}</div>
                  <div className="notification-content">
                    <div className="notification-header">
                      <h3>{notification.title}</h3>
                      <span className="notification-time">{notification.time}</span>
                    </div>
                    <p className="notification-message">{notification.message}</p>
                  </div>
                  {!notification.read && <div className="unread-indicator"></div>}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Notifications;
