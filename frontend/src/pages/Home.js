import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import './shared.css';
import './Home.css';
import runningProgress from './runningProgress.png';
import apiService from '../services/api';

function Home() {
  const [assignments, setAssignments] = useState([]);
  const [completedAssignments, setCompletedAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState(null);
  const [scheduleData, setScheduleData] = useState([]);
  const [scheduleTaskProgress, setScheduleTaskProgress] = useState({}); // Track progress for schedule tasks
  const [completedScheduleTasks, setCompletedScheduleTasks] = useState({}); // Track completed schedule tasks
  const [dashboardStats, setDashboardStats] = useState({
    performanceScore: 0,
    userIntensity: 50,
    workHoursPercentile: 0,
    assignmentCompletionPercent: 0,
    howAmIDoingScore: 0
  });

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
    fetchDashboardStats();
    fetch14DaySchedule();
    
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


  const fetchDashboardStats = async () => {
    try {
      console.log('🔄 Fetching dashboard stats...');
      // Fetch dashboard stats from backend
      const response = await fetch('/api/study/dashboard-stats/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('📊 Dashboard stats received:', data);
        console.log('📊 Personal Score from API:', data.how_am_i_doing_score);
        console.log('📊 Current state before update:', dashboardStats.howAmIDoingScore);
        
        setDashboardStats(prev => {
          const newStats = {
            ...prev,
            performanceScore: data.performance_score || 0,
            workHoursPercentile: data.work_hours_percentile || 0,
            assignmentCompletionPercent: data.assignment_completion_percent || 0,
            howAmIDoingScore: data.how_am_i_doing_score || 0
          };
          console.log('📊 Setting new dashboard stats:', newStats);
          console.log('📊 New Personal Score:', newStats.howAmIDoingScore);
          return newStats;
        });
        
        console.log('✅ Dashboard stats updated in state');
      } else {
        console.error('❌ Failed to fetch dashboard stats');
        // Keep current stats if backend fails
      }
    } catch (error) {
      console.error('❌ Error fetching dashboard stats:', error);
      // Keep current stats if backend fails
    }

    // Load current intensity from backend
    try {
      const intensityData = await apiService.getIntensity();
      
      if (intensityData && intensityData.intensity !== undefined) {
        const frontendIntensity = backendToFrontendIntensity(intensityData.intensity);
        setDashboardStats(prev => ({
          ...prev,
          userIntensity: frontendIntensity
        }));
        console.log(`Loaded intensity: ${intensityData.intensity} -> ${frontendIntensity}%`);
      }
    } catch (error) {
      console.error('Error fetching intensity:', error);
    }
  };

  const fetch14DaySchedule = async () => {
    try {
      const response = await apiService.get14DaySchedule();
      if (response.success) {
        setScheduleData(response.schedule || []);
      }
    } catch (error) {
      console.error('Error fetching 14-day schedule:', error);
    }
  };

  const getTodayAllocatedTime = (taskTitle) => {
    if (!scheduleData || scheduleData.length === 0) return null;
    
    // Get today's tasks (index 0 in the 14-day schedule)
    const todayTasks = scheduleData[0] || [];
    
    // Find the task with matching title
    const task = todayTasks.find(t => t.task_title === taskTitle);
    
    if (task && task.time_allotted) {
      // Convert seconds to HH:MM:SS format with 5-minute rounding
      const seconds = parseFloat(task.time_allotted);
      let hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = Math.floor(seconds % 60);
      
      // Round up to the nearest 5-minute period
      let roundedMinutes = minutes;
      if (secs > 0) {
        roundedMinutes += 1; // Round up if there are any seconds
      }
      // Round up to next 5-minute mark
      roundedMinutes = Math.ceil(roundedMinutes / 5) * 5;
      
      // Handle hour overflow
      if (roundedMinutes >= 60) {
        const additionalHours = Math.floor(roundedMinutes / 60);
        hours += additionalHours;
        roundedMinutes = roundedMinutes % 60;
      }
      
      return `${hours}:${roundedMinutes.toString().padStart(2, '0')}:00`;
    }
    
    return null;
  };

  // Calculate color based on time ratio (X/E)
  const getTaskColor = (task) => {
    if (!task.time_allotted || !task.time_needed_total) return 'green';
    
    const timeAllotted = parseFloat(task.time_allotted); // X - free time allocated
    const timeNeeded = parseFloat(task.time_needed_total); // E - time needed
    
    if (timeNeeded === 0) return 'green';
    
    const ratio = timeAllotted / timeNeeded;
    
    if (ratio <= 2) return 'red';
    if (ratio <= 10) return 'yellow';
    return 'green';
  };

  // Get today's scheduled tasks from the 14-day schedule
  const getTodaysScheduledTasks = () => {
    if (!scheduleData || scheduleData.length === 0) {
      console.log('No schedule data available');
      return [];
    }
    
    // Get today's tasks (index 0 in the 14-day schedule)
    const todayTasks = scheduleData[0] || [];
    console.log('Today\'s tasks from schedule:', todayTasks);
    
    // Convert schedule tasks to assignment format for display
    return todayTasks.map(task => {
      // Format time from seconds to HH:MM:SS string
      let formattedTime = "0:00:00";
      if (task.time_allotted) {
        const seconds = parseFloat(task.time_allotted);
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        // Round up to the nearest 5-minute period
        let roundedMinutes = minutes;
        if (secs > 0) {
          roundedMinutes += 1;
        }
        roundedMinutes = Math.ceil(roundedMinutes / 5) * 5;
        
        // Handle hour overflow
        if (roundedMinutes >= 60) {
          const additionalHours = Math.floor(roundedMinutes / 60);
          const finalHours = hours + additionalHours;
          const finalMinutes = roundedMinutes % 60;
          formattedTime = `${finalHours}:${finalMinutes.toString().padStart(2, '0')}:00`;
        } else {
          formattedTime = `${hours}:${roundedMinutes.toString().padStart(2, '0')}:00`;
        }
      }
      
      // Calculate projected percentage for today based on time allocation
      let projectedPercentage = 0;
      if (task.time_needed_total && task.time_allotted) {
        // Parse time_needed_total (format: "12:00:00")
        const timeNeededParts = task.time_needed_total.split(':');
        const timeNeededSeconds = (parseInt(timeNeededParts[0]) * 3600) + 
                                 (parseInt(timeNeededParts[1]) * 60) + 
                                 parseInt(timeNeededParts[2]);
        
        // Parse time_allotted (in seconds)
        const timeAllotted = parseFloat(task.time_allotted);
        
        if (timeNeededSeconds > 0) {
          // Calculate what percentage of the total task should be done today
          const todayAllocationPercentage = (timeAllotted / timeNeededSeconds) * 100;
          
          // Add this to the current progress to get the target progress
          const currentProgress = scheduleTaskProgress[`schedule_${task.task_id}`] !== undefined 
            ? scheduleTaskProgress[`schedule_${task.task_id}`] 
            : Math.round(task.completion_before || 0);
          
          projectedPercentage = Math.min(100, currentProgress + todayAllocationPercentage);
          // Round to avoid long decimal numbers
          projectedPercentage = Math.round(projectedPercentage);
        }
      }
      
      // Check if we have a local update for this task
      const taskId = `schedule_${task.task_id}`;
      const currentProgress = scheduleTaskProgress[taskId] !== undefined 
        ? scheduleTaskProgress[taskId] 
        : Math.round(task.completion_before || 0);
      
      console.log('getTodaysScheduledTasks - task:', task.task_id, 'scheduleTaskProgress:', scheduleTaskProgress[taskId], 'currentProgress:', currentProgress);
      
      // Calculate color based on time ratio
      const color = getTaskColor(task);
      
      return {
        id: `schedule_${task.task_id}`,
        name: task.task_title,
        description: task.task_description || '',
        dueDate: task.due_date,
        priority: task.priority,
        subject: '', // Not available in schedule data
        estimatedTime: formattedTime, // Now a formatted string
        completionPercentage: currentProgress, // Use local update if available
        projectedPercentage: Math.round(projectedPercentage), // Add projected percentage
        status: currentProgress >= 100 ? 'completed' : 'pending',
        isScheduled: true, // Flag to indicate this is from schedule
        color: color // Add color property
      };
    });
  };

  // Get today's pending scheduled tasks (not completed)
  const getTodaysPendingTasks = () => {
    return getTodaysScheduledTasks().filter(task => task.status !== 'completed');
  };

  // Get today's completed scheduled tasks
  const getTodaysCompletedTasks = () => {
    return getTodaysScheduledTasks().filter(task => task.status === 'completed');
  };

  // Convert backend intensity (0.15-0.85) to frontend percentage (0-100)
  const backendToFrontendIntensity = (backendIntensity) => {
    // Map 0.15-0.85 to 0-100
    const normalized = (backendIntensity - 0.15) / (0.85 - 0.15);
    return Math.round(normalized * 100);
  };

  // Convert frontend percentage (0-100) to backend intensity (0.15-0.85)
  const frontendToBackendIntensity = (frontendPercentage) => {
    // Map 0-100 to 0.15-0.85
    return 0.15 + (frontendPercentage / 100) * (0.85 - 0.15);
  };

  const handleIntensityChange = async (newIntensity) => {
    // Convert from 0-100 slider to 0.15-0.85 backend range
    const backendIntensity = frontendToBackendIntensity(newIntensity);
    
    setDashboardStats(prev => ({
      ...prev,
      userIntensity: newIntensity
    }));
    
    // Update intensity in backend
    try {
      await apiService.setIntensity(backendIntensity);
      console.log(`Intensity updated to ${backendIntensity.toFixed(2)} (${newIntensity}%)`);
      
      // Refresh the 14-day schedule with new intensity
      await fetch14DaySchedule();
      
      // Refresh dashboard stats to update Personal Score
      await fetchDashboardStats();
    } catch (error) {
      console.error('Error updating intensity:', error);
    }
  };

  const handleVoiceAgent = async () => {
    try {
      // Try to capture voice input
      const response = await apiService.captureVoiceInput();
      
      if (response.success) {
        alert(`Voice command processed: "${response.voice_text}"`);
        // Refresh assignments to show any changes
        fetchAssignments();
      } else {
        // Fallback to text input
        const command = prompt('Enter your voice command (e.g., "I finished my math homework"):');
        if (command) {
          await apiService.processVoiceCommand(command);
          alert('Voice command processed!');
          // Refresh assignments to show any changes
          fetchAssignments();
        }
      }
    } catch (error) {
      console.error('Error with voice agent:', error);
      // Fallback to text input
      const command = prompt('Voice not available. Enter your command (e.g., "I finished my math homework"):');
      if (command) {
        try {
          await apiService.processVoiceCommand(command);
          alert('Command processed!');
          // Refresh assignments to show any changes
          fetchAssignments();
        } catch (error) {
          console.error('Error processing command:', error);
          alert('Error processing command. Please try again.');
        }
      }
    }
  };

  const handleCanvasSync = async () => {
    try {
      console.log('🔄 Syncing Canvas tasks...');
      const response = await apiService.syncCanvasTasks();
      
      if (response.success) {
        console.log('✅ Canvas sync successful:', response);
        alert(`Canvas sync successful! Created ${response.tasks_created} tasks from Canvas assignments.`);
        
        // Refresh assignments, schedule, and dashboard stats
        await fetchAssignments();
        await fetch14DaySchedule();
        await fetchDashboardStats();
      } else {
        console.error('❌ Canvas sync failed:', response);
        alert(`Canvas sync failed: ${response.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('❌ Error syncing Canvas tasks:', error);
      alert(`Error syncing Canvas tasks: ${error.message}`);
    }
  };

  // Get performance bar color based on score with gradient transitions
  const getPerformanceBarColor = (score) => {
    if (score >= 67) {
      // High performance: Green gradient
      return `linear-gradient(90deg, #10b981 0%, #059669 100%)`;
    } else if (score >= 34) {
      // Medium performance: Yellow gradient
      return `linear-gradient(90deg, #f59e0b 0%, #d97706 100%)`;
    } else {
      // Low performance: Red gradient
      return `linear-gradient(90deg, #ef4444 0%, #dc2626 100%)`;
    }
  };

  // Get intensity bar color based on intensity level
  const getIntensityBarColor = (intensity) => {
    if (intensity >= 67) {
      // High intensity: Navy blue
      return '#1e40af';
    } else if (intensity >= 34) {
      // Medium intensity: Blue
      return '#3b82f6';
    } else {
      // Low intensity: Very light blue
      return '#93c5fd';
    }
  };

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      const response = await apiService.getTasks();
      
      if (response.success) {
        const allAssignments = response.tasks.map(task => apiService.convertBackendTaskToFrontend(task));
        const pending = allAssignments.filter(a => a.status !== 'completed');
        const completed = allAssignments.filter(a => a.status === 'completed');
        setAssignments(pending);
        setCompletedAssignments(completed);
      } else {
        throw new Error('Failed to fetch tasks');
      }
    } catch (error) {
      console.error('Error fetching assignments:', error);
      // Show empty state if backend is not available
      setAssignments([]);
      setCompletedAssignments([]);
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
      // Create task using API service
      const taskData = apiService.convertFrontendTaskToBackend({
        ...newAssignment,
        estimatedTime: estimatedTime,
        status: 'pending'
      });
      
      const response = await apiService.createTask(taskData);
      
      if (response.success) {
        // Convert backend task to frontend format and add to state
        const frontendTask = apiService.convertBackendTaskToFrontend(response.task);
        setAssignments([...assignments, frontendTask]);
        
        // Refresh 14-day schedule and dashboard stats since new task affects scheduling
        await fetch14DaySchedule();
        await fetchDashboardStats();
      } else {
        throw new Error('Failed to create task');
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
      alert('Failed to create assignment. Please try again.');
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
      } else {
        // Refresh 14-day schedule and dashboard stats since task deletion affects scheduling
        await fetch14DaySchedule();
        await fetchDashboardStats();
      }
    } catch (error) {
      console.error('Error deleting assignment:', error);
    }
  }, [fetch14DaySchedule, fetchDashboardStats]);

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
    // Find the assignment to get its name
    const assignment = completedAssignments.find(a => a.id === assignmentId);
    if (!assignment) return;

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
      await apiService.updateTask(assignment.name, {
        is_completed: false
      });
    } catch (error) {
      console.error('Error undoing completion:', error);
    }
  }, [completedAssignments]);


  const handleMarkComplete = useCallback(async (assignmentId) => {
    console.log('handleMarkComplete called:', { assignmentId });
    
    // Check if this is a schedule task
    if (assignmentId.startsWith('schedule_')) {
      console.log('Marking schedule task as complete:', assignmentId);
      
      // For schedule tasks, just update the progress to 100%
      setScheduleTaskProgress(prev => {
        console.log('Updating scheduleTaskProgress to 100 for:', assignmentId);
        return {
          ...prev,
          [assignmentId]: 100
        };
      });
      
      // Extract the actual task ID and update via API
      const taskId = assignmentId.replace('schedule_', '');
      try {
        console.log(`Calling API to mark task ${taskId} as complete (100%)`);
        await apiService.updateTaskProgress(parseInt(taskId), 100);
        console.log(`Schedule task ${taskId} marked as complete`);
        
        // Refresh the 14-day schedule
        console.log('Refreshing 14-day schedule after completion...');
        await fetch14DaySchedule();
        console.log('Schedule refreshed, new schedule data:', scheduleData);
        
        // Also refresh dashboard stats to update Personal Score
        console.log('Refreshing dashboard stats after completion...');
        await fetchDashboardStats();
      } catch (error) {
        console.error('Error updating schedule task:', error);
      }
    } else {
      // Find the assignment to get its name
      const assignment = assignments.find(a => a.id === assignmentId);
      if (!assignment) return;

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
        await apiService.updateTask(assignment.name, {
          completed_so_far: 100,
          is_completed: true
        });
        
        // Refresh dashboard stats to update Personal Score
        console.log('Refreshing dashboard stats after regular task completion...');
        await fetchDashboardStats();
      } catch (error) {
        console.error('Error updating assignment:', error);
      }
    }
  }, [assignments, fetch14DaySchedule, fetchDashboardStats]);

  const handleUpdateProgress = useCallback((assignmentId, newPercentage) => {
    console.log('handleUpdateProgress called:', { assignmentId, newPercentage });
    
    // Check if this is a schedule task
    if (assignmentId.startsWith('schedule_')) {
      // Update schedule task progress
      setScheduleTaskProgress(prev => {
        console.log('Updating schedule task progress:', { assignmentId, newPercentage });
        return {
          ...prev,
          [assignmentId]: newPercentage
        };
      });
    } else {
      // Update regular assignment progress
      setAssignments(prevAssignments => {
        console.log('Previous assignments:', prevAssignments.map(a => ({ id: a.id, completionPercentage: a.completionPercentage })));
        
        const updated = prevAssignments.map(a => 
          a.id === assignmentId ? { ...a, completionPercentage: newPercentage } : a
        );
        
        console.log('Updated assignments:', updated.map(a => ({ id: a.id, completionPercentage: a.completionPercentage })));
        return updated;
      });
    }
  }, []);

  // Debounced API call to prevent too many requests
  const debouncedApiCall = useCallback(
    (assignmentId, newPercentage) => {
      console.log('debouncedApiCall called:', { assignmentId, newPercentage });
      
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
        console.log('debouncedApiCall timeout executing:', { assignmentId, newPercentage });
        try {
          // Check if this is a schedule task (starts with 'schedule_')
          if (assignmentId.startsWith('schedule_')) {
            // Extract the actual task ID from the schedule ID
            const taskId = assignmentId.replace('schedule_', '');
            console.log(`Updating schedule task - assignmentId: ${assignmentId}, taskId: ${taskId}, parsed: ${parseInt(taskId)}`);
            
            // Call the API to update task progress
            console.log(`Calling API to update task ${taskId} to ${newPercentage}%`);
            try {
              const apiResult = await apiService.updateTaskProgress(parseInt(taskId), newPercentage);
              console.log(`API result for task ${taskId}:`, apiResult);
            } catch (apiError) {
              console.error(`API error for task ${taskId}:`, apiError);
              throw apiError; // Re-throw to be caught by outer try-catch
            }
            
            // Refresh the 14-day schedule to reflect the updated progress
            console.log('Refreshing 14-day schedule after progress update...');
            await fetch14DaySchedule();
            
            // Also refresh dashboard stats to update Personal Score
            console.log('Refreshing dashboard stats after progress update...');
            await fetchDashboardStats();
          } else {
            // Regular assignment update - find in assignments array
            const assignment = assignments.find(a => a.id === assignmentId);
            if (assignment) {
              await apiService.updateTask(assignment.name, {
                completed_so_far: newPercentage
              });
            }
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
    [assignments, fetch14DaySchedule, fetchDashboardStats]
  );

  const handleProgressChange = useCallback((assignmentId, newPercentage) => {
    console.log('🎯 handleProgressChange called:', { assignmentId, newPercentage });
    
    // Update local state immediately for smooth UI
    handleUpdateProgress(assignmentId, newPercentage);
    
    // If 100%, mark as complete
    if (newPercentage >= 100) {
      console.log('🎯 Progress is 100%, calling handleMarkComplete');
      handleMarkComplete(assignmentId);
    } else {
      console.log('🎯 Progress is not 100%, calling debouncedApiCall');
      // Debounced API call for progress update
      debouncedApiCall(assignmentId, newPercentage);
    }
    
    // Always refresh dashboard stats when progress changes
    console.log('🎯 Refreshing dashboard stats after progress change');
    fetchDashboardStats();
  }, [handleUpdateProgress, handleMarkComplete, fetchDashboardStats]);

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
      } else {
        // Refresh 14-day schedule and dashboard stats since task editing affects scheduling
        await fetch14DaySchedule();
        await fetchDashboardStats();
      }
    } catch (error) {
      console.error('Error updating assignment:', error);
    } finally {
      setEditingAssignment(null);
    }
  }, [fetch14DaySchedule, fetchDashboardStats]);

  const formatDate = (dateString) => {
    try {
      if (!dateString) return 'No date';
      
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }
      
      const month = date.toLocaleDateString('en-US', { month: 'short' });
      const day = date.getDate();
      return `${month} ${day}`;
    } catch (error) {
      console.warn('Error formatting date:', dateString, error);
      return 'Invalid date';
    }
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
    try {
      if (!dueDate) return false;
      
      const due = new Date(dueDate);
      if (isNaN(due.getTime())) {
        return false;
      }
      
      const now = new Date();
      return due < now && due.toDateString() !== now.toDateString();
    } catch (error) {
      console.warn('Error checking overdue status:', dueDate, error);
      return false;
    }
  };

  // Sort assignments by priority from very high to low
  const sortAssignmentsByPriority = (assignments) => {
    const priorityOrder = { 'very high': 4, 'high': 3, 'medium': 2, 'low': 1 };
    return [...assignments].sort((a, b) => {
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  };

  // Helper function to get ordinal suffix
  const getOrdinalSuffix = (num) => {
    const j = num % 10;
    const k = num % 100;
    if (j === 1 && k !== 11) return num + "st";
    if (j === 2 && k !== 12) return num + "nd";
    if (j === 3 && k !== 13) return num + "rd";
    return num + "th";
  };

  // Radial Progress Component (Semi-circle facing upwards)
  const RadialProgress = ({ percentage, label, color, icon, showBunny = false, bunnyImages = null, className = "", isPersonalScore = false, isHoursPercentile = false }) => {
    const radius = 80;
    const strokeWidth = 16;
    const normalizedRadius = radius - strokeWidth;
    const circumference = normalizedRadius * Math.PI; // Half circle circumference
    const strokeDasharray = `${circumference} ${circumference}`;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    return (
      <div className={`radial-progress-card ${className}`}>
        <div className="radial-progress-container">
          {icon && <div className="radial-progress-icon">{icon}</div>}
          <svg
            className="radial-progress-svg"
            width={radius * 2}
            height={radius + 20}
            viewBox={`0 0 ${radius * 2} ${radius + 20}`}
          >
            <path
              className="radial-progress-bg"
              stroke="#e2e8f0"
              fill="transparent"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              d={`M ${strokeWidth} ${radius} A ${normalizedRadius} ${normalizedRadius} 0 0 1 ${radius * 2 - strokeWidth} ${radius}`}
            />
            <path
              className="radial-progress-fill"
              stroke={color}
              fill="transparent"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              d={`M ${strokeWidth} ${radius} A ${normalizedRadius} ${normalizedRadius} 0 0 1 ${radius * 2 - strokeWidth} ${radius}`}
            />
          </svg>
          {showBunny && (
            <div className="radial-progress-image">
              <img 
                src={
                  bunnyImages ? (
                    percentage >= 66 ? bunnyImages.high : 
                    percentage >= 33 ? bunnyImages.medium : 
                    bunnyImages.low
                  ) : (
                    percentage >= 66 ? "/bunnyDone.png" : 
                    percentage >= 33 ? "/bunnyWorking.png" : 
                    "/bunnySleeping.png"
                  )
                }
                alt="Study Bunny" 
                className="bunny-icon"
              />
            </div>
          )}
          <div className="radial-progress-text">
            <div className="radial-progress-percentage">
              {isPersonalScore ? percentage : 
               isHoursPercentile ? getOrdinalSuffix(percentage) : 
               `${percentage}%`}
            </div>
            <div className="radial-progress-label">{label}</div>
          </div>
        </div>
      </div>
    );
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
    <div className="page" style={{'--running-progress': `url(${runningProgress})`}}>
      <div className="dashboard">
        <div className="radial-progress-section">
        <RadialProgress
          percentage={dashboardStats.workHoursPercentile}
          label="Hours Percentile"
          color={
            dashboardStats.workHoursPercentile >= 66 ? "#1e40af" : 
            dashboardStats.workHoursPercentile >= 33 ? "#3b82f6" : 
            "#93c5fd"
          }
          showBunny={true}
          bunnyImages={{
            low: "/bunnyDepressed.png",
            medium: "/bunnyThoughtless.png", 
            high: "/bunnyCool.png"
          }}
          className="hours-percentile"
          isHoursPercentile={true}
        />
        <RadialProgress
          percentage={Math.min(100, dashboardStats.assignmentCompletionPercent * 10)} // Scale: 10 tasks = 100%
          label={`Assignment Completion (${dashboardStats.assignmentCompletionPercent} tasks)`}
          color={
            dashboardStats.assignmentCompletionPercent >= 8 ? "#1e40af" : 
            dashboardStats.assignmentCompletionPercent >= 5 ? "#3b82f6" : 
            "#93c5fd"
          }
          showBunny={true}
          className="assignment-completion"
        />
        <RadialProgress
          percentage={dashboardStats.howAmIDoingScore}
          label="Personal Score"
          color={
            dashboardStats.howAmIDoingScore >= 66 ? "#1e40af" : 
            dashboardStats.howAmIDoingScore >= 33 ? "#3b82f6" : 
            "#93c5fd"
          }
          showBunny={true}
          bunnyImages={{
            low: "/bunnySad.png",
            medium: "/bunnyMid.png", 
            high: "/bunnyThrilled.png"
          }}
          className="personal-score"
          isPersonalScore={true}
        />
        </div>
        
        <div className="intensity-section">
          <div className="intensity-card-small">
            <div className="intensity-content">
              <div className="intensity-slider-container-small" style={{'--slider-value': dashboardStats.userIntensity}}>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={dashboardStats.userIntensity}
                  onChange={(e) => handleIntensityChange(parseInt(e.target.value))}
                  onMouseDown={() => {
                    const container = document.querySelector('.intensity-slider-container-small');
                    container?.classList.add('slider-moving');
                  }}
                  onMouseUp={() => {
                    const container = document.querySelector('.intensity-slider-container-small');
                    container?.classList.remove('slider-moving');
                  }}
                  onTouchStart={() => {
                    const container = document.querySelector('.intensity-slider-container-small');
                    container?.classList.add('slider-moving');
                  }}
                  onTouchEnd={() => {
                    const container = document.querySelector('.intensity-slider-container-small');
                    container?.classList.remove('slider-moving');
                  }}
                  className="intensity-slider-small"
                  style={{
                    backgroundImage: `linear-gradient(to right, ${getIntensityBarColor(dashboardStats.userIntensity)} ${dashboardStats.userIntensity}%, #e2e8f0 ${dashboardStats.userIntensity}%)`
                  }}
                />
                <div className="intensity-value-small">{dashboardStats.userIntensity}%</div>
              </div>
              <div className="intensity-label-small">Work Intensity</div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="assignments-section">
        <div className="section-header">
          <h2>Today's Tasks</h2>
          <div className="assignment-actions-header">
            <button 
              className="canvas-sync-btn circular-btn"
              onClick={handleCanvasSync}
              title="Sync Canvas Assignments - Import tasks from Canvas LMS"
            >
              🎨
            </button>
            <button 
              className="voice-ai-btn circular-btn"
              onClick={handleVoiceAgent}
              title="Voice AI Agent - Edit assignments with voice commands"
            >
              🎤
            </button>
            <button 
              className="btn btn-primary add-btn circular-btn"
              onClick={() => setShowAddForm(!showAddForm)}
              title="Add Assignment"
            >
              +
            </button>
          </div>
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
          <div className="loading">Loading today's schedule...</div>
        ) : (
          <div className="assignments-grid">
            {getTodaysPendingTasks().length === 0 ? (
              <div className="no-assignments">
                <p>No tasks scheduled for today. Check the calendar for your 14-day schedule!</p>
              </div>
            ) : (
              sortAssignmentsByPriority(getTodaysPendingTasks()).map(assignment => (
                <div key={assignment.id} className={`assignment-card ${assignment.color || 'green'}`} data-priority={assignment.priority}>
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
                    <div className="assignment-time" title="Allocated time from 14-day schedule">
                      {formatTimeLeft(assignment.estimatedTime)}
                      <span className="schedule-indicator"> 📅</span>
                    </div>
                  </div>
                  
                  <div className="progress-section">
                    <div className="progress-info">
                      <span className="current-progress">{assignment.completionPercentage}%</span>
                      {assignment.projectedPercentage && (
                        <span className="projected-progress">Target: {assignment.projectedPercentage}%</span>
                      )}
                    </div>
                    <div className="progress-slider-container">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={assignment.completionPercentage}
                        onChange={(e) => {
                          console.log('Slider onChange fired:', { assignmentId: assignment.id, value: e.target.value });
                          handleProgressChange(assignment.id, parseInt(e.target.value));
                        }}
                        onInput={(e) => {
                          console.log('Slider onInput fired:', { assignmentId: assignment.id, value: e.target.value });
                        }}
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
                      {assignment.projectedPercentage && (
                        <div className="projected-indicator" style={{left: `${assignment.projectedPercentage}%`}}>
                          <div className="projected-line"></div>
                        </div>
                      )}
                    </div>
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
          <h2>Today's Completed Tasks</h2>
        </div>

        {loading ? (
          <div className="loading">Loading today's completed tasks...</div>
        ) : (
          <div className="assignments-grid">
            {getTodaysCompletedTasks().length === 0 ? (
              <div className="no-assignments">
                <p>No completed tasks for today yet. Complete some tasks to see them here!</p>
              </div>
            ) : (
              sortAssignmentsByPriority(getTodaysCompletedTasks()).map(assignment => (
                <div key={assignment.id} className={`assignment-card completed-assignment ${assignment.color || 'green'}`} data-priority={assignment.priority}>
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
                    <div className="assignment-time" title="Allocated time from 14-day schedule">
                      {formatTimeLeft(assignment.estimatedTime)}
                      <span className="schedule-indicator"> 📅</span>
                    </div>
                  </div>
                  
                  <div className="progress-section">
                    <div className="progress-info">
                      <span className="current-progress">{assignment.completionPercentage}%</span>
                      {assignment.projectedPercentage && (
                        <span className="projected-progress">Target: {assignment.projectedPercentage}%</span>
                      )}
                    </div>
                    <div className="progress-slider-container">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={assignment.completionPercentage}
                        onChange={(e) => {
                          console.log('Slider onChange fired:', { assignmentId: assignment.id, value: e.target.value });
                          handleProgressChange(assignment.id, parseInt(e.target.value));
                        }}
                        onInput={(e) => {
                          console.log('Slider onInput fired:', { assignmentId: assignment.id, value: e.target.value });
                        }}
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
                      {assignment.projectedPercentage && (
                        <div className="projected-indicator" style={{left: `${assignment.projectedPercentage}%`}}>
                          <div className="projected-line"></div>
                        </div>
                      )}
                    </div>
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
