import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './shared.css';
import './Calendar.css';
import apiService from '../services/api';

function Calendar() {
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(null);
  const [selectedDayTasks, setSelectedDayTasks] = useState([]);
  const [calendarDays, setCalendarDays] = useState([]);

  useEffect(() => {
    fetch14DaySchedule();
  }, []);

  // Generate calendar days when schedule changes
  useEffect(() => {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      // Calculate day index more robustly by comparing dates without time
      const todayDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
      const targetDate = new Date(year, month, day);
      const dayIndex = Math.floor((targetDate - todayDate) / (1000 * 60 * 60 * 24));
      
      // Only show tasks for the next 14 days (indices 0-13)
      const dayTasks = (dayIndex >= 0 && dayIndex < 14) ? getTasksForDay(dayIndex) : [];
      
      // Debug logging for today
      if (day === today.getDate() && month === today.getMonth()) {
        console.log('Today - dayIndex:', dayIndex, 'tasks:', dayTasks);
        console.log('Today date:', todayDate, 'Target date:', targetDate);
        console.log('Date difference:', (targetDate - todayDate) / (1000 * 60 * 60 * 24));
      }
      
      days.push({
        date: date,
        dayNumber: day,
        tasks: dayTasks,
        isToday: day === today.getDate() && month === today.getMonth()
      });
    }
    
    setCalendarDays(days);
  }, [schedule]);

  const fetch14DaySchedule = async () => {
    try {
      setLoading(true);
      const response = await apiService.get14DaySchedule();
      
      if (response.success) {
        setSchedule(response.schedule || []);
        console.log('14-day schedule loaded:', response.schedule);
        console.log('Schedule length:', response.schedule?.length);
        console.log('Today tasks (index 0):', response.schedule?.[0]);
      } else {
        console.log('No schedule data available');
      }
    } catch (error) {
      console.error('Error fetching 14-day schedule:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get tasks for a specific day from the 14-day schedule
  const getTasksForDay = (dayIndex) => {
    console.log('getTasksForDay called with dayIndex:', dayIndex, 'schedule length:', schedule?.length);
    if (schedule && schedule.length > dayIndex && dayIndex >= 0) {
      const tasks = schedule[dayIndex] || [];
      console.log('Returning tasks for day', dayIndex, ':', tasks);
      return tasks;
    }
    console.log('No tasks for day', dayIndex);
    return [];
  };

  // Debug: Log the schedule data
  console.log('Current schedule state:', schedule);
  console.log('Schedule length:', schedule?.length);
  console.log('Day 0 tasks:', schedule?.[0]);
  console.log('Day 1 tasks:', schedule?.[1]);
  console.log('Calendar days with tasks:', calendarDays.filter(day => day && day.tasks.length > 0));

  const handleDayClick = (day) => {
    console.log('Day clicked:', day);
    try {
      if (day && day.tasks.length > 0) {
        console.log('Setting selected day with tasks:', day.tasks);
        setSelectedDay(day);
        setSelectedDayTasks(day.tasks);
      } else {
        console.log('Setting selected day without tasks');
        setSelectedDay(day);
        setSelectedDayTasks([]);
      }
    } catch (error) {
      console.error('Error handling day click:', error);
    }
  };

  const closeDayDetails = () => {
    setSelectedDay(null);
    setSelectedDayTasks([]);
  };

  const formatTime = (timeString) => {
    console.log('formatTime called with:', timeString, 'type:', typeof timeString);
    
    if (!timeString) return 'Not specified';
    
    try {
      const seconds = parseFloat(timeString);
      console.log('Parsed seconds:', seconds);
      
      if (isNaN(seconds) || seconds < 0) {
        console.log('Invalid seconds value:', seconds);
        return 'Invalid time';
      }
      
      // Convert to total minutes and round up to nearest 5-minute interval
      const totalMinutes = Math.ceil(seconds / 60);
      const roundedMinutes = Math.ceil(totalMinutes / 5) * 5;
      
      const hours = Math.floor(roundedMinutes / 60);
      const minutes = roundedMinutes % 60;
      
      console.log('Total minutes:', totalMinutes);
      console.log('Rounded minutes:', roundedMinutes);
      console.log('Final hours:', hours, 'Final minutes:', minutes);
      
      const result = `${hours}:${minutes.toString().padStart(2, '0')}:00`;
      console.log('Final result:', result);
      return result;
    } catch (error) {
      console.error('Error formatting time:', error, 'Input:', timeString);
      return 'Invalid time';
    }
  };

  const formatStartTime = (timeString) => {
    if (!timeString) return 'Not specified';
    // Extract just the time part (HH:MM:SS) from the timestamp
    const timeMatch = timeString.match(/(\d{2}:\d{2}:\d{2})/);
    return timeMatch ? timeMatch[1] : timeString;
  };

  return (
    <div className="page calendar-page">
      <div className="calendar-header">
        <div className="header-content">
          <div className="calendar-title">
            <div className="desktop-letters">
              <div className="post-it-letter">C</div>
              <div className="post-it-letter">A</div>
              <div className="post-it-letter">L</div>
              <div className="post-it-letter">E</div>
              <div className="post-it-letter">N</div>
              <div className="post-it-letter">D</div>
              <div className="post-it-letter">A</div>
              <div className="post-it-letter">R</div>
            </div>
            <div className="mobile-letters">
              <div className="mobile-word">
                <div className="post-it-letter">C</div>
                <div className="post-it-letter">A</div>
                <div className="post-it-letter">L</div>
                <div className="post-it-letter">E</div>
                <div className="post-it-letter">N</div>
              </div>
              <div className="mobile-word">
                <div className="post-it-letter">D</div>
                <div className="post-it-letter">A</div>
                <div className="post-it-letter">R</div>
              </div>
            </div>
          </div>
          <p className="page-subtitle">Manage your study schedule and upcoming events</p>
        </div>
        <div className="carrot-decoration carrot-left">🥕</div>
        <div className="carrot-decoration carrot-right">🥕</div>
      </div>
      
      <div className="page-content">
        <div className="calendar-container">
          {loading && (
            <div className="loading-indicator">
              <div className="loading-spinner"></div>
              <p>Loading your 14-day schedule...</p>
            </div>
          )}
          <div className="calendar-grid">
            <div className="calendar-day-header">Mon</div>
            <div className="calendar-day-header">Tue</div>
            <div className="calendar-day-header">Wed</div>
            <div className="calendar-day-header">Thu</div>
            <div className="calendar-day-header">Fri</div>
            <div className="calendar-day-header">Sat</div>
            <div className="calendar-day-header">Sun</div>
            
            {calendarDays.map((day, index) => {
              if (!day) {
                return <div key={index} className="calendar-day empty"></div>;
              }
              
              return (
                <div 
                  key={index} 
                  className={`calendar-day ${day.isToday ? 'today' : ''} ${selectedDay && selectedDay.dayNumber === day.dayNumber ? 'selected' : ''}`}
                  title={day.tasks.length > 0 ? `${day.tasks.length} tasks scheduled` : 'No tasks'}
                  onClick={() => handleDayClick(day)}
                >
                  <div className="day-number">{day.dayNumber}</div>
                  {day.tasks.length > 0 && (
                    <div className="task-indicators">
                      {day.tasks.slice(0, 2).map((task, taskIndex) => (
                        <div 
                          key={taskIndex}
                          className="task-indicator"
                          title={task.task_title || 'Task'}
                        >
                          {task.task_title ? task.task_title.substring(0, 3) : 'T'}
                        </div>
                      ))}
                      {day.tasks.length > 2 && (
                        <div className="more-tasks">+{day.tasks.length - 2}</div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          
          {schedule.length > 0 && (
            <div className="schedule-info">
              <div className="schedule-info-content">
                <h3>📊 Schedule Overview</h3>
                <p>Total days with tasks: {schedule.filter(day => day && day.length > 0).length}</p>
              </div>
            </div>
          )}
        </div>

        {/* Day Details Modal */}
        {selectedDay && (
          <div className="day-details-modal">
            <div className="day-details-content">
              <div className="day-details-header">
                <h3>
                  {selectedDay.date && selectedDay.date instanceof Date 
                    ? selectedDay.date.toLocaleDateString('en-US', { 
                        weekday: 'long', 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })
                    : `Day ${selectedDay.dayNumber}`
                  }
                </h3>
                <button className="close-btn" onClick={closeDayDetails}>×</button>
              </div>
              
              {selectedDayTasks.length > 0 ? (
                <div className="day-tasks">
                  <h4>Scheduled Tasks ({selectedDayTasks.length})</h4>
                  {selectedDayTasks.map((task, index) => {
                    console.log('Rendering task:', task);
                    console.log('task.time_allotted:', task.time_allotted, 'type:', typeof task.time_allotted);
                    return (
                      <div key={index} className="task-item">
                        <div className="task-name">{task.task_title || 'Unnamed Task'}</div>
                        <div className="task-details">
                          <span className="task-time">
                            Study Time: {formatTime(task.time_allotted)}
                          </span>
                          {task.priority && (
                            <span className="task-priority">
                              Priority: {task.priority}
                            </span>
                          )}
                        </div>
                        {task.reason && (
                          <div className="task-reason">
                            Reason: {task.reason}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="no-tasks">
                  <p>No tasks scheduled for this day</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Calendar;
