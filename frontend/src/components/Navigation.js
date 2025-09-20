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
          >
             Home
          </Link>
        </li>
        <li>
          <Link 
            to="/calendar" 
            className={location.pathname === '/calendar' ? 'active' : ''}
          >
             Calendar
          </Link>
        </li>
        <li>
          <Link 
            to="/statistics" 
            className={location.pathname === '/statistics' ? 'active' : ''}
          >
             Statistics
          </Link>
        </li>
        <li>
          <Link 
            to="/notifications" 
            className={location.pathname === '/notifications' ? 'active' : ''}
          >
             Notifications
          </Link>
        </li>
      </ul>
    </nav>
  );
}

export default Navigation;
