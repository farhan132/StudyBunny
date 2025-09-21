import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './shared.css';
import './Notifications.css';
import apiService from '../services/api';

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [settings, setSettings] = useState({
    study_reminders: true,
    break_alerts: true,
    progress_reports: false,
    goal_achievements: true,
    motivation_messages: true,
    sound_enabled: true
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchNotifications();
    fetchNotificationSettings();
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const response = await apiService.getNotifications();
      console.log('📢 Notifications response:', response);
      
      if (response.success) {
        // Convert backend format to frontend format
        const formattedNotifications = response.notifications.map(notif => ({
          id: notif.id,
          type: notif.type,
          title: notif.title,
          message: notif.message,
          time: notif.time_ago,
          icon: notif.icon,
          read: notif.is_read
        }));
        setNotifications(formattedNotifications);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
      setError('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const fetchNotificationSettings = async () => {
    try {
      const response = await apiService.getNotificationSettings();
      if (response.success) {
        setSettings(response.settings);
      }
    } catch (error) {
      console.error('Error fetching notification settings:', error);
    }
  };

  const handleSettingChange = async (setting) => {
    const newSettings = {
      ...settings,
      [setting]: !settings[setting]
    };
    
    try {
      setSettings(newSettings);
      await apiService.updateNotificationSettings(newSettings);
      console.log('✅ Notification settings updated');
    } catch (error) {
      console.error('Error updating settings:', error);
      // Revert on error
      setSettings(settings);
    }
  };

  const markAsRead = async (id) => {
    try {
      await apiService.markNotificationRead(id);
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === id ? { ...notif, read: true } : notif
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const clearAllNotifications = async () => {
    try {
      await apiService.clearAllNotifications();
      setNotifications([]);
    } catch (error) {
      console.error('Error clearing notifications:', error);
    }
  };

  const generateTestNotifications = async () => {
    try {
      await apiService.generateTestNotifications();
      await fetchNotifications(); // Refresh the list
    } catch (error) {
      console.error('Error generating test notifications:', error);
    }
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
                  checked={settings.study_reminders}
                  onChange={() => handleSettingChange('study_reminders')}
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
                  checked={settings.break_alerts}
                  onChange={() => handleSettingChange('break_alerts')}
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
                  checked={settings.progress_reports}
                  onChange={() => handleSettingChange('progress_reports')}
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
                  checked={settings.goal_achievements}
                  onChange={() => handleSettingChange('goal_achievements')}
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
                  checked={settings.motivation_messages}
                  onChange={() => handleSettingChange('motivation_messages')}
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
                  checked={settings.sound_enabled}
                  onChange={() => handleSettingChange('sound_enabled')}
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
              <button className="action-btn" onClick={generateTestNotifications}>
                🧪 Generate Test
              </button>
              <button className="action-btn" onClick={clearAllNotifications}>
                🗑️ Clear All
              </button>
            </div>
          </div>
          
          <div className="notifications-list">
            {loading ? (
              <div className="loading-notifications">
                <div className="loading-spinner">🔄 Loading notifications...</div>
              </div>
            ) : error ? (
              <div className="error-notifications">
                <div className="error-message">❌ {error}</div>
                <button onClick={fetchNotifications} className="retry-btn">🔄 Retry</button>
              </div>
            ) : notifications.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🔔</div>
                <h3>No notifications yet</h3>
                <p>You'll see your study reminders and achievements here</p>
                <button onClick={generateTestNotifications} className="test-btn">
                  🧪 Generate Test Notifications
                </button>
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
