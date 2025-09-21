import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './shared.css';
import './Tasks.css';
import apiService from '../services/api';

function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, completed, pending, overdue

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.getTasks();
      console.log('📋 Tasks response:', response);
      
      if (response.success) {
        // Sort tasks by due date (latest/most recent due dates first)
        const sortedTasks = response.tasks.sort((a, b) => {
          const dateA = new Date(a.due_date);
          const dateB = new Date(b.due_date);
          return dateB - dateA; // Descending order (latest first)
        });
        setTasks(sortedTasks);
      } else {
        setError('Failed to load tasks');
      }
      
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const getFilteredTasks = () => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    switch (filter) {
      case 'completed':
        return tasks.filter(task => task.is_completed);
      case 'pending':
        return tasks.filter(task => !task.is_completed);
      case 'overdue':
        return tasks.filter(task => {
          const dueDate = new Date(task.due_date);
          return !task.is_completed && dueDate < today;
        });
      default:
        return tasks;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const taskDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    
    const diffTime = taskDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays === -1) return 'Yesterday';
    if (diffDays > 1) return `In ${diffDays} days`;
    if (diffDays < -1) return `${Math.abs(diffDays)} days ago`;
    
    return date.toLocaleDateString();
  };

  const getTaskStatusClass = (task) => {
    if (task.is_completed) return 'completed';
    
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const dueDate = new Date(task.due_date);
    const taskDueDate = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());
    
    if (taskDueDate < today) return 'overdue';
    if (taskDueDate.getTime() === today.getTime()) return 'due-today';
    
    const diffTime = taskDueDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays <= 3) return 'due-soon';
    return 'upcoming';
  };

  const getPriorityLabel = (priority) => {
    const priorityMap = {
      1: { label: 'Urgent', class: 'priority-1' },
      2: { label: 'High', class: 'priority-2' },
      3: { label: 'Medium', class: 'priority-3' },
      4: { label: 'Low', class: 'priority-4' },
      5: { label: 'Later', class: 'priority-5' }
    };
    return priorityMap[priority] || { label: 'Medium', class: 'priority-3' };
  };

  const filteredTasks = getFilteredTasks();

  return (
    <div className="page tasks-page">
      <div className="tasks-header">
        <div className="header-content">
          <h1 className="page-title">All Tasks</h1>
          <p className="page-subtitle">Complete overview of all your assignments and tasks</p>
        </div>
        <div className="header-stats">
          <div className="stat-item">
            <span className="stat-number">{tasks.length}</span>
            <span className="stat-label">Total</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{tasks.filter(t => t.is_completed).length}</span>
            <span className="stat-label">Completed</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{tasks.filter(t => !t.is_completed).length}</span>
            <span className="stat-label">Pending</span>
          </div>
        </div>
      </div>

      <div className="page-content">
        <div className="tasks-controls">
          <div className="filter-buttons">
            <button 
              className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All Tasks ({tasks.length})
            </button>
            <button 
              className={`filter-btn ${filter === 'pending' ? 'active' : ''}`}
              onClick={() => setFilter('pending')}
            >
              Pending ({tasks.filter(t => !t.is_completed).length})
            </button>
            <button 
              className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
              onClick={() => setFilter('completed')}
            >
              Completed ({tasks.filter(t => t.is_completed).length})
            </button>
            <button 
              className={`filter-btn ${filter === 'overdue' ? 'active' : ''}`}
              onClick={() => setFilter('overdue')}
            >
              Overdue ({tasks.filter(t => {
                const now = new Date();
                const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                const dueDate = new Date(t.due_date);
                return !t.is_completed && dueDate < today;
              }).length})
            </button>
          </div>
          
          <button onClick={fetchTasks} className="refresh-btn" title="Refresh tasks">
            🔄 Refresh
          </button>
        </div>

        {loading ? (
          <div className="loading-tasks">
            <div className="loading-spinner">🔄 Loading tasks...</div>
          </div>
        ) : error ? (
          <div className="error-tasks">
            <div className="error-message">❌ {error}</div>
            <button onClick={fetchTasks} className="retry-btn">🔄 Retry</button>
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="no-tasks">
            <div className="no-tasks-message">
              <div className="no-tasks-icon">📝</div>
              <h3>No tasks found</h3>
              <p>
                {filter === 'all' 
                  ? 'You have no tasks yet. Create your first task to get started!'
                  : `No ${filter} tasks found. Try a different filter.`
                }
              </p>
            </div>
          </div>
        ) : (
          <div className="tasks-list">
            {filteredTasks.map((task) => {
              const statusClass = getTaskStatusClass(task);
              const priority = getPriorityLabel(task.delta);
              
              return (
                <div key={task.id} className={`task-card ${statusClass}`}>
                  <div className="task-header">
                    <div className="task-title-section">
                      <h3 className="task-title">{task.title}</h3>
                      <div className="task-meta">
                        <span className={`priority-badge ${priority.class}`}>
                          {priority.label}
                        </span>
                        <span className="due-date">
                          📅 Due {formatDate(task.due_date)}
                        </span>
                      </div>
                    </div>
                    <div className="task-status">
                      {task.is_completed ? (
                        <span className="status-badge completed">✅ Completed</span>
                      ) : (
                        <span className={`status-badge ${statusClass}`}>
                          {statusClass === 'overdue' && '⚠️ Overdue'}
                          {statusClass === 'due-today' && '🔥 Due Today'}
                          {statusClass === 'due-soon' && '⏰ Due Soon'}
                          {statusClass === 'upcoming' && '📋 Upcoming'}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="task-content">
                    {task.description && (
                      <p className="task-description">{task.description}</p>
                    )}
                    
                    <div className="task-details">
                      <div className="detail-item">
                        <span className="detail-label">Estimated Time:</span>
                        <span className="detail-value">{task.T_n}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Progress:</span>
                        <span className="detail-value">{task.completed_so_far}%</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Created:</span>
                        <span className="detail-value">
                          {new Date(task.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="task-progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${task.completed_so_far}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default Tasks;
