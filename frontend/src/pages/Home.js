import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import './shared.css';
import './Home.css';

function Home() {
  const [assignments, setAssignments] = useState([]);
  const [completedAssignments, setCompletedAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState(null);
  const [newAssignment, setNewAssignment] = useState({
    name: '',
    description: '',
    dueDate: new Date().toISOString().split('T')[0], // Today's date in YYYY-MM-DD format
    priority: 'medium',
    subject: '',
    estimatedHours: 0,
    estimatedMinutes: 0,
    completionPercentage: 0
  });

  // Fetch assignments from backend on component mount
  useEffect(() => {
    fetchAssignments();
    
    // Cleanup function to clear timeouts when component unmounts
    return () => {
      if (window.progressTimeouts) {
        Object.values(window.progressTimeouts).forEach(timeoutId => {
          clearTimeout(timeoutId);
        });
        window.progressTimeouts = {};
      }
    };
  }, []);

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      // Backend API call to get all assignments
      const response = await fetch('/api/assignments/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Add authentication headers if needed
          // 'Authorization': Bearer 
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const allAssignments = data.assignments || [];
        const pending = allAssignments.filter(a => a.status !== 'completed');
        const completed = allAssignments.filter(a => a.status === 'completed');
        setAssignments(pending);
        setCompletedAssignments(completed);
      } else {
        console.error('Failed to fetch assignments');
        // Mock data for development
        const mockAssignments = [
          {
            id: 1,
            name: 'English Paper',
            description: 'Write a 5-page essay on climate change',
            dueDate: '2024-09-21',
            priority: 'high',
            status: 'pending',
            subject: 'English',
            estimatedTime: '4:00:00',
            completionPercentage: 50
          },
          {
            id: 2,
            name: 'Math Problem Set',
            description: 'Complete calculus exercises 1-20',
            dueDate: '2025-09-25',
            priority: 'medium',
            status: 'pending',
            subject: 'Mathematics',
            estimatedTime: '2:30:00',
            completionPercentage: 25
          },
          {
            id: 3,
            name: 'History Research',
            description: 'Research paper on World War II',
            dueDate: '2025-09-28',
            priority: 'low',
            status: 'completed',
            subject: 'History',
            estimatedTime: '6:00:00',
            completionPercentage: 100
          }
        ];
        const pending = mockAssignments.filter(a => a.status !== 'completed');
        const completed = mockAssignments.filter(a => a.status === 'completed');
        setAssignments(pending);
        setCompletedAssignments(completed);
      }
    } catch (error) {
      console.error('Error fetching assignments:', error);
      // Use mock data as fallback
      const fallbackAssignments = [
        {
          id: 1,
          name: 'English Paper',
          description: 'Write a 5-page essay on climate change',
          dueDate: '2024-09-21',
          priority: 'high',
          status: 'pending',
          subject: 'English',
          estimatedTime: '4:00:00',
          completionPercentage: 50
        }
      ];
      const pending = fallbackAssignments.filter(a => a.status !== 'completed');
      const completed = fallbackAssignments.filter(a => a.status === 'completed');
      setAssignments(pending);
      setCompletedAssignments(completed);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAssignment = async (e) => {
    e.preventDefault();
    
    // Validate that time is not 0h 0m using HTML5 validation
    if (newAssignment.estimatedHours === 0 && newAssignment.estimatedMinutes === 0) {
      // Find the hours select element and trigger validation
      const hoursSelect = document.querySelector('select[name="estimatedHours"]');
      if (hoursSelect) {
        hoursSelect.setCustomValidity('Please select a time greater than 0 hours and 0 minutes.');
        hoursSelect.reportValidity();
      }
      return;
    }
    
    // Convert hours and minutes to HH:MM:SS format
    const estimatedTime = `${newAssignment.estimatedHours.toString().padStart(2, '0')}:${newAssignment.estimatedMinutes.toString().padStart(2, '0')}:00`;
    
    try {
      // Backend API call to create new assignment
      const response = await fetch('/api/assignments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add authentication headers if needed
          // 'Authorization': Bearer 
        },
        body: JSON.stringify({
          ...newAssignment,
          estimatedTime: estimatedTime,
          status: 'pending'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAssignments([...assignments, data.assignment]);
      } else {
        console.error('Failed to create assignment');
        // Add to local state if backend fails
        const newId = Math.max(...assignments.map(a => a.id), 0) + 1;
        setAssignments([...assignments, { 
          ...newAssignment, 
          id: newId, 
          estimatedTime: estimatedTime,
          status: 'pending'
        }]);
      }
      
      // Reset form
      setNewAssignment({ 
        name: '', 
        description: '', 
        dueDate: new Date().toISOString().split('T')[0], // Today's date
        priority: 'medium', 
        subject: '',
        estimatedHours: 0,
        estimatedMinutes: 0,
        completionPercentage: 0
      });
      setShowAddForm(false);
    } catch (error) {
      console.error('Error creating assignment:', error);
      // Add to local state as fallback
      const newId = Math.max(...assignments.map(a => a.id), 0) + 1;
      setAssignments([...assignments, { 
        ...newAssignment, 
        id: newId, 
        estimatedTime: estimatedTime,
        status: 'pending'
      }]);
      setNewAssignment({ 
        name: '', 
        description: '', 
        dueDate: new Date().toISOString().split('T')[0], // Today's date
        priority: 'medium', 
        subject: '',
        estimatedHours: 0,
        estimatedMinutes: 0,
        completionPercentage: 0
      });
      setShowAddForm(false);
    }
  };

  const handleDeleteAssignment = useCallback(async (assignmentId) => {
    // Update UI immediately
    setAssignments(prevAssignments => prevAssignments.filter(a => a.id !== assignmentId));

    // API call in background
    try {
      const response = await fetch(`/api/assignments/${assignmentId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          // Add authentication headers if needed
          // 'Authorization': 'Bearer <token>'
        }
      });

      if (!response.ok) {
        console.error('Failed to delete assignment');
      }
    } catch (error) {
      console.error('Error deleting assignment:', error);
    }
  }, []);

  const handleDeleteCompletedAssignment = useCallback(async (assignmentId) => {
    // Update UI immediately
    setCompletedAssignments(prevCompleted => prevCompleted.filter(a => a.id !== assignmentId));

    // API call in background
    try {
      const response = await fetch(`/api/assignments/${assignmentId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          // Add authentication headers if needed
          // 'Authorization': 'Bearer <token>'
        }
      });

      if (!response.ok) {
        console.error('Failed to delete assignment');
      }
    } catch (error) {
      console.error('Error deleting assignment:', error);
    }
  }, []);

  const handleUndoComplete = useCallback(async (assignmentId) => {
    // Update UI immediately
    setCompletedAssignments(prevCompleted => {
      const assignmentToMove = prevCompleted.find(a => a.id === assignmentId);
      if (assignmentToMove) {
        const pendingAssignment = { ...assignmentToMove, status: 'pending' };
        setAssignments(prevAssignments => [...prevAssignments, pendingAssignment]);
        return prevCompleted.filter(a => a.id !== assignmentId);
      }
      return prevCompleted;
    });

    // API call in background
    try {
      const response = await fetch(`/api/assignments/${assignmentId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'pending' })
      });

      if (!response.ok) {
        console.error('Failed to update assignment on server');
      }
    } catch (error) {
      console.error('Error undoing completion:', error);
    }
  }, []);

  const handleMarkComplete = useCallback(async (assignmentId) => {
    // Update UI immediately for better responsiveness
    setAssignments(prevAssignments => {
      const assignmentToMove = prevAssignments.find(a => a.id === assignmentId);
      if (assignmentToMove) {
        const completedAssignment = { ...assignmentToMove, status: 'completed', completionPercentage: 100 };
        // Add to completed assignments immediately
        setCompletedAssignments(prevCompleted => {
          // Check if assignment already exists to prevent duplicates
          const exists = prevCompleted.some(a => a.id === assignmentId);
          if (!exists) {
            return [...prevCompleted, completedAssignment];
          }
          return prevCompleted;
        });
        return prevAssignments.filter(a => a.id !== assignmentId);
      }
      return prevAssignments;
    });

    // API call in background
    try {
      const response = await fetch(`/api/assignments/${assignmentId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'completed', completionPercentage: 100 })
      });

      if (!response.ok) {
        console.error('Failed to update assignment on server');
      }
    } catch (error) {
      console.error('Error updating assignment:', error);
    }
  }, []);

  const handleUpdateProgress = useCallback((assignmentId, newPercentage) => {
    // Update local state immediately for smooth UI using functional update
    setAssignments(prevAssignments => 
      prevAssignments.map(a => 
        a.id === assignmentId ? { ...a, completionPercentage: newPercentage } : a
      )
    );
  }, []);

  // Debounced API call to prevent too many requests
  const debouncedApiCall = useCallback(
    (assignmentId, newPercentage) => {
      // Clear any existing timeout for this assignment
      if (window.progressTimeouts && window.progressTimeouts[assignmentId]) {
        clearTimeout(window.progressTimeouts[assignmentId]);
      }
      
      // Initialize timeouts object if it doesn't exist
      if (!window.progressTimeouts) {
        window.progressTimeouts = {};
      }
      
      // Set new timeout
      window.progressTimeouts[assignmentId] = setTimeout(async () => {
        try {
          const response = await fetch(`/api/assignments/${assignmentId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completionPercentage: newPercentage })
          });

          if (!response.ok) {
            console.error('Failed to update progress on server');
          }
        } catch (error) {
          console.error('Error updating progress:', error);
        } finally {
          // Clean up timeout reference
          if (window.progressTimeouts) {
            delete window.progressTimeouts[assignmentId];
          }
        }
      }, 500); // Increased delay to 500ms for better performance
    },
    []
  );

  const handleProgressChange = useCallback((assignmentId, newPercentage) => {
    // Update local state immediately for smooth UI
    handleUpdateProgress(assignmentId, newPercentage);
    
    // Debounced API call
    debouncedApiCall(assignmentId, newPercentage);
  }, [handleUpdateProgress, debouncedApiCall]);

  const handleEditAssignment = useCallback((assignment) => {
    setEditingAssignment(assignment);
  }, []);

  const handleCancelEdit = useCallback(() => {
    setEditingAssignment(null);
  }, []);

  const handleSaveEdit = useCallback(async (updatedAssignment) => {
    try {
      // Update local state immediately
      setAssignments(prevAssignments => 
        prevAssignments.map(a => 
          a.id === updatedAssignment.id ? updatedAssignment : a
        )
      );
      setCompletedAssignments(prevCompleted => 
        prevCompleted.map(a => 
          a.id === updatedAssignment.id ? updatedAssignment : a
        )
      );

      // API call in background
      const response = await fetch(`/api/assignments/${updatedAssignment.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedAssignment)
      });

      if (!response.ok) {
        console.error('Failed to update assignment on server');
      }
    } catch (error) {
      console.error('Error updating assignment:', error);
    } finally {
      setEditingAssignment(null);
    }
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const month = date.toLocaleDateString('en-US', { month: 'short' });
    const day = date.getDate();
    return `${month} ${day}`;
  };

  const formatTimeLeft = (timeString) => {
    // Parse HH:MM:SS format
    const [hours, minutes, seconds] = timeString.split(':').map(Number);
    const totalMinutes = hours * 60 + minutes;
    
    if (totalMinutes === 0) {
      return "0m left";
    }
    
    const hoursLeft = Math.floor(totalMinutes / 60);
    const minutesLeft = totalMinutes % 60;
    
    if (hoursLeft > 0 && minutesLeft > 0) {
      return `${hoursLeft}h ${minutesLeft}m left`;
    } else if (hoursLeft > 0) {
      return `${hoursLeft}h left`;
    } else {
      return `${minutesLeft}m left`;
    }
  };

  const isOverdue = (dueDate) => {
    const due = new Date(dueDate);
    const now = new Date();
    return due < now && due.toDateString() !== now.toDateString();
  };

  // Sort assignments by priority from very high to low
  const sortAssignmentsByPriority = (assignments) => {
    const priorityOrder = { 'very high': 4, 'high': 3, 'medium': 2, 'low': 1 };
    return [...assignments].sort((a, b) => {
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  };

  // Edit Assignment Form Component
  const EditAssignmentForm = ({ assignment, onSave, onCancel }) => {
    const [editData, setEditData] = useState({
      name: assignment.name,
      description: assignment.description || '',
      dueDate: assignment.dueDate,
      priority: assignment.priority,
      subject: assignment.subject || '',
      estimatedHours: Math.floor(parseInt(assignment.estimatedTime?.split(':')[0]) || 0),
      estimatedMinutes: parseInt(assignment.estimatedTime?.split(':')[1]) || 0,
      completionPercentage: assignment.completionPercentage
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      const estimatedTime = `${editData.estimatedHours.toString().padStart(2, '0')}:${editData.estimatedMinutes.toString().padStart(2, '0')}:00`;
      onSave({
        ...assignment,
        ...editData,
        estimatedTime: estimatedTime
      });
    };

    return (
      <div className="edit-assignment-form">
        <h4>Edit Assignment</h4>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name:</label>
            <input
              type="text"
              value={editData.name}
              onChange={(e) => setEditData({...editData, name: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <label>Description:</label>
            <input
              type="text"
              value={editData.description}
              onChange={(e) => setEditData({...editData, description: e.target.value})}
            />
          </div>
          <div className="form-group">
            <label>Due Date:</label>
            <input
              type="date"
              value={editData.dueDate}
              onChange={(e) => setEditData({...editData, dueDate: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <label>Priority:</label>
            <select
              value={editData.priority}
              onChange={(e) => setEditData({...editData, priority: e.target.value})}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="very high">Very High</option>
            </select>
          </div>
          <div className="form-group">
            <label>Subject:</label>
            <input
              type="text"
              value={editData.subject}
              onChange={(e) => setEditData({...editData, subject: e.target.value})}
            />
          </div>
          <div className="form-group">
            <label>Estimated Time:</label>
            <div className="time-inputs">
              <div className="time-input-group">
                <label>Hours:</label>
                <select
                  value={editData.estimatedHours}
                  onChange={(e) => setEditData({...editData, estimatedHours: parseInt(e.target.value)})}
                >
                  {Array.from({ length: 41 }, (_, i) => (
                    <option key={i} value={i}>{i}h</option>
                  ))}
                </select>
              </div>
              <div className="time-input-group">
                <label>Minutes:</label>
                <select
                  value={editData.estimatedMinutes}
                  onChange={(e) => setEditData({...editData, estimatedMinutes: parseInt(e.target.value)})}
                >
                  {Array.from({ length: 4 }, (_, i) => {
                    const minutes = i * 15;
                    return (
                      <option key={minutes} value={minutes}>{minutes}m</option>
                    );
                  })}
                </select>
              </div>
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Save Changes</button>
            <button type="button" className="btn btn-secondary" onClick={onCancel}>Cancel</button>
          </div>
        </form>
      </div>
    );
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Welcome to StudyBunny</h1>
        <p>Your personal study companion to help you stay organized and productive!</p>
      </div>
      
      <div className="assignments-section">
        <div className="section-header">
          <h2>Your Assignments</h2>
          <button 
            className="btn btn-primary add-btn"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            + Add Assignment
          </button>
        </div>

        {showAddForm && (
          <div className="add-assignment-form">
            <h3>Add New Assignment</h3>
            <form onSubmit={handleAddAssignment}>
              <div className="form-group">
                <label>Name:</label>
                <input
                  type="text"
                  value={newAssignment.name}
                  onChange={(e) => setNewAssignment({...newAssignment, name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Due Date:</label>
                <input
                  type="date"
                  value={newAssignment.dueDate}
                  onChange={(e) => setNewAssignment({...newAssignment, dueDate: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Priority:</label>
                <select
                  value={newAssignment.priority}
                  onChange={(e) => setNewAssignment({...newAssignment, priority: e.target.value})}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="very high">Very High</option>
                </select>
              </div>
              <div className="form-group">
                <label>Estimated Time:</label>
                <div className="time-inputs">
                  <div className="time-input-group">
                    <label>Hours:</label>
                    <select
                      name="estimatedHours"
                      value={newAssignment.estimatedHours}
                      onChange={(e) => {
                        setNewAssignment({...newAssignment, estimatedHours: parseInt(e.target.value)});
                        e.target.setCustomValidity(''); // Clear custom validation
                      }}
                      required
                    >
                      {Array.from({ length: 41 }, (_, i) => (
                        <option key={i} value={i}>{i}h</option>
                      ))}
                    </select>
                  </div>
                  <div className="time-input-group">
                    <label>Minutes:</label>
                    <select
                      name="estimatedMinutes"
                      value={newAssignment.estimatedMinutes}
                      onChange={(e) => {
                        setNewAssignment({...newAssignment, estimatedMinutes: parseInt(e.target.value)});
                        e.target.setCustomValidity(''); // Clear custom validation
                      }}
                      required
                    >
                      {Array.from({ length: 4 }, (_, i) => {
                        const minutes = i * 15;
                        return (
                          <option key={minutes} value={minutes}>{minutes}m</option>
                        );
                      })}
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="form-actions">
                <button type="submit" className="btn btn-primary">Add Assignment</button>
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        )}

        {loading ? (
          <div className="loading">Loading assignments...</div>
        ) : (
          <div className="assignments-grid">
            {assignments.length === 0 ? (
              <div className="no-assignments">
                <p>No assignments yet. Click the + button to add your first assignment!</p>
              </div>
            ) : (
              sortAssignmentsByPriority(assignments).map(assignment => (
                <div key={assignment.id} className="assignment-card" data-priority={assignment.priority}>
                  <div className="assignment-actions">
                    {assignment.status !== 'completed' && (
                      <button 
                        className="complete-btn"
                        onClick={() => handleMarkComplete(assignment.id)}
                        title="Mark as complete"
                      >
                        ✓
                      </button>
                    )}
                    <button 
                      className="edit-btn"
                      onClick={() => handleEditAssignment(assignment)}
                      title="Edit assignment"
                    >
                      ✏️
                    </button>
                    <button 
                      className="delete-btn"
                      onClick={() => handleDeleteAssignment(assignment.id)}
                      title="Delete assignment"
                    >
                      🗑
                    </button>
                  </div>

                  <div className="assignment-header">
                    <h3 className="assignment-title">{assignment.name}</h3>
                    <div className="assignment-time">{formatTimeLeft(assignment.estimatedTime)}</div>
                  </div>
                  
                  <div className="progress-section">
                    <div className="progress-slider-container">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={assignment.completionPercentage}
                        onChange={(e) => handleProgressChange(assignment.id, parseInt(e.target.value))}
                        className="progress-slider"
                        title="Adjust completion percentage"
                        style={{
                          backgroundImage: `linear-gradient(to right, ${
                            assignment.priority === 'low' ? '#35854d' : 
                            assignment.priority === 'medium' ? '#bcab12' : 
                            assignment.priority === 'high' ? '#cc4444' : '#d63031'
                          } ${assignment.completionPercentage}%, transparent ${assignment.completionPercentage}%)`
                        }}
                      />
                    </div>
                    <div className="progress-percentage">{assignment.completionPercentage}%</div>
                  </div>

                  <div className="assignment-footer">
                    <div className="assignment-due-date">
                      {formatDate(assignment.dueDate)}
                      {isOverdue(assignment.dueDate) && <span className="overdue-badge">OVERDUE</span>}
                    </div>
                  </div>
                  
                  {assignment.status === 'completed' && (
                    <div className="completed-badge"> Completed</div>
                  )}
                  
                  {editingAssignment && editingAssignment.id === assignment.id && (
                    <EditAssignmentForm
                      assignment={assignment}
                      onSave={handleSaveEdit}
                      onCancel={handleCancelEdit}
                    />
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Completed Assignments Section */}
      <div className="assignments-section">
        <div className="section-header">
          <h2>Completed Assignments</h2>
        </div>

        {loading ? (
          <div className="loading">Loading completed assignments...</div>
        ) : (
          <div className="assignments-grid">
            {completedAssignments.length === 0 ? (
              <div className="no-assignments">
                <p>No completed assignments yet. Complete some assignments to see them here!</p>
              </div>
            ) : (
              sortAssignmentsByPriority(completedAssignments).map(assignment => (
                <div key={assignment.id} className="assignment-card completed-assignment" data-priority={assignment.priority}>
                  <div className="assignment-actions">
                    <button 
                      className="undo-btn"
                      onClick={() => handleUndoComplete(assignment.id)}
                      title="Undo completion"
                    >
                      ↶
                    </button>
                    <button 
                      className="edit-btn"
                      onClick={() => handleEditAssignment(assignment)}
                      title="Edit assignment"
                    >
                      ✏️
                    </button>
                    <button 
                      className="delete-btn"
                      onClick={() => handleDeleteCompletedAssignment(assignment.id)}
                      title="Delete assignment"
                    >
                      🗑
                    </button>
                  </div>

                  <div className="assignment-header">
                    <h3 className="assignment-title">{assignment.name}</h3>
                    <div className="assignment-time">{formatTimeLeft(assignment.estimatedTime)}</div>
                  </div>
                  
                  <div className="progress-section">
                    <div className="progress-slider-container">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={assignment.completionPercentage}
                        onChange={(e) => handleProgressChange(assignment.id, parseInt(e.target.value))}
                        className="progress-slider"
                        title="Adjust completion percentage"
                        style={{
                          backgroundImage: `linear-gradient(to right, ${
                            assignment.priority === 'low' ? '#35854d' : 
                            assignment.priority === 'medium' ? '#bcab12' : 
                            assignment.priority === 'high' ? '#cc4444' : '#d63031'
                          } ${assignment.completionPercentage}%, transparent ${assignment.completionPercentage}%)`
                        }}
                      />
                    </div>
                    <div className="progress-percentage">{assignment.completionPercentage}%</div>
                  </div>

                  <div className="assignment-footer">
                    <div className="assignment-due-date">
                      {formatDate(assignment.dueDate)}
                    </div>
                  </div>
                  
                  <div className="completed-badge">✓ Completed</div>
                  
                  {editingAssignment && editingAssignment.id === assignment.id && (
                    <EditAssignmentForm
                      assignment={assignment}
                      onSave={handleSaveEdit}
                      onCancel={handleCancelEdit}
                    />
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;
