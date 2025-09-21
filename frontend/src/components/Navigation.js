import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.css';

function Navigation() {
  const location = useLocation();

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <img src="/bunny_cropped.png" alt="StudyBunny Logo" className="nav-logo" />
        <span className="nav-title">StudyBunny</span>
      </div>
      <ul className="nav-links">
        <li>
          <Link 
            to="/" 
            className={location.pathname === '/' ? 'active' : ''}
            title="Home"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3l8 6v12h-5v-6H9v6H4V9l8-6z"/>
            </svg>
          </Link>
        </li>
        <li>
          <Link 
            to="/tasks" 
            className={location.pathname === '/tasks' ? 'active' : ''}
            title="All Tasks"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
            </svg>
          </Link>
        </li>
        <li>
          <Link 
            to="/calendar" 
            className={location.pathname === '/calendar' ? 'active' : ''}
            title="Calendar"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/>
            </svg>
          </Link>
        </li>
        <li>
          <Link 
            to="/statistics" 
            className={location.pathname === '/statistics' ? 'active' : ''}
            title="Statistics"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z"/>
            </svg>
          </Link>
        </li>
        <li>
          <Link 
            to="/notifications" 
            className={location.pathname === '/notifications' ? 'active' : ''}
            title="Notifications"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
            </svg>
          </Link>
        </li>
      </ul>
    </nav>
  );
}

export default Navigation;
